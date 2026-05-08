import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { Subscription } from 'rxjs';

export interface NavigationItem {
  label: string;
  route: string;
  icon: string;
  badge?: string | number;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent implements OnDestroy {
  currentRoute: string = '';
  isCollapsed: boolean = false;
  private subscription: Subscription;

  private readonly navigationItems: NavigationItem[] = [
    { label: 'Dashboard', route: '/dashboard', icon: '📊' },
    { label: 'Monitoring', route: '/monitoring', icon: '📈' },
    { label: 'Recovery', route: '/recovery', icon: '🔧' },
    { label: 'Settings', route: '/settings', icon: '⚙️' }
  ];

  constructor(private router: Router) {
    this.subscription = this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.currentRoute = event.urlAfterRedirects;
    });
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  toggleSidebar(): void {
    this.isCollapsed = !this.isCollapsed;
  }

  isActive(route: string): boolean {
    return this.currentRoute === route || this.currentRoute.startsWith(route + '/');
  }

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  getNavigationItems(): NavigationItem[] {
    return this.navigationItems;
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
      this.isCollapsed = true;
    }
  }
}
