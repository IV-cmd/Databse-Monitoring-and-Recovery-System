import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, RecoveryRequest } from '../../../../core/services/api.service';

export interface RecoveryFormData {
  type: 'backup' | 'restore' | 'repair' | 'rebuild';
  reason: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  details?: string;
}

@Component({
  selector: 'app-recovery-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './recovery-form.component.html',
  styleUrls: ['./recovery-form.component.scss']
})
export class RecoveryFormComponent {
  @Output() formSubmit = new EventEmitter<RecoveryFormData>();
  @Output() cancel = new EventEmitter<void>();

  formData: RecoveryFormData = {
    type: 'backup',
    reason: '',
    severity: 'medium',
    details: ''
  };

  recoveryTypes = [
    { value: 'backup', label: '💾 Backup' },
    { value: 'restore', label: '🔄 Restore' },
    { value: 'repair', label: '🔧 Repair' },
    { value: 'rebuild', label: '🏗️ Rebuild' }
  ];

  severityLevels = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
  ];

  onSubmit(): void {
    if (this.isFormValid()) {
      this.formSubmit.emit(this.formData);
    }
  }

  onCancel(): void {
    this.cancel.emit();
  }

  isFormValid(): boolean {
    return this.formData.type && this.formData.reason.trim().length > 0;
  }

  getTypeIcon(type: string): string {
    const selected = this.recoveryTypes.find(t => t.value === type);
    return selected ? selected.label.split(' ')[0] : '📋';
  }

  resetForm(): void {
    this.formData = {
      type: 'backup',
      reason: '',
      severity: 'medium',
      details: ''
    };
  }
}
