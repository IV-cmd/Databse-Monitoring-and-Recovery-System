import { Component, Input, Output, EventEmitter, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ToastConfig {
  id?: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  title?: string;
  duration?: number;
  showClose?: boolean;
  showIcon?: boolean;
  showProgress?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  actions?: Array<{
    label: string;
    action: string;
    type?: 'primary' | 'secondary';
  }>;
}

@Component({
  selector: 'app-toast',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './toast.component.html',
  styleUrls: ['./toast.component.scss']
})
export class ToastComponent implements OnInit, OnDestroy {
  @Input() config!: ToastConfig;
  @Output() close = new EventEmitter<string>();
  @Output() action = new EventEmitter<{ action: string; toastId: string }>();

  private timeoutId: any;
  private progressInterval: any;
  public progress: number = 0;
  public isVisible: boolean = false;

  ngOnInit(): void {
    this.isVisible = true;
    this.startAutoClose();
    if (this.config.showProgress) {
      this.startProgress();
    }
  }

  ngOnDestroy(): void {
    this.clearTimeouts();
  }

  get toastClass(): string {
    const classes = ['toast'];
    classes.push(`toast-${this.config.type}`);
    classes.push(`toast-${this.config.position || 'top-right'}`);
    return classes.join(' ');
  }

  get icon(): string {
    switch (this.config.type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return 'ℹ️';
    }
  }

  get hasTitle(): boolean {
    return !!this.config.title;
  }

  get hasActions(): boolean {
    return !!(this.config.actions && this.config.actions.length > 0);
  }

  get showCloseButton(): boolean {
    return this.config.showClose !== false;
  }

  get showIcon(): boolean {
    return this.config.showIcon !== false;
  }

  get showProgressBar(): boolean {
    return this.config.showProgress === true && !!this.config.duration && this.config.duration > 0;
  }

  onClose(): void {
    this.clearTimeouts();
    this.isVisible = false;
    setTimeout(() => {
      this.close.emit(this.config.id || '');
    }, 300);
  }

  onActionClick(action: string): void {
    this.action.emit({ action, toastId: this.config.id || '' });
    this.onClose();
  }

  onMouseEnter(): void {
    this.clearTimeouts();
  }

  onMouseLeave(): void {
    this.startAutoClose();
    if (this.config.showProgress) {
      this.startProgress();
    }
  }

  private startAutoClose(): void {
    if (this.config.duration && this.config.duration > 0) {
      this.timeoutId = setTimeout(() => {
        this.onClose();
      }, this.config.duration);
    }
  }

  private startProgress(): void {
    if (!this.config.duration) return;

    const duration = this.config.duration;
    const interval = 50; // Update every 50ms
    const increment = (interval / duration) * 100;

    this.progress = 0;
    this.progressInterval = setInterval(() => {
      this.progress += increment;
      if (this.progress >= 100) {
        this.progress = 100;
        clearInterval(this.progressInterval);
      }
    }, interval);
  }

  private clearTimeouts(): void {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
      this.progressInterval = null;
    }
  }

  getActionClass(type?: string): string {
    const baseClass = 'toast-action';
    return type ? `${baseClass} ${baseClass}-${type}` : baseClass;
  }
}
