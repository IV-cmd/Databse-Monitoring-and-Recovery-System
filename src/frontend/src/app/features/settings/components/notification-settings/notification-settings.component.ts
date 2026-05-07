import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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

@Component({
  selector: 'app-notification-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './notification-settings.component.html',
  styleUrls: ['./notification-settings.component.scss']
})
export class NotificationSettingsComponent {
  config: NotificationConfig = {
    emailEnabled: false,
    emailSmtpHost: '',
    emailSmtpPort: 587,
    emailUsername: '',
    emailPassword: '',
    emailFrom: '',
    emailTo: '',
    slackEnabled: false,
    slackWebhookUrl: '',
    slackChannel: '',
    alertSeverity: 'medium',
    alertCooldownMinutes: 15,
    enableSms: false,
    smsPhoneNumber: ''
  };

  severityLevels = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' }
  ];

  saveSettings(): void {
    console.log('Saving notification settings:', this.config);
  }

  resetSettings(): void {
    this.config = {
      emailEnabled: false,
      emailSmtpHost: '',
      emailSmtpPort: 587,
      emailUsername: '',
      emailPassword: '',
      emailFrom: '',
      emailTo: '',
      slackEnabled: false,
      slackWebhookUrl: '',
      slackChannel: '',
      alertSeverity: 'medium',
      alertCooldownMinutes: 15,
      enableSms: false,
      smsPhoneNumber: ''
    };
  }

  testEmailNotification(): void {
    console.log('Testing email notification...');
  }

  testSlackNotification(): void {
    console.log('Testing Slack notification...');
  }
}
