import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, DatePipe],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit, OnDestroy {
  systemStatus: string = 'unknown';
  statusVersion: string = '';
  now: Date = new Date();
  readonly env: string = this.detectEnv();

  private clockTimer: any = null;
  private pollTimer: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.fetchHealth();
    this.clockTimer = setInterval(() => { this.now = new Date(); }, 1000);
    this.pollTimer  = setInterval(() => { this.fetchHealth(); }, 30000);
  }

  ngOnDestroy(): void {
    if (this.clockTimer) clearInterval(this.clockTimer);
    if (this.pollTimer)  clearInterval(this.pollTimer);
  }

  private fetchHealth(): void {
    this.apiService.getHealth().subscribe({
      next:  (h: any) => { this.systemStatus = h?.status ?? 'unknown'; this.statusVersion = h?.version ?? ''; },
      error: ()       => { this.systemStatus = 'unreachable'; }
    });
  }

  private detectEnv(): string {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') return 'LOCAL';
    if (host.includes('staging') || host.includes('stage')) return 'STAGING';
    return 'PRODUCTION';
  }

  getStatusLabel(): string {
    switch (this.systemStatus.toLowerCase()) {
      case 'healthy':     return 'All Systems Operational';
      case 'warning':     return 'Degraded Performance';
      case 'unhealthy':
      case 'error':       return 'System Degraded';
      case 'unreachable': return 'Backend Unreachable';
      default:            return 'Checking…';
    }
  }

  getStatusClass(): string {
    switch (this.systemStatus.toLowerCase()) {
      case 'healthy':     return 'status-ok';
      case 'warning':     return 'status-warn';
      case 'unhealthy':
      case 'error':
      case 'unreachable': return 'status-err';
      default:            return 'status-unknown';
    }
  }
}
