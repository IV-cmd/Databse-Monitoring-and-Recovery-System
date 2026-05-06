import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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
  selector: 'app-recovery-history',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './recovery-history.component.html',
  styleUrls: ['./recovery-history.component.scss']
})
export class RecoveryHistoryComponent {
  @Input() recoveryOperations: RecoveryOperation[] = [];
  @Input() loading: boolean = false;
  @Input() error: string | null = null;

  dateRange = '30';
  selectedType = 'all';

  get filteredOperations(): RecoveryOperation[] {
    let filtered = this.recoveryOperations;

    if (this.dateRange !== 'all') {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - parseInt(this.dateRange));
      filtered = filtered.filter(op => new Date(op.startTime) >= cutoffDate);
    }

    if (this.selectedType !== 'all') {
      filtered = filtered.filter(op => op.type === this.selectedType);
    }

    return filtered;
  }

  get totalOperations(): number {
    return this.filteredOperations.length;
  }

  get successRate(): number {
    const total = this.filteredOperations.length;
    const completed = this.filteredOperations.filter(op => op.status === 'completed').length;
    return total > 0 ? (completed / total) * 100 : 0;
  }

  get operationsByType(): { [key: string]: number } {
    return this.filteredOperations.reduce((acc, op) => {
      acc[op.type] = (acc[op.type] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });
  }

  get operationsByStatus(): { [key: string]: number } {
    return this.filteredOperations.reduce((acc, op) => {
      acc[op.status] = (acc[op.status] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });
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
    return date.toLocaleDateString();
  }
}
