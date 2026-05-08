import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoadingComponent } from '../loading/loading.component';

export interface CardConfig {
  title?: string;
  subtitle?: string;
  content?: string;
  footer?: string;
  image?: string;
  variant?: 'default' | 'outlined' | 'elevated' | 'flat';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  clickable?: boolean;
  dismissible?: boolean;
  loading?: boolean;
  icon?: string;
  badge?: string | number;
  actions?: Array<{
    label: string;
    action: string;
    type?: 'primary' | 'secondary' | 'danger';
  }>;
}

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule, LoadingComponent],
  templateUrl: './card.component.html',
  styleUrls: ['./card.component.scss']
})
export class CardComponent {
  @Input() config: CardConfig = {};

  @Output() cardClick = new EventEmitter<void>();
  @Output() actionClick = new EventEmitter<string>();
  @Output() dismiss = new EventEmitter<void>();

  get cardClass(): string {
    const classes = ['card'];
    
    // Variant
    classes.push(`card-${this.config.variant || 'default'}`);
    
    // Size
    classes.push(`card-${this.config.size || 'medium'}`);
    
    // Color
    if (this.config.color) {
      classes.push(`card-${this.config.color}`);
    }
    
    // Interactive
    if (this.config.clickable) {
      classes.push('card-clickable');
    }
    
    // Loading
    if (this.config.loading) {
      classes.push('card-loading');
    }
    
    return classes.join(' ');
  }

  get hasHeader(): boolean {
    return !!(this.config.title || this.config.subtitle || this.config.icon || this.config.dismissible);
  }

  get hasFooter(): boolean {
    return !!(this.config.footer || this.config.actions);
  }

  get hasImage(): boolean {
    return !!this.config.image;
  }

  onCardClick(): void {
    if (this.config.clickable) {
      this.cardClick.emit();
    }
  }

  onActionClick(action: string, event: MouseEvent): void {
    event.stopPropagation();
    this.actionClick.emit(action);
  }

  onDismiss(event: MouseEvent): void {
    event.stopPropagation();
    this.dismiss.emit();
  }

  getActionClass(type?: string): string {
    const baseClass = 'card-action';
    return type ? `${baseClass} ${baseClass}-${type}` : baseClass;
  }

  getBadgeClass(): string {
    return 'card-badge';
  }
}
