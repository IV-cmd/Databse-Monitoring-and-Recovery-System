import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';

import { DatabaseSettingsComponent } from './components/database-settings/database-settings.component';
import { MonitoringSettingsComponent } from './components/monitoring-settings/monitoring-settings.component';
import { NotificationSettingsComponent } from './components/notification-settings/notification-settings.component';
import { SystemSettingsComponent } from './components/system-settings/system-settings.component';

export interface DatabaseConfig {
  primaryUrl: string;
  replicaUrl?: string;
  sslEnabled: boolean;
  sslCertFile?: string;
  sslKeyFile?: string;
  sslCaFile?: string;
  sslVerify: 'disable' | 'prefer' | 'require';
  maxConnections: number;
  minConnections: number;
  commandTimeout: number;
}

export interface MonitoringConfig {
  intervalSeconds: number;
  autoRecoveryEnabled: boolean;
  maxRecoveryAttempts: number;
  cpuWarning: number;
  cpuCritical: number;
  memoryWarning: number;
  memoryCritical: number;
  diskWarning: number;
  diskCritical: number;
  maxConnections: number;
  replicationLagThreshold: number;
  databaseSizeThresholdGb: number;
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

export interface NotificationConfig {
  emailEnabled: boolean;
  emailSmtpHost: string;
  emailSmtpPort: number;
  emailUsername: string;
  emailPassword: string;
  emailFrom: string;
  emailTo: string;
  slackEnabled: boolean;
  slackWebhookUrl: string;
  slackChannel: string;
  alertSeverity: 'low' | 'medium' | 'high' | 'critical';
  alertCooldownMinutes: number;
  enableSms: boolean;
  smsPhoneNumber: string;
}

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    FormsModule,
    RouterModule.forChild([
      { path: '', component: SystemSettingsComponent },
      { path: 'system', component: SystemSettingsComponent },
      { path: 'database', component: DatabaseSettingsComponent },
      { path: 'monitoring', component: MonitoringSettingsComponent },
      { path: 'notifications', component: NotificationSettingsComponent }
    ])
  ],
  exports: []
})
export class SettingsModule { }
