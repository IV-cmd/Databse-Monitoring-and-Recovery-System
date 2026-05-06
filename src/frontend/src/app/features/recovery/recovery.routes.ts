import { Routes } from '@angular/router';
import { RecoveryDashboardComponent } from './components/recovery-dashboard/recovery-dashboard.component';
import { RecoveryFormComponent } from './components/recovery-form/recovery-form.component';
import { RecoveryListComponent } from './components/recovery-list/recovery-list.component';
import { RecoveryStatusComponent } from './components/recovery-status/recovery-status.component';
import { RecoveryHistoryComponent } from './components/recovery-history/recovery-history.component';

export const recoveryRoutes: Routes = [
  {
    path: '',
    component: RecoveryDashboardComponent
  },
  {
    path: 'dashboard',
    component: RecoveryDashboardComponent
  },
  {
    path: 'form',
    component: RecoveryFormComponent
  },
  {
    path: 'list',
    component: RecoveryListComponent
  },
  {
    path: 'status/:id',
    component: RecoveryStatusComponent
  },
  {
    path: 'history',
    component: RecoveryHistoryComponent
  }
];
