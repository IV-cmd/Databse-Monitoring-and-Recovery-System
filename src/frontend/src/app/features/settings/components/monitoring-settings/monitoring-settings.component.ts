import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface MonitoringConfig {
  intervalSeconds: number;
  autoRecoveryEnabled: boolean;
  maxRecoveryAttempts: number;
  cpuWarning: number; cpuCritical: number;
  memoryWarning: number; memoryCritical: number;
  diskWarning: number; diskCritical: number;
  maxConnections: number;
  replicationLagThreshold: number;
  databaseSizeThresholdGb: number;
}

const DEFAULTS: MonitoringConfig = {
  intervalSeconds: 30, autoRecoveryEnabled: true, maxRecoveryAttempts: 3,
  cpuWarning: 80, cpuCritical: 95,
  memoryWarning: 85, memoryCritical: 95,
  diskWarning: 85, diskCritical: 95,
  maxConnections: 100, replicationLagThreshold: 10, databaseSizeThresholdGb: 10
};

@Component({
  selector: 'app-monitoring-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './monitoring-settings.component.html',
  styleUrls: ['./monitoring-settings.component.scss']
})
export class MonitoringSettingsComponent implements OnInit {
  config: MonitoringConfig = { ...DEFAULTS };
  private saved: MonitoringConfig = { ...DEFAULTS };
  isDirty = false;
  showToast = false; toastMsg = ''; toastType: 'success'|'error' = 'success';

  ngOnInit(): void {
    const s = localStorage.getItem('settings_monitoring');
    if (s) this.config = { ...DEFAULTS, ...JSON.parse(s) };
    this.saved = { ...this.config };
  }

  onChange(): void { this.isDirty = JSON.stringify(this.config) !== JSON.stringify(this.saved); }

  save(): void {
    localStorage.setItem('settings_monitoring', JSON.stringify(this.config));
    this.saved = { ...this.config }; this.isDirty = false;
    this.toast('Monitoring settings saved', 'success');
  }

  reset(): void { this.config = { ...DEFAULTS }; this.onChange(); }

  private toast(msg: string, type: 'success'|'error'): void {
    this.toastMsg = msg; this.toastType = type; this.showToast = true;
    setTimeout(() => this.showToast = false, 3000);
  }
}
