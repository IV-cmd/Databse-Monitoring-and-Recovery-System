import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-monitoring',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './monitoring.component.html',
  styleUrls: ['./monitoring.component.scss']
})
export class MonitoringComponent implements OnInit, OnDestroy {
  // ── Data ──────────────────────────────────────────────────────────────────
  monitoringStatus: any = null;
  alertsData: any = null;
  depsData: any = null;

  // ── UI state ──────────────────────────────────────────────────────────────
  loading = true;
  isFetching = false;
  countdown = 30;
  readonly refreshInterval = 30;
  autoRefreshEnabled = true;
  expandedQueries = false;
  copiedExpr: string | null = null;

  private pending = 0;
  private countdownTimer: any = null;
  private loadingTimeout: any = null;

  // ── Observability stack ────────────────────────────────────────────────────
  readonly stack = [
    {
      id: 'prometheus', name: 'Prometheus', icon: '&#128200;',
      desc: 'Metrics collection & alerting',
      openUrl: 'http://localhost:9090/graph', depKey: 'prometheus',
      queries: [
        { label: 'DB connections',  expr: 'pg_stat_database_numbackends{datname="monitoring_db"}' },
        { label: 'DB size',         expr: 'pg_database_size_bytes{datname="monitoring_db"}' },
        { label: 'Query rate (5m)', expr: 'rate(pg_stat_database_xact_commit{datname="monitoring_db"}[5m])' },
        { label: 'Cache hit ratio', expr: 'pg_stat_database_blks_hit{datname="monitoring_db"} / (pg_stat_database_blks_hit{datname="monitoring_db"} + pg_stat_database_blks_read{datname="monitoring_db"} + 1)' },
      ],
    },
    {
      id: 'grafana', name: 'Grafana', icon: '&#128202;',
      desc: 'Metrics visualisation & dashboards',
      openUrl: 'http://localhost:3000/d/postgres-db', depKey: 'grafana',
      queries: null,
    },
    {
      id: 'kibana', name: 'ELK / Kibana', icon: '&#128269;',
      desc: 'Log aggregation & full-text search',
      openUrl: 'http://localhost:5602', depKey: 'kibana',
      queries: null,
    },
  ];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.load();
    this.countdownTimer = setInterval(() => {
      if (!this.autoRefreshEnabled || this.isFetching) return;
      this.countdown--;
      if (this.countdown <= 0) { this.countdown = this.refreshInterval; this.load(); }
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.countdownTimer)  clearInterval(this.countdownTimer);
    if (this.loadingTimeout)  clearTimeout(this.loadingTimeout);
  }

  toggleAutoRefresh(): void {
    this.autoRefreshEnabled = !this.autoRefreshEnabled;
    if (this.autoRefreshEnabled) this.countdown = this.refreshInterval;
  }

  refreshData(): void { this.isFetching = false; this.load(); }

  load(): void {
    if (this.isFetching) return;
    this.isFetching = true;
    this.loading = this.monitoringStatus === null;
    this.pending = 3;
    this.countdown = this.refreshInterval;
    if (this.loadingTimeout) clearTimeout(this.loadingTimeout);
    this.loadingTimeout = setTimeout(() => { if (this.loading) this.done(); }, 12000);
    this.apiService.getMonitoringStatus().subscribe({ next: (d) => { this.monitoringStatus = d; this.resolve(); }, error: () => this.resolve() });
    this.apiService.getMonitoringAlerts().subscribe({ next: (d) => { this.alertsData = d; this.resolve(); }, error: () => this.resolve() });
    this.apiService.getHealthDependencies().subscribe({ next: (d) => { this.depsData = d; this.resolve(); }, error: () => this.resolve() });
  }

  private resolve(): void { this.pending--; if (this.pending <= 0) this.done(); }
  private done(): void {
    this.loading = false; this.isFetching = false;
    if (this.loadingTimeout) { clearTimeout(this.loadingTimeout); this.loadingTimeout = null; }
  }

