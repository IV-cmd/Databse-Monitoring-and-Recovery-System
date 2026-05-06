import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardComponent } from './components/dashboard.component';
import { QuickActionsComponent } from './components/quick-actions/quick-actions.component';

@NgModule({
  declarations: [
    DashboardComponent,
    QuickActionsComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: '', component: DashboardComponent },
      { path: 'quick-actions', component: QuickActionsComponent }
    ])
  ],
  exports: [
    DashboardComponent,
    QuickActionsComponent
  ]
})
export class DashboardModule { }
