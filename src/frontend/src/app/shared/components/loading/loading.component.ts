import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface LoadingConfig {
  message?: string;
  size?: 'small' | 'medium' | 'large';
  type?: 'spinner' | 'dots' | 'pulse';
  overlay?: boolean;
}

@Component({
  selector: 'app-loading',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './loading.component.html',
  styleUrls: ['./loading.component.scss']
})
export class LoadingComponent {
  @Input() config: LoadingConfig = {};

  get loadingMessage(): string {
    return this.config.message || 'Loading...';
  }

  get loadingSize(): string {
    return this.config.size || 'medium';
  }

  get loadingType(): string {
    return this.config.type || 'spinner';
  }

  get isOverlay(): boolean {
    return this.config.overlay !== false;
  }

  get sizeClass(): string {
    switch (this.loadingSize) {
      case 'small':
        return 'loading-small';
      case 'large':
        return 'loading-large';
      default:
        return 'loading-medium';
    }
  }

  get typeClass(): string {
    switch (this.loadingType) {
      case 'dots':
        return 'loading-dots';
      case 'pulse':
        return 'loading-pulse';
      default:
        return 'loading-spinner';
    }
  }
}
