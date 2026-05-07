import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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

@Component({
  selector: 'app-monitoring-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './monitoring-settings.component.html',
  styleUrls: ['./monitoring-settings.component.scss']
})
export class MonitoringSettingsComponent {
  config: MonitoringConfig = {
    intervalSeconds: 30,
    autoRecoveryEnabled: true,
    maxRecoveryAttempts: 3,
    cpuWarning: 80,
    cpuCritical: 95,
    memoryWarning: 85,
    memoryCritical: 95,
    diskWarning: 85,
    diskCritical: 95,
    maxConnections: 100,
    replicationLagThreshold: 10,
    databaseSizeThresholdGb: 10
  };

  saveSettings(): void {
    console.log('Saving monitoring settings:', this.config);
  }

  resetSettings(): void {
    this.config = {
      intervalSeconds: 30,
      autoRecoveryEnabled: true,
      maxRecoveryAttempts: 3,
      cpuWarning: 80,
      cpuCritical: 95,
      memoryWarning: 85,
      memoryCritical: 95,
      diskWarning: 85,
      diskCritical: 95,
      maxConnections: 100,
      replicationLagThreshold: 10,
      databaseSizeThresholdGb: 10
    };
  }
}
