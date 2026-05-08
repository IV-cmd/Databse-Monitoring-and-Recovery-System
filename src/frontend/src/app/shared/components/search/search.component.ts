import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FilterConfig } from '../../types';

export interface SearchConfig {
  placeholder?: string;
  value?: string;
  filters?: FilterConfig[];
  showFilters?: boolean;
  showClear?: boolean;
  debounceTime?: number;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'outlined' | 'filled';
}

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent {
  @Input() config: SearchConfig = {};
  
  @Output() searchChange = new EventEmitter<string>();
  @Output() filterChange = new EventEmitter<FilterConfig[]>();
  @Output() clear = new EventEmitter<void>();

  searchValue: string = '';
  activeFilters: FilterConfig[] = [];
  showFilterPanel: boolean = false;

  ngOnInit(): void {
    this.searchValue = this.config.value || '';
    this.activeFilters = this.config.filters ? [...this.config.filters] : [];
  }

  get searchPlaceholder(): string {
    return this.config.placeholder || 'Search...';
  }

  get searchClass(): string {
    const classes = ['search'];
    
    // Size
    classes.push(`search-${this.config.size || 'medium'}`);
    
    // Variant
    classes.push(`search-${this.config.variant || 'default'}`);
    
    return classes.join(' ');
  }

  get showClearButton(): boolean {
    return this.config.showClear !== false && !!this.searchValue;
  }

  get hasActiveFilters(): boolean {
    return this.activeFilters.length > 0;
  }

  onSearchInput(): void {
    this.searchChange.emit(this.searchValue);
  }

  onClearSearch(): void {
    this.searchValue = '';
    this.searchChange.emit('');
    this.clear.emit();
  }

  onClearFilters(): void {
    this.activeFilters = [];
    this.filterChange.emit([]);
  }

  onClearAll(): void {
    this.onClearSearch();
    this.onClearFilters();
  }

  toggleFilterPanel(): void {
    this.showFilterPanel = !this.showFilterPanel;
  }

  onFilterChange(filter: FilterConfig, event: Event): void {
    const target = event.target as HTMLInputElement | HTMLSelectElement;
    const existingIndex = this.activeFilters.findIndex(f => f.field === filter.field);
    
    if (target.value) {
      const newFilter: FilterConfig = {
        ...filter,
        value: target.value
      };
      
      if (existingIndex > -1) {
        this.activeFilters[existingIndex] = newFilter;
      } else {
        this.activeFilters.push(newFilter);
      }
    } else if (existingIndex > -1) {
      this.activeFilters.splice(existingIndex, 1);
    }
    
    this.filterChange.emit([...this.activeFilters]);
  }

  getFilterValue(field: string): any {
    const filter = this.activeFilters.find(f => f.field === field);
    return filter?.value || '';
  }

  getFilterOptions(filter: FilterConfig): string[] {
    // This could be extended to accept options from config
    if (filter.field === 'severity') {
      return ['low', 'medium', 'high', 'critical'];
    }
    if (filter.field === 'status') {
      return ['active', 'inactive', 'pending', 'resolved'];
    }
    if (filter.field === 'type') {
      return ['cpu', 'memory', 'disk', 'network'];
    }
    return [];
  }

  isFilterActive(field: string): boolean {
    return this.activeFilters.some(f => f.field === field);
  }

  getActiveFilterCount(): number {
    return this.activeFilters.length;
  }

  removeFilter(filter: FilterConfig): void {
    const existingIndex = this.activeFilters.findIndex(f => f.field === filter.field);
    if (existingIndex > -1) {
      this.activeFilters.splice(existingIndex, 1);
      this.filterChange.emit([...this.activeFilters]);
    }
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      this.showFilterPanel = false;
    }
  }

  onClickOutside(): void {
    this.showFilterPanel = false;
  }
}
