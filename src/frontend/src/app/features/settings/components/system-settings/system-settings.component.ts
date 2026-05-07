import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-system-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './system-settings.component.html',
  styleUrls: ['./system-settings.component.scss']
})
export class SystemSettingsComponent {
  config: SystemConfig = {
    environment: 'development',
    logLevel: 'info',
    debugMode: false,
    maintenanceMode: false,
    sessionTimeout: 30,
    timezone: 'UTC',
    dateFormat: 'MM/DD/YYYY',
    language: 'en',
    maxLoginAttempts: 5,
    passwordMinLength: 8
  };

  environments = [
    { value: 'development', label: 'Development' },
    { value: 'staging', label: 'Staging' },
    { value: 'production', label: 'Production' }
  ];

  logLevels = [
    { value: 'debug', label: 'Debug' },
    { value: 'info', label: 'Info' },
    { value: 'warning', label: 'Warning' },
    { value: 'error', label: 'Error' }
  ];

  timezones = [
    { value: 'UTC', label: 'UTC' },
    { value: 'America/New_York', label: 'Eastern Time' },
    { value: 'America/Chicago', label: 'Central Time' },
    { value: 'America/Denver', label: 'Mountain Time' },
    { value: 'America/Los_Angeles', label: 'Pacific Time' },
    { value: 'Europe/London', label: 'London' },
    { value: 'Europe/Paris', label: 'Paris' },
    { value: 'Asia/Tokyo', label: 'Tokyo' }
  ];

  dateFormats = [
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY' },
    { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD' }
  ];

  languages = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'it', label: 'Italian' },
    { value: 'pt', label: 'Portuguese' },
    { value: 'zh', label: 'Chinese' },
    { value: 'ja', label: 'Japanese' }
  ];

  saveSettings(): void {
    console.log('Saving system settings:', this.config);
  }

  resetSettings(): void {
    this.config = {
      environment: 'development',
      logLevel: 'info',
      debugMode: false,
      maintenanceMode: false,
      sessionTimeout: 30,
      timezone: 'UTC',
      dateFormat: 'MM/DD/YYYY',
      language: 'en',
      maxLoginAttempts: 5,
      passwordMinLength: 8
    };
  }
}

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
