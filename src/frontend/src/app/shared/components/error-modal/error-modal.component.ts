import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ErrorModalData {
  title: string;
  message: string;
  type: 'error' | 'warning' | 'info';
  showCloseButton?: boolean;
}

@Component({
  selector: 'app-error-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './error-modal.component.html',
  styleUrls: ['./error-modal.component.scss']
})
export class ErrorModalComponent {
  @Input() errorData: ErrorModalData | null = null;
  @Input() isVisible: boolean = false;
  @Output() closeModal = new EventEmitter<void>();
  @Output() retryAction = new EventEmitter<void>();

  get modalClass(): string {
    if (!this.errorData) return '';
    
    switch (this.errorData.type) {
      case 'error':
        return 'modal-error';
      case 'warning':
        return 'modal-warning';
      case 'info':
        return 'modal-info';
      default:
        return 'modal-error';
    }
  }

  get icon(): string {
    if (!this.errorData) return '';
    
    switch (this.errorData.type) {
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return '❌';
    }
  }

  onClose(): void {
    this.closeModal.emit();
  }

  onRetry(): void {
    this.retryAction.emit();
    this.closeModal.emit();
  }

  onBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.onClose();
    }
  }
}
