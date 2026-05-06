import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { RecoveryDashboardComponent } from './components/recovery-dashboard/recovery-dashboard.component';
import { RecoveryFormComponent } from './components/recovery-form/recovery-form.component';
import { RecoveryListComponent } from './components/recovery-list/recovery-list.component';
import { RecoveryStatusComponent } from './components/recovery-status/recovery-status.component';
import { RecoveryHistoryComponent } from './components/recovery-history/recovery-history.component';

@NgModule({
  declarations: [
    RecoveryDashboardComponent,
    RecoveryFormComponent,
    RecoveryListComponent,
    RecoveryStatusComponent,
    RecoveryHistoryComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: '', component: RecoveryDashboardComponent },
      { path: 'dashboard', component: RecoveryDashboardComponent },
      { path: 'form', component: RecoveryFormComponent },
      { path: 'list', component: RecoveryListComponent },
      { path: 'status/:id', component: RecoveryStatusComponent },
      { path: 'history', component: RecoveryHistoryComponent }
    ])
  ],
  exports: [
    RecoveryDashboardComponent,
    RecoveryFormComponent,
    RecoveryListComponent,
    RecoveryStatusComponent,
    RecoveryHistoryComponent
  ]
})
export class RecoveryModule { }
