import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, HealthResponse, MetricsResponse } from '../../../core/services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  healthData: HealthResponse | null = null;
  metricsData: MetricsResponse | null = null;
  loading = true;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    this.loading = true;
    this.error = null;

    // Load health and metrics data in parallel
    this.apiService.getHealth().subscribe({
      next: (health) => {
        this.healthData = health;
        this.checkLoadingComplete();
      },
      error: (err) => {
        this.error = 'Failed to load health data';
        this.loading = false;
      }
    });

    this.apiService.getCurrentMetrics().subscribe({
      next: (metrics) => {
        this.metricsData = metrics;
        this.checkLoadingComplete();
      },
      error: (err) => {
        this.error = 'Failed to load metrics data';
        this.loading = false;
      }
    });
  }

  private checkLoadingComplete(): void {
    if (this.healthData && this.metricsData) {
      this.loading = false;
    }
  }

  refreshData(): void {
    this.loadDashboardData();
  }

  getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'status-healthy';
      case 'warning':
        return 'status-warning';
      case 'error':
      case 'unhealthy':
        return 'status-error';
      default:
        return 'status-unknown';
    }
  }

  getDatabaseMetrics(): any {
    return this.metricsData?.current?.database;
  }

  getSystemMetrics(): any {
    return this.metricsData?.current?.system;
  }

  formatMetricValue(value: number): string {
    if (value >= 90) return `${value}%`;
    if (value >= 75) return `${value}%`;
    return `${value}%`;
  }
}
