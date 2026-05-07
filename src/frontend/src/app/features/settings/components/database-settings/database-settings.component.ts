import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

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

@Component({
  selector: 'app-database-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './database-settings.component.html',
  styleUrls: ['./database-settings.component.scss']
})
export class DatabaseSettingsComponent {
  config: DatabaseConfig = {
    primaryUrl: '',
    sslEnabled: false,
    sslVerify: 'disable',
    maxConnections: 100,
    minConnections: 10,
    commandTimeout: 60
  };

  sslOptions = [
    { value: 'disable', label: 'Disabled' },
    { value: 'prefer', label: 'Preferred' },
    { value: 'require', label: 'Required' }
  ];

  onSslToggle(): void {
    if (!this.config.sslEnabled) {
      this.config.sslCertFile = '';
      this.config.sslKeyFile = '';
      this.config.sslCaFile = '';
      this.config.sslVerify = 'disable';
    }
  }

  saveSettings(): void {
    console.log('Saving database settings:', this.config);
  }

  resetSettings(): void {
    this.config = {
      primaryUrl: '',
      sslEnabled: false,
      sslVerify: 'disable',
      maxConnections: 100,
      minConnections: 10,
      commandTimeout: 60
    };
  }
}
