import { Component, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { Subscription } from 'rxjs';

export interface NavigationItem {
  label: string;
  route: string;
  icon: string;
}

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnDestroy {
  currentRoute: string = '';
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

  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  isActive(route: string): boolean {
    return this.currentRoute === route || this.currentRoute.startsWith(route + '/');
  }

  getNavigationItems(): NavigationItem[] {
    return this.navigationItems;
  }
}
