import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Alert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  source?: string;
}

@Component({
  selector: 'app-alerts-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts-panel.component.html',
  styleUrls: ['./alerts-panel.component.scss']
})
export class AlertsPanelComponent {
  @Input() alerts: Alert[] = [];
  @Input() maxAlerts: number = 10;
  @Input() showFilters: boolean = true;

  getSeverityClass(severity: string): string {
    switch (severity) {
      case 'low':
        return 'severity-low';
      case 'medium':
        return 'severity-medium';
      case 'high':
        return 'severity-high';
      case 'critical':
        return 'severity-critical';
      default:
        return 'severity-unknown';
    }
  }

  getSeverityIcon(severity: string): string {
    switch (severity) {
      case 'low':
        return 'info';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      case 'critical':
        return 'danger';
      default:
        return 'help';
    }
  }

  dismissAlert(alertId: string): void {
    this.alerts = this.alerts.filter(alert => alert.id !== alertId);
  }

  clearAllAlerts(): void {
    this.alerts = [];
  }

  getFilteredAlerts(): Alert[] {
    return this.alerts.slice(0, this.maxAlerts);
  }

  getAlertCountBySeverity(severity: string): number {
    return this.alerts.filter(alert => alert.severity === severity).length;
  }
}
