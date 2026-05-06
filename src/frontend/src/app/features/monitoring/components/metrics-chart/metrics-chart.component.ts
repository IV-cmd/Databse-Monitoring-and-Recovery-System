import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface MetricData {
  timestamp: string;
  value: number;
  label?: string;
}

export interface ChartConfig {
  title: string;
  type: 'line' | 'bar' | 'area';
  color: string;
  unit: string;
  max?: number;
  min?: number;
}

@Component({
  selector: 'app-metrics-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './metrics-chart.component.html',
  styleUrls: ['./metrics-chart.component.scss']
})
export class MetricsChartComponent implements OnInit {
  @Input() metrics: MetricData[] = [];
  @Input() config: ChartConfig = {
    title: 'Metrics',
    type: 'line',
    color: '#667eea',
    unit: '%'
  };
  @Input() height: number = 200;
  @Input() showGrid: boolean = true;
  @Input() showLegend: boolean = true;

  chartData: any[] = [];
  chartOptions: any = {};

  ngOnInit(): void {
    this.setupChart();
  }

  ngOnChanges(): void {
    this.setupChart();
  }

  private setupChart(): void {
    if (!this.metrics || this.metrics.length === 0) return;

    this.chartData = this.metrics.map(metric => ({
      name: metric.label || metric.timestamp,
      value: metric.value,
      timestamp: metric.timestamp
    }));

    this.chartOptions = {
      series: [{
        name: this.config.title,
        data: this.chartData,
        color: this.config.color
      }],
      chart: {
        type: this.config.type,
        height: this.height,
        toolbar: {
          show: false
        }
      },
      xaxis: {
        type: 'datetime',
        labels: {
          format: 'HH:mm'
        }
      },
      yaxis: {
        title: {
          text: this.config.unit
        },
        min: this.config.min,
        max: this.config.max
      },
      grid: {
        show: this.showGrid
      },
      legend: {
        show: this.showLegend
      },
      theme: {
        mode: 'light'
      }
    };
  }

  getLatestValue(): number {
    return this.metrics.length > 0 ? this.metrics[this.metrics.length - 1].value : 0;
  }

  getAverageValue(): number {
    if (this.metrics.length === 0) return 0;
    const sum = this.metrics.reduce((acc, metric) => acc + metric.value, 0);
    return Math.round(sum / this.metrics.length);
  }

  getMinValue(): number {
    if (this.metrics.length === 0) return 0;
    return Math.min(...this.metrics.map(m => m.value));
  }

  getMaxValue(): number {
    if (this.metrics.length === 0) return 0;
    return Math.max(...this.metrics.map(m => m.value));
  }

  formatValue(value: number): string {
    return `${value}${this.config.unit}`;
  }

  getTrend(): 'up' | 'down' | 'stable' {
    if (this.metrics.length < 2) return 'stable';
    
    const recent = this.metrics.slice(-5);
    const older = this.metrics.slice(-10, -5);
    
    if (recent.length === 0 || older.length === 0) return 'stable';
    
    const recentAvg = recent.reduce((acc, m) => acc + m.value, 0) / recent.length;
    const olderAvg = older.reduce((acc, m) => acc + m.value, 0) / older.length;
    
    if (recentAvg > olderAvg * 1.05) return 'up';
    if (recentAvg < olderAvg * 0.95) return 'down';
    return 'stable';
  }

  getTrendIcon(): string {
    switch (this.getTrend()) {
      case 'up': return 'trending_up';
      case 'down': return 'trending_down';
      default: return 'trending_flat';
    }
  }

  getTrendClass(): string {
    switch (this.getTrend()) {
      case 'up': return 'trend-up';
      case 'down': return 'trend-down';
      default: return 'trend-stable';
    }
  }
}
