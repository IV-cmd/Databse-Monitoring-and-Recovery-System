import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-settings-shell',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterLink, RouterLinkActive],
  templateUrl: './settings-shell.component.html',
  styleUrls: ['./settings-shell.component.scss']
})
export class SettingsShellComponent {
  navItems = [
    { path: 'system',        label: 'System',        icon: '⚙️',  desc: 'Environment & security'  },
    { path: 'database',      label: 'Database',      icon: '🗄️',  desc: 'Connections & pool'      },
    { path: 'monitoring',    label: 'Monitoring',    icon: '📊',  desc: 'Intervals & thresholds'  },
    { path: 'notifications', label: 'Notifications', icon: '🔔',  desc: 'Email, Slack & SMS'      },
  ];
}
