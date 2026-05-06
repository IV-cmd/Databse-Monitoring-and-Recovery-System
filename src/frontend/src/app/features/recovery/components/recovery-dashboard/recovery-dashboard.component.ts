import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { ApiService, RecoveryRequest } from '../../../../core/services/api.service';

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

export interface RecoveryStats {
  totalOperations: number;
  successfulOperations: number;
  failedOperations: number;
  pendingOperations: number;
  runningOperations: number;
  lastBackup?: Date;
  lastRestore?: Date;
}

@Component({
  selector: 'app-recovery-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './recovery-dashboard.component.html',
  styleUrls: ['./recovery-dashboard.component.scss']
})
export class RecoveryDashboardComponent implements OnInit {
  recoveryOperations: RecoveryOperation[] = [];
  recoveryStats: RecoveryStats | null = null;
  loading = true;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.loadRecoveryData();
  }

  loadRecoveryData(): void {
    this.loading = true;
    this.error = null;

    // Load recovery history from backend
    this.apiService.getRecoveryHistory().subscribe({
      next: (history) => {
        this.recoveryOperations = history;
        // Calculate stats from operations
        this.calculateStats();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load recovery data';
        this.loading = false;
      }
    });
  }

  private calculateStats(): void {
    const total = this.recoveryOperations.length;
    const successful = this.recoveryOperations.filter(op => op.status === 'completed').length;
    const failed = this.recoveryOperations.filter(op => op.status === 'failed').length;
    const pending = this.recoveryOperations.filter(op => op.status === 'pending').length;
    const running = this.recoveryOperations.filter(op => op.status === 'running').length;

    const completedOperations = this.recoveryOperations.filter(op => op.status === 'completed');
    const lastBackup = completedOperations
      .filter(op => op.type === 'backup')
      .sort((a, b) => new Date(b.endTime!).getTime() - new Date(a.endTime!).getTime())[0];
    const lastRestore = completedOperations
      .filter(op => op.type === 'restore')
      .sort((a, b) => new Date(b.endTime!).getTime() - new Date(a.endTime!).getTime())[0];

    this.recoveryStats = {
      totalOperations: total,
      successfulOperations: successful,
      failedOperations: failed,
      pendingOperations: pending,
      runningOperations: running,
      lastBackup: lastBackup?.endTime,
      lastRestore: lastRestore?.endTime
    };
  }

  refreshData(): void {
    this.loadRecoveryData();
  }

  startNewRecovery(type: string): void {
    const request: RecoveryRequest = {
      type: type,
      reason: `Starting ${type} operation from dashboard`,
      severity: 'medium'
    };

    this.apiService.startRecovery(request).subscribe({
      next: () => {
        this.loadRecoveryData(); // Refresh data after starting
      },
      error: () => {
        this.error = `Failed to start ${type} operation`;
      }
    });
  }

  cancelOperation(operationId: string): void {
    this.apiService.cancelRecovery(operationId).subscribe({
      next: () => {
        this.loadRecoveryData(); // Refresh data after canceling
      },
      error: () => {
        this.error = 'Failed to cancel operation';
      }
    });
  }

  retryOperation(operationId: string): void {
    const operation = this.recoveryOperations.find(op => op.id === operationId);
    if (operation) {
      const request: RecoveryRequest = {
        type: operation.type,
        reason: `Retrying ${operation.type} operation`,
        severity: 'medium'
      };
      
      this.apiService.startRecovery(request).subscribe({
        next: () => {
          this.loadRecoveryData(); // Refresh data after retrying
        },
        error: () => {
          this.error = 'Failed to retry operation';
        }
      });
    }
  }

  viewOperationDetails(operationId: string): void {
    console.log(`Viewing details for operation ${operationId}`);
    // TODO: Navigate to operation details page or open modal
  }

  getStatusClass(status: string): string {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'status-completed';
      case 'running':
        return 'status-running';
      case 'pending':
        return 'status-pending';
      case 'failed':
        return 'status-failed';
      default:
        return 'status-unknown';
    }
  }

  getTypeIcon(type: string): string {
    switch (type.toLowerCase()) {
      case 'backup':
        return '💾';
      case 'restore':
        return '🔄';
      case 'repair':
        return '🔧';
      case 'rebuild':
        return '🏗️';
      default:
        return '📋';
    }
  }

  formatDate(date: Date): string {
    return date.toLocaleString();
  }

  getProgressColor(progress: number): string {
    if (progress >= 80) return '#4caf50';
    if (progress >= 50) return '#ff9800';
    return '#f44336';
  }

  trackByOperationId(index: number, operation: RecoveryOperation): string {
    return operation.id;
  }
}
