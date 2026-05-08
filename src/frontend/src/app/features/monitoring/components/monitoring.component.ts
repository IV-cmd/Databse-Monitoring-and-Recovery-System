import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';
import { AlertsPanelComponent } from './alerts-panel/alerts-panel.component';

export interface MonitoringData {
  status: string;
  metrics: any;
  timestamp: string;
}

export interface Alert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  source?: string;
}

@Component({
  selector: 'app-monitoring',
  standalone: true,
  imports: [CommonModule, AlertsPanelComponent],
  templateUrl: './monitoring.component.html',
  styleUrls: ['./monitoring.component.scss']
})
export class MonitoringComponent implements OnInit {
  monitoringData: MonitoringData | null = null;
  alerts: Alert[] = [];
  loading = true;
  error: string | null = null;
  metricsData: any = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadMonitoringData();
  }

  loadMonitoringData(): void {
    this.loading = true;
    this.error = null;

    this.apiService.getMonitoringStatus().subscribe({
      next: (data) => {
        this.monitoringData = data;
        this.metricsData = data.metrics;
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Failed to load monitoring data';
        this.loading = false;
      }
    });

    this.apiService.getMonitoringAlerts().subscribe({
      next: (alerts: Alert[]) => {
        this.alerts = alerts;
      },
      error: (err: any) => {
        console.error('Failed to load alerts:', err);
      }
    });
  }

  refreshData(): void {
    this.loadMonitoringData();
  }
}
