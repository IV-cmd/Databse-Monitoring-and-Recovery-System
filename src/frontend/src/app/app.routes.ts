import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    loadChildren: () => import('./features/dashboard/dashboard.routes').then(m => m.dashboardRoutes)
  },
  {
    path: 'monitoring',
    loadChildren: () => import('./features/monitoring/monitoring.routes').then(m => m.monitoringRoutes)
  },
  {
    path: 'recovery',
    loadChildren: () => import('./features/recovery/recovery.routes').then(m => m.recoveryRoutes)
  },
  {
    path: 'settings',
    loadChildren: () => import('./features/settings/settings.routes').then(m => m.settingsRoutes)
  },
  {
    path: '**',
    redirectTo: '/dashboard'
  }
];
