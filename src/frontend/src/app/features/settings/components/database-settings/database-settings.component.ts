import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface DatabaseConfig {
  primaryUrl: string;
  replicaUrl: string;
  sslEnabled: boolean;
  sslCertFile: string;
  sslKeyFile: string;
  sslCaFile: string;
  sslVerify: 'disable' | 'prefer' | 'require';
  maxConnections: number;
  minConnections: number;
  commandTimeout: number;
}

const DEFAULTS: DatabaseConfig = {
  primaryUrl: 'postgresql://admin:admin123@localhost:5432/monitoring_db',
  replicaUrl: 'postgresql://admin:admin123@localhost:5433/monitoring_db',
  sslEnabled: false, sslCertFile: '', sslKeyFile: '', sslCaFile: '',
  sslVerify: 'disable', maxConnections: 100, minConnections: 10, commandTimeout: 60
};

@Component({
  selector: 'app-database-settings',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './database-settings.component.html',
  styleUrls: ['./database-settings.component.scss']
})
export class DatabaseSettingsComponent implements OnInit {
  config: DatabaseConfig = { ...DEFAULTS };
  private saved: DatabaseConfig = { ...DEFAULTS };
  isDirty = false;
  showToast = false; toastMsg = ''; toastType: 'success'|'error' = 'success';
  showPrimary = false; showReplica = false;
  connStatus: 'idle'|'testing'|'ok'|'fail' = 'idle';
  connMsg = '';
  sslOptions = [
    { value: 'disable', label: 'Disabled' },
    { value: 'prefer',  label: 'Preferred' },
    { value: 'require', label: 'Required' }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    const s = localStorage.getItem('settings_database');
    if (s) this.config = { ...DEFAULTS, ...JSON.parse(s) };
    this.saved = { ...this.config };
  }

  onChange(): void { this.isDirty = JSON.stringify(this.config) !== JSON.stringify(this.saved); }

  onSslToggle(): void {
    if (!this.config.sslEnabled) { this.config.sslCertFile = ''; this.config.sslKeyFile = ''; this.config.sslCaFile = ''; this.config.sslVerify = 'disable'; }
    this.onChange();
  }

  testConnection(): void {
    this.connStatus = 'testing'; this.connMsg = 'Connecting…';
    this.http.get<any>('http://localhost:8000/api/v1/health/dependencies').subscribe({
      next: (r) => {
        const pg = r?.dependencies?.postgresql?.status ?? r?.postgresql?.status ?? 'unknown';
        if (pg === 'healthy') { this.connStatus = 'ok'; this.connMsg = 'Connected — PostgreSQL is healthy'; }
        else { this.connStatus = 'fail'; this.connMsg = `Status: ${pg}`; }
      },
      error: () => { this.connStatus = 'fail'; this.connMsg = 'Could not reach the health endpoint'; }
    });
  }

  copy(val: string): void { navigator.clipboard.writeText(val).then(() => this.toast('Copied!', 'success')); }

  save(): void {
    localStorage.setItem('settings_database', JSON.stringify(this.config));
    this.saved = { ...this.config }; this.isDirty = false;
    this.toast('Database settings saved', 'success');
  }

  reset(): void { this.config = { ...DEFAULTS }; this.onChange(); }

  private toast(msg: string, type: 'success'|'error'): void {
    this.toastMsg = msg; this.toastType = type; this.showToast = true;
    setTimeout(() => this.showToast = false, 3000);
  }
}
