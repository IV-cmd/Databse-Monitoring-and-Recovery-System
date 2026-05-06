import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../../core/services/api.service';

export interface RecoveryOperation {
  id: string;
  type: 'backup' | 'restore' | 'repair' | 'rebuild';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime: Date;
  endTime?: Date;
  errorMessage?: string;
  details?: string;
}

@Component({
  selector: 'app-recovery-status',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recovery-status.component.html',
  styleUrls: ['./recovery-status.component.scss']
})
export class RecoveryStatusComponent implements OnInit {
  @Input() operationId: string = '';
  
  operation: RecoveryOperation | null = null;
  loading = true;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    if (this.operationId) {
      this.loadOperationStatus();
    }
  }

  loadOperationStatus(): void {
    this.loading = true;
    this.error = null;

    this.apiService.getRecoveryStatus(this.operationId).subscribe({
      next: (operation) => {
        this.operation = operation;
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load operation status';
        this.loading = false;
      }
    });
  }

  getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed': return 'status-completed';
      case 'running': return 'status-running';
      case 'pending': return 'status-pending';
      case 'failed': return 'status-failed';
      default: return 'status-unknown';
    }
  }

  getTypeIcon(type: string): string {
    switch (type.toLowerCase()) {
      case 'backup': return '💾';
      case 'restore': return '🔄';
      case 'repair': return '🔧';
      case 'rebuild': return '🏗️';
      default: return '📋';
    }
  }

  formatDate(date: Date): string {
    return date.toLocaleString();
  }

  getDuration(): string {
    if (!this.operation) return 'N/A';
    
    const start = new Date(this.operation.startTime);
    const end = this.operation.endTime ? new Date(this.operation.endTime) : new Date();
    const duration = end.getTime() - start.getTime();
    
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((duration % (1000 * 60)) / 1000);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  }

  getProgressColor(progress: number): string {
    if (progress >= 80) return '#4caf50';
    if (progress >= 50) return '#ff9800';
    return '#f44336';
  }

  cancelOperation(): void {
    if (this.operation) {
      this.apiService.cancelRecovery(this.operation.id).subscribe({
        next: () => {
          this.loadOperationStatus();
        },
        error: () => {
          this.error = 'Failed to cancel operation';
        }
      });
    }
  }

  refreshStatus(): void {
    this.loadOperationStatus();
  }
}
