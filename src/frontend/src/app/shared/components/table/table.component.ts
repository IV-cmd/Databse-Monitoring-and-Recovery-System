import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TableColumn, PaginationInfo, SortConfig, FilterConfig } from '../../types';
import { LoadingComponent } from '../loading/loading.component';

export interface TableConfig {
  columns: TableColumn[];
  data: any[];
  pagination?: PaginationInfo;
  sort?: SortConfig;
  filters?: FilterConfig[];
  loading?: boolean;
  emptyMessage?: string;
  selectable?: boolean;
  hoverable?: boolean;
  striped?: boolean;
  compact?: boolean;
}

@Component({
  selector: 'app-table',
  standalone: true,
  imports: [CommonModule, LoadingComponent],
  templateUrl: './table.component.html',
  styleUrls: ['./table.component.scss']
})
export class TableComponent {
  Math = Math; // Make Math available in template
  
  @Input() config: TableConfig = {
    columns: [],
    data: [],
    loading: false,
    emptyMessage: 'No data available'
  };

  @Output() sortChange = new EventEmitter<SortConfig>();
  @Output() filterChange = new EventEmitter<FilterConfig[]>();
  @Output() pageChange = new EventEmitter<number>();
  @Output() rowClick = new EventEmitter<any>();
  @Output() selectionChange = new EventEmitter<any[]>();

  selectedRows: any[] = [];
  allSelected: boolean = false;

  get isLoading(): boolean {
    return this.config.loading || false;
  }

  get isEmpty(): boolean {
    return !this.isLoading && (!this.config.data || this.config.data.length === 0);
  }

  get showPagination(): boolean {
    return !!this.config.pagination && this.config.pagination.totalPages > 1;
  }

  get tableClass(): string {
    const classes = ['table'];
    if (this.config.hoverable) classes.push('table-hover');
    if (this.config.striped) classes.push('table-striped');
    if (this.config.compact) classes.push('table-compact');
    return classes.join(' ');
  }

  onSort(column: TableColumn): void {
    if (!column.sortable) return;

    const currentSort = this.config.sort;
    let newDirection: 'asc' | 'desc' = 'asc';

    if (currentSort?.field === column.key) {
      newDirection = currentSort.direction === 'asc' ? 'desc' : 'asc';
    }

    this.sortChange.emit({
      field: column.key,
      direction: newDirection
    });
  }

  getSortIcon(column: TableColumn): string {
    if (!this.config.sort || this.config.sort.field !== column.key) {
      return '↕️';
    }
    return this.config.sort.direction === 'asc' ? '↑' : '↓';
  }

  onRowClick(row: any, event: MouseEvent): void {
    // Don't trigger row click if clicking on checkbox
    if (event.target instanceof HTMLInputElement) return;
    
    this.rowClick.emit(row);
  }

  onRowSelect(row: any, event: MouseEvent): void {
    event.stopPropagation();
    
    if (this.config.selectable) {
      const index = this.selectedRows.findIndex(r => r === row);
      if (index > -1) {
        this.selectedRows.splice(index, 1);
      } else {
        this.selectedRows.push(row);
      }
      this.selectionChange.emit(this.selectedRows);
      this.updateSelectAllState();
    }
  }

  onSelectAll(event: MouseEvent): void {
    event.stopPropagation();
    
    if (this.allSelected) {
      this.selectedRows = [];
    } else {
      this.selectedRows = [...this.config.data];
    }
    this.allSelected = !this.allSelected;
    this.selectionChange.emit(this.selectedRows);
  }

  updateSelectAllState(): void {
    this.allSelected = this.selectedRows.length === this.config.data?.length;
  }

  onPageClick(page: number | string): void {
    if (page === '...' || typeof page === 'string') {
      return; // Don't do anything for ellipsis pages
    }
    this.pageChange.emit(page as number);
  }

  getCellValue(row: any, column: TableColumn): string {
    const value = this.getNestedValue(row, column.key);
    return this.formatValue(value, column.type);
  }

  getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => current?.[key], obj);
  }

  formatValue(value: any, type?: string): string {
    if (value === null || value === undefined) return '';
    
    switch (type) {
      case 'date':
        return new Date(value).toLocaleDateString();
      case 'number':
        return typeof value === 'number' ? value.toLocaleString() : value;
      case 'boolean':
        return value ? 'Yes' : 'No';
      default:
        return String(value);
    }
  }

  isRowSelected(row: any): boolean {
    return this.selectedRows.includes(row);
  }

  trackByFn(index: number, item: any): any {
    return item.id || index;
  }

  getStartItem(): number {
    const page = this.config.pagination?.page || 1;
    const limit = this.config.pagination?.limit || 10;
    return (page - 1) * limit + 1;
  }

  getEndItem(): number {
    const page = this.config.pagination?.page || 1;
    const limit = this.config.pagination?.limit || 10;
    const total = this.config.pagination?.total || 0;
    return Math.min(page * limit, total);
  }

  getPreviousPage(): number {
    return Math.max(1, (this.config.pagination?.page || 1) - 1);
  }

  getNextPage(): number {
    const page = this.config.pagination?.page || 1;
    const totalPages = this.config.pagination?.totalPages || 1;
    return Math.min(totalPages, page + 1);
  }

  getPageNumbers() {
    const pagination = this.config.pagination;
    if (!pagination) return [];

    const pages: (number | string)[] = [];
    const { page, totalPages } = pagination;

    // Always show first page
    pages.push(1);

    // Show ellipsis if needed
    if (page > 3) {
      pages.push('...');
    }

    // Show pages around current page
    const start = Math.max(2, page - 1);
    const end = Math.min(totalPages - 1, page + 1);

    for (let i = start; i <= end; i++) {
      if (i !== 1 && i !== totalPages) {
        pages.push(i);
      }
    }

    // Show ellipsis if needed
    if (page < totalPages - 2) {
      pages.push('...');
    }

    // Always show last page
    if (totalPages > 1) {
      pages.push(totalPages);
    }

    return pages;
  }
}
