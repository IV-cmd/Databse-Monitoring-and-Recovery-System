import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { MonitoringComponent } from './components/monitoring.component';
import { AlertsPanelComponent } from './components/alerts-panel/alerts-panel.component';
import { MetricsChartComponent } from './components/metrics-chart/metrics-chart.component';
import { StatusIndicatorComponent } from './components/status-indicator/status-indicator.component';

@NgModule({
  declarations: [
    MonitoringComponent,
    AlertsPanelComponent,
    MetricsChartComponent,
    StatusIndicatorComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild([
      { path: '', component: MonitoringComponent }
    ])
  ],
  exports: [
    MonitoringComponent,
    AlertsPanelComponent,
    MetricsChartComponent,
    StatusIndicatorComponent
  ]
})
export class MonitoringModule { }
