import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, RecoveryRequest } from '../../../../core/services/api.service';

export interface RecoveryOperation {
  id: string;
  type: string;
  status: string;
  progress?: number;
  start_time?: string;
  end_time?: string;
  reason?: string;
  severity?: string;
  details?: any;
  error?: string;
}

interface ActionDef {
  type: string;
  label: string;
  icon: string;
  desc: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  color: string;
}

@Component({
  selector: 'app-recovery-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recovery-dashboard.component.html',
  styleUrls: ['./recovery-dashboard.component.scss']
})
export class RecoveryDashboardComponent implements OnInit, OnDestroy {
  operations: RecoveryOperation[] = [];
  loading = true;
  refreshing = false;
  error: string | null = null;
  actionLoading: Record<string, boolean> = {};
  actionSuccess: string | null = null;
  expandedId: string | null = null;
  statusFilter: string = 'all';

  private refreshTimer: any;
  readonly refreshInterval = 30;
  countdown = 30;

  readonly actions: ActionDef[] = [
    { type: 'backup',  label: 'Backup',  icon: '💾', desc: 'Create a full snapshot of the primary database',            severity: 'low',      color: 'act-blue'   },
    { type: 'restore', label: 'Restore', icon: '🔄', desc: 'Restore database state from the latest backup',            severity: 'high',     color: 'act-amber'  },
    { type: 'repair',  label: 'Repair',  icon: '🔧', desc: 'Repair corrupted indexes and vacuum dead tuples',          severity: 'medium',   color: 'act-indigo' },
    { type: 'rebuild', label: 'Rebuild', icon: '🏗️', desc: 'Rebuild replica from primary (full re-sync)',             severity: 'critical', color: 'act-red'    },
  ];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.load();
    this.refreshTimer = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) { this.countdown = this.refreshInterval; this.silentRefresh(); }
    }, 1000);
  }

  ngOnDestroy(): void {
    if (this.refreshTimer) clearInterval(this.refreshTimer);
  }

  load(): void {
    this.loading = true;
    this.error = null;
    this.apiService.getRecoveryHistory().subscribe({
      next: (res) => {
        this.operations = Array.isArray(res) ? res : (res?.recoveries ?? []);
        this.loading = false;
      },
      error: () => { this.error = 'Unable to load recovery history'; this.loading = false; }
    });
  }

  silentRefresh(): void {
    this.refreshing = true;
    this.apiService.getRecoveryHistory().subscribe({
      next: (res) => { this.operations = Array.isArray(res) ? res : (res?.recoveries ?? []); this.refreshing = false; },
      error: () => { this.refreshing = false; }
    });
  }

  manualRefresh(): void { this.countdown = this.refreshInterval; this.load(); }

  startAction(type: string, severity: string): void {
    this.actionLoading[type] = true;
    this.actionSuccess = null;
    const request: RecoveryRequest = { type, reason: `Manual ${type} triggered from dashboard`, severity };
    this.apiService.startRecovery(request).subscribe({
      next: (res) => {
        this.actionLoading[type] = false;
        this.actionSuccess = type;
        setTimeout(() => { this.actionSuccess = null; }, 3000);
        this.silentRefresh();
      },
      error: () => { this.actionLoading[type] = false; this.error = `Failed to start ${type} operation`; }
    });
  }

  cancelOp(id: string): void {
    this.apiService.cancelRecovery(id).subscribe({
      next: () => this.silentRefresh(),
      error: () => { this.error = 'Failed to cancel operation'; }
    });
  }

  retryOp(op: RecoveryOperation): void {
    this.startAction(op.type, op.severity ?? 'medium');
  }

  toggleExpand(id: string): void {
    this.expandedId = this.expandedId === id ? null : id;
  }

  // ── Computed ────────────────────────────────────────────────────────────────
  get filtered(): RecoveryOperation[] {
    if (this.statusFilter === 'all') return this.operations;
    return this.operations.filter(o => o.status === this.statusFilter);
  }

  get total(): number     { return this.operations.length; }
  get successful(): number { return this.operations.filter(o => o.status === 'completed').length; }
  get failed(): number    { return this.operations.filter(o => o.status === 'failed').length; }
  get running(): number   { return this.operations.filter(o => o.status === 'running' || o.status === 'in_progress').length; }
  get successRate(): number {
    return this.total > 0 ? Math.round((this.successful / this.total) * 100) : 0;
  }

  // ── Helpers ─────────────────────────────────────────────────────────────────
  statusClass(s: string): string {
    switch ((s || '').toLowerCase()) {
      case 'completed':   return 'st-ok';
      case 'running':
      case 'in_progress': return 'st-run';
      case 'pending':     return 'st-pend';
      case 'failed':      return 'st-err';
      case 'cancelled':   return 'st-cancel';
      default:            return 'st-unknown';
    }
  }

  statusLabel(s: string): string {
    switch ((s || '').toLowerCase()) {
      case 'completed':   return '✓ Completed';
      case 'running':
      case 'in_progress': return '⟳ Running';
      case 'pending':     return '○ Pending';
      case 'failed':      return '✕ Failed';
      case 'cancelled':   return '— Cancelled';
      default:            return s;
    }
  }

  typeIcon(t: string): string {
    const a = this.actions.find(x => x.type === t);
    return a ? a.icon : '📋';
  }

  formatTs(ts: string | undefined): string {
    if (!ts) return '—';
    const d = new Date(ts);
    return isNaN(d.getTime()) ? ts : d.toLocaleString();
  }

  duration(op: RecoveryOperation): string {
    if (!op.start_time) return '—';
    const end = op.end_time ? new Date(op.end_time) : new Date();
    const secs = Math.round((end.getTime() - new Date(op.start_time).getTime()) / 1000);
    if (secs < 60) return `${secs}s`;
    return `${Math.floor(secs / 60)}m ${secs % 60}s`;
  }

  trackById(_: number, op: RecoveryOperation): string { return op.id; }
}
