import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule, DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, HealthResponse, MetricsResponse } from '../../../core/services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, DecimalPipe],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit, OnDestroy {
  // ── Data ────────────────────────────────────────────────────────────────────
  healthData: HealthResponse | null = null;
  metricsData: MetricsResponse | null = null;
  depsData: any = null;
  monitoringStatus: any = null;
  alertsData: any = null;
  recoveryHistory: any[] = [];

  // ── UI state ─────────────────────────────────────────────────────────────────
  loading = true;
  healthError: string | null = null;
  metricsError: string | null = null;
  loadTime: Date = new Date();

  // ── Auto-refresh ─────────────────────────────────────────────────────────────
  autoRefreshEnabled = true;
  countdown = 30;
  readonly refreshInterval = 30;

  private pendingCalls = 0;
  isFetching = false;
  private loadingTimeout: any = null;
  private countdownTimer: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadDashboardData();
    this.countdownTimer = setInterval(() => {
      if (!this.autoRefreshEnabled || this.isFetching) return;
      this.countdown--;
      if (this.countdown <= 0) {
        this.countdown = this.refreshInterval;
        this.loadDashboardData();
      }
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.loadingTimeout) clearTimeout(this.loadingTimeout);
    if (this.countdownTimer)  clearInterval(this.countdownTimer);
  }

  toggleAutoRefresh(): void {
    this.autoRefreshEnabled = !this.autoRefreshEnabled;
    if (this.autoRefreshEnabled) this.countdown = this.refreshInterval;
  }

  refreshData(): void {
    this.isFetching = false;
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    if (this.isFetching) return;
    this.isFetching = true;
    this.loading = this.healthData === null;
    this.healthError = null;
    this.metricsError = null;
    this.pendingCalls = 5;
    this.countdown = this.refreshInterval;

    if (this.loadingTimeout) clearTimeout(this.loadingTimeout);
    this.loadingTimeout = setTimeout(() => { if (this.loading) this.finishLoading(); }, 12000);

    this.apiService.getHealth().subscribe({
      next:  (h) => { this.healthData = h;      this.resolve(); },
      error: ()  => { this.healthError = 'Health check unavailable'; this.resolve(); }
    });

    this.apiService.getCurrentMetrics().subscribe({
      next:  (m) => { this.metricsData = m;     this.resolve(); },
      error: ()  => { this.metricsError = 'Metrics unavailable';    this.resolve(); }
    });

    this.apiService.getHealthDependencies().subscribe({
      next:  (d) => { this.depsData = d;         this.resolve(); },
      error: ()  =>                               this.resolve()
    });

    this.apiService.getMonitoringStatus().subscribe({
      next:  (s) => { this.monitoringStatus = s; this.resolve(); },
      error: ()  =>                               this.resolve()
    });

    this.apiService.getMonitoringAlerts().subscribe({
      next:  (a) => { this.alertsData = a;       this.resolve(); },
      error: ()  =>                               this.resolve()
    });
  }

  private resolve(): void {
    this.pendingCalls--;
    if (this.pendingCalls <= 0) this.finishLoading();
  }

  private finishLoading(): void {
    this.loading = false;
    this.isFetching = false;
    if (this.loadingTimeout) { clearTimeout(this.loadingTimeout); this.loadingTimeout = null; }
  }

  // ── System metrics ───────────────────────────────────────────────────────────
  getSystemMetrics(): any {
    const sys = this.metricsData?.current?.system as any;
    if (!sys) return null;
    const inner = sys.system ?? sys;
    return {
      cpu_usage:    inner.cpu?.percent    ?? inner.cpu_usage    ?? 0,
      memory_usage: inner.memory?.percent ?? inner.memory_usage ?? 0,
      disk_usage:   inner.disk?.percent   ?? inner.disk_usage   ?? 0,
    };
  }

  // ── Database metrics ─────────────────────────────────────────────────────────
  getDatabaseMetrics(): any {
    const db = this.metricsData?.current?.database as any;
    if (!db) return null;
    return {
      connections:  db.connections?.total  ?? db.connections ?? 0,
      active:       db.connections?.active ?? 0,
      idle:         db.connections?.idle   ?? 0,
      size_bytes:   db.database_size_bytes ?? null,
    };
  }

  getConnectionPct(): number {
    const db = this.getDatabaseMetrics();
    return db ? Math.min(Math.round((db.connections / 100) * 100), 100) : 0;
  }

  // ── Node helpers ─────────────────────────────────────────────────────────────
  getPrimaryNode(): any { return this.depsData?.postgresql_primary ?? null; }
  getReplicaNode(): any { return this.depsData?.postgresql_replica  ?? null; }

  // ── Monitoring helpers ───────────────────────────────────────────────────────
  isMonitoringActive(): boolean { return this.monitoringStatus?.is_monitoring === true; }
  getMonitoringInterval(): number { return this.monitoringStatus?.interval_seconds ?? 30; }

  // ── Alert helpers ────────────────────────────────────────────────────────────
  getActiveAlerts(): any[] { return this.alertsData?.system_alerts ?? []; }
  getAlertCount(): number  { return this.alertsData?.total_count ?? 0; }
  hasAlerts(): boolean     { return this.getAlertCount() > 0; }

  // ── Recovery helpers ─────────────────────────────────────────────────────────
  getRecoveryStatusClass(status: string): string {
    switch ((status || '').toLowerCase()) {
      case 'completed': return 'rc-completed';
      case 'failed':    return 'rc-failed';
      case 'in_progress':
      case 'pending':   return 'rc-running';
      default:          return 'rc-unknown';
    }
  }

  // ── Styling helpers ──────────────────────────────────────────────────────────
  getStatusClass(status: string): string {
    switch ((status || '').toLowerCase()) {
      case 'healthy':   return 'status-healthy';
      case 'warning':   return 'status-warning';
      case 'error':
      case 'unhealthy': return 'status-error';
      default:          return 'status-unknown';
    }
  }

  getUsageClass(value: number): string {
    if (value >= 90) return 'bar-danger';
    if (value >= 75) return 'bar-warning';
    return 'bar-healthy';
  }

  formatBytes(bytes: number): string {
    if (!bytes) return '0 B';
    if (bytes >= 1073741824) return `${(bytes / 1073741824).toFixed(1)} GB`;
    if (bytes >= 1048576)    return `${(bytes / 1048576).toFixed(1)} MB`;
    if (bytes >= 1024)       return `${(bytes / 1024).toFixed(1)} KB`;
    return `${bytes} B`;
  }
}
