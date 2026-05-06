import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

export interface QuickAction {
  id: string;
  label: string;
  icon: string;
  route: string;
  description?: string;
  badge?: string;
  disabled?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
}

@Component({
  selector: 'app-quick-actions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './quick-actions.component.html',
  styleUrls: ['./quick-actions.component.scss']
})
export class QuickActionsComponent {
  @Input() actions: QuickAction[] = [];
  @Input() title: string = 'Quick Actions';
  @Input() layout: 'grid' | 'list' = 'grid';
  @Input() showDescriptions: boolean = true;

  constructor(private router: Router) {}

  executeAction(action: QuickAction): void {
    if (action.disabled) return;
    
    this.router.navigate([action.route]);
  }

  getActionClass(action: QuickAction): string {
    let classes = 'action-btn';
    
    if (action.color) {
      classes += ` color-${action.color}`;
    }
    
    if (action.disabled) {
      classes += ' disabled';
    }
    
    return classes;
  }

  getIconClass(action: QuickAction): string {
    return `material-icons ${action.icon}`;
  }

  trackAction(action: QuickAction): void {
    console.log(`Quick action executed: ${action.label}`, action);
  }
}
