import { Component, Input, Output, EventEmitter, AfterViewInit, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface ChartDataPoint {
  label: string;
  value: number;
  timestamp?: string;
  color?: string;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'area' | 'pie' | 'gauge';
  data: ChartDataPoint[];
  title?: string;
  subtitle?: string;
  width?: number;
  height?: number;
  showLegend?: boolean;
  showGrid?: boolean;
  showTooltip?: boolean;
  animated?: boolean;
  colors?: string[];
  thresholds?: {
    warning: number;
    critical: number;
  };
  unit?: string;
  max?: number;
  min?: number;
}

@Component({
  selector: 'app-chart',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chart.component.html',
  styleUrls: ['./chart.component.scss']
})
export class ChartComponent implements AfterViewInit {
  @Input() config!: ChartConfig;
  @Output() dataPointClick = new EventEmitter<ChartDataPoint>();

  private canvas!: HTMLCanvasElement;
  private ctx!: CanvasRenderingContext2D;
  private animationFrame!: number;

  constructor(private elementRef: ElementRef) {}

  ngAfterViewInit(): void {
    this.canvas = this.elementRef.nativeElement.querySelector('canvas');
    this.ctx = this.canvas.getContext('2d')!;
    this.setupCanvas();
    this.drawChart();
  }

  get chartClass(): string {
    const classes = ['chart'];
    classes.push(`chart-${this.config.type}`);
    if (this.config.animated) classes.push('chart-animated');
    return classes.join(' ');
  }

  get chartStyle(): { [key: string]: string } {
    return {
      width: `${this.config.width || 400}px`,
      height: `${this.config.height || 300}px`
    };
  }

  private setupCanvas(): void {
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    
    this.ctx.scale(dpr, dpr);
    
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = rect.height + 'px';
  }

  private drawChart(): void {
    if (!this.ctx || !this.config.data) return;

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    switch (this.config.type) {
      case 'line':
        this.drawLineChart();
        break;
      case 'bar':
        this.drawBarChart();
        break;
      case 'area':
        this.drawAreaChart();
        break;
      case 'pie':
        this.drawPieChart();
        break;
      case 'gauge':
        this.drawGaugeChart();
        break;
    }
  }

  private drawLineChart(): void {
    const data = this.config.data;
    const padding = 40;
    const width = this.canvas.width / (window.devicePixelRatio || 1) - padding * 2;
    const height = this.canvas.height / (window.devicePixelRatio || 1) - padding * 2;
    
    // Draw grid
    if (this.config.showGrid) {
      this.drawGrid(padding, width, height);
    }

    // Calculate points
    const maxValue = Math.max(...data.map(d => d.value));
    const points = data.map((point, index) => ({
      x: padding + (index / (data.length - 1)) * width,
      y: padding + height - (point.value / maxValue) * height,
      data: point
    }));

    // Draw line
    this.ctx.beginPath();
    this.ctx.strokeStyle = this.getPrimaryColor();
    this.ctx.lineWidth = 2;
    
    points.forEach((point, index) => {
      if (index === 0) {
        this.ctx.moveTo(point.x, point.y);
      } else {
        this.ctx.lineTo(point.x, point.y);
      }
    });
    
    this.ctx.stroke();

    // Draw points
    points.forEach(point => {
      this.ctx.beginPath();
      this.ctx.arc(point.x, point.y, 4, 0, Math.PI * 2);
      this.ctx.fillStyle = this.getPrimaryColor();
      this.ctx.fill();
      this.ctx.strokeStyle = 'white';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();
    });
  }

  private drawBarChart(): void {
    const data = this.config.data;
    const padding = 40;
    const width = this.canvas.width / (window.devicePixelRatio || 1) - padding * 2;
    const height = this.canvas.height / (window.devicePixelRatio || 1) - padding * 2;
    
    if (this.config.showGrid) {
      this.drawGrid(padding, width, height);
    }

    const maxValue = Math.max(...data.map(d => d.value));
    const barWidth = width / data.length * 0.6;
    const barSpacing = width / data.length * 0.4;

    data.forEach((point, index) => {
      const barHeight = (point.value / maxValue) * height;
      const x = padding + index * (barWidth + barSpacing) + barSpacing / 2;
      const y = padding + height - barHeight;

      // Draw bar
      this.ctx.fillStyle = this.getColorForValue(point.value);
      this.ctx.fillRect(x, y, barWidth, barHeight);

      // Draw value label
      this.ctx.fillStyle = '#374151';
      this.ctx.font = '12px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(point.value.toString(), x + barWidth / 2, y - 5);
    });
  }

  private drawAreaChart(): void {
    const data = this.config.data;
    const padding = 40;
    const width = this.canvas.width / (window.devicePixelRatio || 1) - padding * 2;
    const height = this.canvas.height / (window.devicePixelRatio || 1) - padding * 2;
    
    if (this.config.showGrid) {
      this.drawGrid(padding, width, height);
    }

    const maxValue = Math.max(...data.map(d => d.value));
    const points = data.map((point, index) => ({
      x: padding + (index / (data.length - 1)) * width,
      y: padding + height - (point.value / maxValue) * height,
      data: point
    }));

    // Draw area
    this.ctx.beginPath();
    this.ctx.moveTo(points[0].x, padding + height);
    
    points.forEach(point => {
      this.ctx.lineTo(point.x, point.y);
    });
    
    this.ctx.lineTo(points[points.length - 1].x, padding + height);
    this.ctx.closePath();
    
    // Create gradient
    const gradient = this.ctx.createLinearGradient(0, padding, 0, padding + height);
    gradient.addColorStop(0, this.getPrimaryColor() + '40');
    gradient.addColorStop(1, this.getPrimaryColor() + '10');
    
    this.ctx.fillStyle = gradient;
    this.ctx.fill();

    // Draw line on top
    this.ctx.beginPath();
    this.ctx.strokeStyle = this.getPrimaryColor();
    this.ctx.lineWidth = 2;
    
    points.forEach((point, index) => {
      if (index === 0) {
        this.ctx.moveTo(point.x, point.y);
      } else {
        this.ctx.lineTo(point.x, point.y);
      }
    });
    
    this.ctx.stroke();
  }

  private drawPieChart(): void {
    const data = this.config.data;
    const centerX = this.canvas.width / (window.devicePixelRatio || 1) / 2;
    const centerY = this.canvas.height / (window.devicePixelRatio || 1) / 2;
    const radius = Math.min(centerX, centerY) - 40;
    
    const total = data.reduce((sum, point) => sum + point.value, 0);
    let currentAngle = -Math.PI / 2;

    data.forEach((point, index) => {
      const sliceAngle = (point.value / total) * Math.PI * 2;
      
      // Draw slice
      this.ctx.beginPath();
      this.ctx.moveTo(centerX, centerY);
      this.ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
      this.ctx.closePath();
      
      this.ctx.fillStyle = this.getColorForIndex(index);
      this.ctx.fill();
      
      // Draw label
      const labelAngle = currentAngle + sliceAngle / 2;
      const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7);
      const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7);
      
      this.ctx.fillStyle = 'white';
      this.ctx.font = 'bold 12px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(point.label, labelX, labelY);
      
      currentAngle += sliceAngle;
    });
  }

  private drawGaugeChart(): void {
    const centerX = this.canvas.width / (window.devicePixelRatio || 1) / 2;
    const centerY = this.canvas.height / (window.devicePixelRatio || 1) / 2 + 20;
    const radius = Math.min(centerX, centerY) - 40;
    
    if (!this.config.data || this.config.data.length === 0) return;
    
    const value = this.config.data[0].value;
    const maxValue = this.config.max || 100;
    const percentage = Math.min(value / maxValue, 1);
    
    // Draw background arc
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, Math.PI, 0);
    this.ctx.strokeStyle = '#e5e7eb';
    this.ctx.lineWidth = 20;
    this.ctx.stroke();
    
    // Draw value arc
    const endAngle = Math.PI + (Math.PI * percentage);
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius, Math.PI, endAngle);
    this.ctx.strokeStyle = this.getColorForValue(value);
    this.ctx.lineWidth = 20;
    this.ctx.stroke();
    
    // Draw value text
    this.ctx.fillStyle = '#111827';
    this.ctx.font = 'bold 24px sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.fillText(value.toString(), centerX, centerY);
    
    // Draw unit
    if (this.config.unit) {
      this.ctx.font = '14px sans-serif';
      this.ctx.fillStyle = '#6b7280';
      this.ctx.fillText(this.config.unit, centerX, centerY + 20);
    }
    
    // Draw thresholds
    if (this.config.thresholds) {
      this.drawThresholds(centerX, centerY, radius, maxValue);
    }
  }

  private drawGrid(padding: number, width: number, height: number): void {
    this.ctx.strokeStyle = '#f3f4f6';
    this.ctx.lineWidth = 1;
    
    // Horizontal lines
    for (let i = 0; i <= 5; i++) {
      const y = padding + (height / 5) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(padding, y);
      this.ctx.lineTo(padding + width, y);
      this.ctx.stroke();
    }
    
    // Vertical lines
    for (let i = 0; i <= 5; i++) {
      const x = padding + (width / 5) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(x, padding);
      this.ctx.lineTo(x, padding + height);
      this.ctx.stroke();
    }
  }

  private drawThresholds(centerX: number, centerY: number, radius: number, maxValue: number): void {
    const thresholds = this.config.thresholds;
    if (!thresholds) return;
    
    // Warning threshold
    const warningAngle = Math.PI + (Math.PI * (thresholds.warning / maxValue));
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius + 25, warningAngle - 0.1, warningAngle + 0.1);
    this.ctx.strokeStyle = '#f59e0b';
    this.ctx.lineWidth = 3;
    this.ctx.stroke();
    
    // Critical threshold
    const criticalAngle = Math.PI + (Math.PI * (thresholds.critical / maxValue));
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, radius + 25, criticalAngle - 0.1, criticalAngle + 0.1);
    this.ctx.strokeStyle = '#ef4444';
    this.ctx.lineWidth = 3;
    this.ctx.stroke();
  }

  private getPrimaryColor(): string {
    return this.config.colors?.[0] || '#667eea';
  }

  getColorForIndex(index: number): string {
    const colors = this.config.colors || ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];
    return colors[index % colors.length];
  }

  private getColorForValue(value: number): string {
    if (!this.config.thresholds) return this.getPrimaryColor();
    
    if (value >= this.config.thresholds.critical) return '#ef4444';
    if (value >= this.config.thresholds.warning) return '#f59e0b';
    return '#10b981';
  }

  onCanvasClick(event: MouseEvent): void {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Simple hit detection - could be enhanced for each chart type
    const dataPoint = this.findDataPointAt(x, y);
    if (dataPoint) {
      this.dataPointClick.emit(dataPoint);
    }
  }

  private findDataPointAt(x: number, y: number): ChartDataPoint | null {
    // Simplified hit detection - would need to be enhanced for production
    return null;
  }
}
