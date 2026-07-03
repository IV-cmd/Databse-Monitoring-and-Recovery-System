import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export interface SystemConfig {
  environment: 'development' | 'staging' | 'production';
  logLevel: 'debug' | 'info' | 'warning' | 'error';
  debugMode: boolean;
  maintenanceMode: boolean;
  sessionTimeout: number;
  timezone: string;
  dateFormat: 'MM/DD/YYYY' | 'DD/MM/YYYY' | 'YYYY-MM-DD';
  language: string;
  maxLoginAttempts: number;
  passwordMinLength: number;
}

const DEFAULTS: SystemConfig = {
  environment: 'development', logLevel: 'info', debugMode: false,
  maintenanceMode: false, sessionTimeout: 30, timezone: 'UTC',
  dateFormat: 'MM/DD/YYYY', language: 'en', maxLoginAttempts: 5, passwordMinLength: 8
};

@Component({
  selector: 'app-system-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './system-settings.component.html',
  styleUrls: ['./system-settings.component.scss']
})
export class SystemSettingsComponent implements OnInit, OnDestroy {
  config: SystemConfig = { ...DEFAULTS };
  private saved: SystemConfig = { ...DEFAULTS };
  isDirty = false;
  showToast = false;
  toastMsg = '';
  toastType: 'success' | 'error' = 'success';

  environments: { value: SystemConfig['environment']; label: string; icon: string; color: string }[] = [
    { value: 'development', label: 'Development', icon: '🧪', color: '#3b82f6' },
    { value: 'staging',     label: 'Staging',     icon: '🔧', color: '#f59e0b' },
    { value: 'production',  label: 'Production',  icon: '🚀', color: '#10b981' }
  ];
  logLevels: { value: SystemConfig['logLevel']; label: string; color: string }[] = [
    { value: 'debug',   label: 'Debug',   color: '#6366f1' },
    { value: 'info',    label: 'Info',    color: '#3b82f6' },
    { value: 'warning', label: 'Warning', color: '#f59e0b' },
    { value: 'error',   label: 'Error',   color: '#ef4444' }
  ];
  timezones = [
    { value: 'UTC',                  label: 'UTC (Coordinated Universal Time)' },
    { value: 'Europe/Geneva',        label: 'Geneva (CET/CEST)' },
    { value: 'Europe/London',        label: 'London (GMT/BST)' },
    { value: 'Europe/Paris',         label: 'Paris (CET/CEST)' },
    { value: 'America/New_York',     label: 'New York (ET)' },
    { value: 'America/Los_Angeles',  label: 'Los Angeles (PT)' },
    { value: 'Asia/Tokyo',           label: 'Tokyo (JST)' },
  ];
  dateFormats = [
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (ISO)' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
  ];
  languages = [
    { value: 'en', label: '🇬🇧 English' },
    { value: 'fr', label: '🇫🇷 French' },
    { value: 'de', label: '🇩🇪 German' },
    { value: 'es', label: '🇪🇸 Spanish' },
  ];

  private kbHandler = (e: KeyboardEvent) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); this.save(); }
  };

  ngOnInit(): void {
    const stored = localStorage.getItem('settings_system');
    if (stored) this.config = { ...DEFAULTS, ...JSON.parse(stored) };
    this.saved = { ...this.config };
    document.addEventListener('keydown', this.kbHandler);
  }

  ngOnDestroy(): void {
    document.removeEventListener('keydown', this.kbHandler);
  }

  onChange(): void {
    this.isDirty = JSON.stringify(this.config) !== JSON.stringify(this.saved);
  }

  save(): void {
    localStorage.setItem('settings_system', JSON.stringify(this.config));
    this.saved = { ...this.config };
    this.isDirty = false;
    this.toast('System settings saved', 'success');
  }

  reset(): void {
    this.config = { ...DEFAULTS };
    this.onChange();
  }

  private toast(msg: string, type: 'success' | 'error'): void {
    this.toastMsg = msg; this.toastType = type; this.showToast = true;
    setTimeout(() => this.showToast = false, 3000);
  }
}
