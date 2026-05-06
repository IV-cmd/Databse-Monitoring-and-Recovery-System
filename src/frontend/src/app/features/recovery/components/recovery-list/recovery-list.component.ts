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
  selector: 'app-recovery-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './recovery-list.component.html',
  styleUrls: ['./recovery-list.component.scss']
})
export class RecoveryListComponent {
  @Input() recoveryOperations: RecoveryOperation[] = [];
  @Input() loading: boolean = false;
  @Input() error: string | null = null;

  filterType = 'all';
  filterStatus = 'all';
  currentPage = 1;
  pageSize = 10;

  get filteredOperations(): RecoveryOperation[] {
    let filtered = this.recoveryOperations;

    if (this.filterType !== 'all') {
      filtered = filtered.filter(op => op.type === this.filterType);
    }

    if (this.filterStatus !== 'all') {
      filtered = filtered.filter(op => op.status === this.filterStatus);
    }

    return filtered;
  }

  get paginatedOperations(): RecoveryOperation[] {
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    return this.filteredOperations.slice(start, end);
  }

  get totalPages(): number {
    return Math.ceil(this.filteredOperations.length / this.pageSize);
  }

  onFilterChange(): void {
    this.currentPage = 1;
  }

  onPageChange(page: number): void {
    this.currentPage = page;
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

  trackByOperationId(index: number, operation: RecoveryOperation): string {
    return operation.id;
  }

  cancelOperation(operationId: string): void {
    console.log(`Canceling operation ${operationId}`);
  }

  viewOperationDetails(operationId: string): void {
    console.log(`Viewing details for operation ${operationId}`);
  }
}
