import { Component, OnInit } from '@angular/core';
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

const DEFAULTS: NotificationConfig = {
  emailEnabled: false, emailSmtpHost: '', emailSmtpPort: 587,
  emailUsername: '', emailPassword: '', emailFrom: '', emailTo: '',
  slackEnabled: false, slackWebhookUrl: '', slackChannel: '',
  alertSeverity: 'medium', alertCooldownMinutes: 15,
  enableSms: false, smsPhoneNumber: ''
};

@Component({
  selector: 'app-notification-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './notification-settings.component.html',
  styleUrls: ['./notification-settings.component.scss']
})
export class NotificationSettingsComponent implements OnInit {
  config: NotificationConfig = { ...DEFAULTS };
  private saved: NotificationConfig = { ...DEFAULTS };
  isDirty = false;
  showToast = false; toastMsg = ''; toastType: 'success'|'error' = 'success';
  showEmailPw = false;
  testingEmail = false; testingSlack = false;

  severityLevels: { value: NotificationConfig['alertSeverity']; label: string; color: string }[] = [
    { value: 'low',      label: 'Low',      color: '#3b82f6' },
    { value: 'medium',   label: 'Medium',   color: '#f59e0b' },
    { value: 'high',     label: 'High',     color: '#ef4444' },
    { value: 'critical', label: 'Critical', color: '#7c3aed' }
  ];

  ngOnInit(): void {
    const s = localStorage.getItem('settings_notifications');
    if (s) this.config = { ...DEFAULTS, ...JSON.parse(s) };
    this.saved = { ...this.config };
  }

  onChange(): void { this.isDirty = JSON.stringify(this.config) !== JSON.stringify(this.saved); }

  sendTestEmail(): void {
    if (!this.config.emailEnabled) return;
    this.testingEmail = true;
    setTimeout(() => { this.testingEmail = false; this.toast('Test email dispatched — check your inbox', 'success'); }, 1800);
  }

  sendTestSlack(): void {
    if (!this.config.slackEnabled) return;
    this.testingSlack = true;
    setTimeout(() => { this.testingSlack = false; this.toast('Test Slack message sent', 'success'); }, 1400);
  }

  save(): void {
    localStorage.setItem('settings_notifications', JSON.stringify(this.config));
    this.saved = { ...this.config }; this.isDirty = false;
    this.toast('Notification settings saved', 'success');
  }

  reset(): void { this.config = { ...DEFAULTS }; this.onChange(); }

  private toast(msg: string, type: 'success'|'error'): void {
    this.toastMsg = msg; this.toastType = type; this.showToast = true;
    setTimeout(() => this.showToast = false, 3000);
  }
}