  // ── Data helpers ──────────────────────────────────────────────────────────
  getSys(): any {
    const s = this.monitoringStatus?.metrics?.system?.system;
    if (!s) return null;
    return {
      cpu:        s.cpu?.percent    ?? 0,
      cores:      s.cpu?.count      ?? 0,
      mem:        s.memory?.percent ?? 0,
      memTotalGB: s.memory?.total   ? (s.memory.total / 1073741824).toFixed(1) : null,
      disk:       s.disk?.percent   ?? 0,
      diskUsedGB: s.disk?.used      ? (s.disk.used / 1073741824).toFixed(1) : null,
      netSent:    s.network?.bytes_sent ?? 0,
      netRecv:    s.network?.bytes_recv ?? 0,
    };
  }

  getDB(): any {
    const d = this.monitoringStatus?.metrics?.database;
    if (!d) return null;
    const total = d.connections?.total ?? 0;
    return {
      status:    d.status ?? 'unknown',
      total,
      active:    d.connections?.active ?? 0,
      idle:      d.connections?.idle   ?? 0,
      maxConn:   100,
      sizeBytes: d.database_size_bytes ?? null,
    };
  }

  getConnectedStackCount(): number {
    return this.stack.filter(t => this.getStackStatus(t.depKey) === 'healthy').length;
  }

  getHealthScore(): { label: string; cls: string; score: number } {
    const db = this.getDB();
    const sys = this.getSys();
    if (!db) return { label: 'Unknown', cls: 'hs-unknown', score: 0 };
    let score = 100;
    if (db.status !== 'healthy') score -= 30;
    if (sys) {
      if (sys.cpu  >= 90) score -= 20; else if (sys.cpu  >= 75) score -= 10;
      if (sys.mem  >= 90) score -= 15; else if (sys.mem  >= 85) score -= 7;
      if (sys.disk >= 90) score -= 15; else if (sys.disk >= 85) score -= 7;
    }
    score = Math.max(0, score);
    if (score >= 90) return { label: 'Healthy',  cls: 'hs-ok',   score };
    if (score >= 70) return { label: 'Degraded', cls: 'hs-warn', score };
    return               { label: 'Critical',  cls: 'hs-err',  score };
  }

  async copyToClipboard(expr: string): Promise<void> {
    try {
      await navigator.clipboard.writeText(expr);
      this.copiedExpr = expr;
      setTimeout(() => { this.copiedExpr = null; }, 2000);
    } catch { /* clipboard unavailable */ }
  }

  // ── Stack helpers ─────────────────────────────────────────────────────────
  getStackStatus(depKey: string | null): string {
    if (!depKey) return 'not_configured';
    return this.depsData?.[depKey]?.status ?? 'not_configured';
  }

  // ── Style helpers ─────────────────────────────────────────────────────────
  getUsageClass(v: number): string {
    return v >= 90 ? 'bar-danger' : v >= 75 ? 'bar-warning' : 'bar-ok';
  }

  getGaugeClass(v: number, warnAt = 75, critAt = 90): string {
    return v >= critAt ? 'g-danger' : v >= warnAt ? 'g-warn' : 'g-ok';
  }

  getStatusClass(s: string): string {
    switch ((s || '').toLowerCase()) {
      case 'healthy':   return 'st-ok';
      case 'warning':   return 'st-warn';
      case 'unhealthy':
      case 'error':     return 'st-err';
      default:          return 'st-unknown';
    }
  }

  encodeURIComponent = encodeURIComponent;

  formatBytes(b: number): string {
    if (!b) return '—';
    if (b >= 1073741824) return (b / 1073741824).toFixed(1) + ' GB';
    if (b >= 1048576)    return (b / 1048576).toFixed(1)    + ' MB';
    return (b / 1024).toFixed(1) + ' KB';
  }

  formatNetBytes(b: number): string {
    if (!b) return '0 B';
    if (b >= 1073741824) return (b / 1073741824).toFixed(2) + ' GB';
    if (b >= 1048576)    return (b / 1048576).toFixed(1)    + ' MB';
    return (b / 1024).toFixed(1) + ' KB';
  }
}
