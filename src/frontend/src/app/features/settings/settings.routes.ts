import { Routes } from '@angular/router';
import { DatabaseSettingsComponent } from './components/database-settings/database-settings.component';
import { MonitoringSettingsComponent } from './components/monitoring-settings/monitoring-settings.component';
import { NotificationSettingsComponent } from './components/notification-settings/notification-settings.component';
import { SystemSettingsComponent } from './components/system-settings/system-settings.component';

export const settingsRoutes: Routes = [
  {
    path: '',
    component: SystemSettingsComponent
  },
  {
    path: 'system',
    component: SystemSettingsComponent
  },
  {
    path: 'database',
    component: DatabaseSettingsComponent
  },
  {
    path: 'monitoring',
    component: MonitoringSettingsComponent
  },
  {
    path: 'notifications',
    component: NotificationSettingsComponent
  }
];
