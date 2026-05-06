import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type StatusType = 'healthy' | 'warning' | 'error' | 'unknown' | 'loading';
export type StatusSize = 'small' | 'medium' | 'large';

@Component({
  selector: 'app-status-indicator',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './status-indicator.component.html',
  styleUrls: ['./status-indicator.component.scss']
})
export class StatusIndicatorComponent {
  @Input() status: StatusType = 'unknown';
  @Input() label: string = '';
  @Input() size: StatusSize = 'medium';
  @Input() showIcon: boolean = true;
  @Input() showLabel: boolean = true;
  @Input() animated: boolean = true;

  getStatusClass(): string {
    return `status-${this.status} size-${this.size}`;
  }

  getStatusIcon(): string {
    switch (this.status) {
      case 'healthy':
        return 'check_circle';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      case 'loading':
        return 'hourglass_empty';
      default:
        return 'help';
    }
  }

  getStatusText(): string {
    switch (this.status) {
      case 'healthy':
        return 'Healthy';
      case 'warning':
        return 'Warning';
      case 'error':
        return 'Error';
      case 'loading':
        return 'Loading';
      default:
        return 'Unknown';
    }
  }

  isHealthy(): boolean {
    return this.status === 'healthy';
  }

  isWarning(): boolean {
    return this.status === 'warning';
  }

  isError(): boolean {
    return this.status === 'error';
  }

  isLoading(): boolean {
    return this.status === 'loading';
  }

  getAriaLabel(): string {
    return `${this.label || this.getStatusText()}: ${this.getStatusText()}`;
  }
}
