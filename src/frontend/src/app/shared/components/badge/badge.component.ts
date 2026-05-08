import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface BadgeConfig {
  text?: string;
  count?: number;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium' | 'large';
  variant?: 'solid' | 'outline' | 'pill';
  showDot?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  animated?: boolean;
  maxCount?: number;
}

@Component({
  selector: 'app-badge',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './badge.component.html',
  styleUrls: ['./badge.component.scss']
})
export class BadgeComponent {
  @Input() config: BadgeConfig = {};

  get badgeText(): string {
    if (this.config.showDot) return '';
    if (this.config.text) return this.config.text;
    if (this.config.count !== undefined) {
      const count = this.config.count;
      const maxCount = this.config.maxCount || 99;
      return count > maxCount ? `${maxCount}+` : count.toString();
    }
    return '';
  }

  get badgeClass(): string {
    const classes = ['badge'];
    
    // Color
    classes.push(`badge-${this.config.color || 'primary'}`);
    
    // Size
    classes.push(`badge-${this.config.size || 'medium'}`);
    
    // Variant
    classes.push(`badge-${this.config.variant || 'solid'}`);
    
    // Special states
    if (this.config.showDot) classes.push('badge-dot');
    if (this.config.animated) classes.push('badge-animated');
    
    return classes.join(' ');
  }

  get hasContent(): boolean {
    return !this.config.showDot && !!this.badgeText;
  }

  get isPositioned(): boolean {
    return !!this.config.position;
  }

  get positionClass(): string {
    if (!this.config.position) return '';
    return `badge-position-${this.config.position}`;
  }

  get showBadge(): boolean {
    if (this.config.showDot) return true;
    if (this.config.count !== undefined) return this.config.count > 0;
    if (this.config.text) return true;
    return false;
  }
}
