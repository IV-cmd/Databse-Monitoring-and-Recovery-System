import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { Store } from './store';
import { Subscription, BehaviorSubject } from 'rxjs';
import { AppState } from './store';
import { HeaderComponent } from './shared/components/header/header.component';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { ErrorModalComponent } from './shared/components/error-modal/error-modal.component';
import { LoadingComponent } from './shared/components/loading/loading.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule, 
    RouterOutlet,
    HeaderComponent,
    SidebarComponent,
    ErrorModalComponent,
    LoadingComponent
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'Database Monitoring System';
  
  private stateSubject = new BehaviorSubject<AppState>({} as AppState);
  private storeSubscription!: Subscription;
  
  constructor(private store: Store) {}

  ngOnInit(): void {
    console.log('🚀 AppComponent: Initializing...');
    
    // Initialize store and subscribe to state changes
    this.storeSubscription = this.stateSubject.subscribe((state) => {
      console.log('📊 AppComponent: State changed:', state);
      if (state.settings) {
        console.log('🎨 AppComponent: Applying theme settings:', state.settings);
        this.applyThemeSettings(state.settings);
      }
    });
    
    // Update state from store
    console.log('🔄 AppComponent: Updating state from store...');
    this.updateStateFromStore();
    console.log('✅ AppComponent: Initialization complete');
  }

  ngOnDestroy(): void {
    // Clean up subscriptions
    if (this.storeSubscription) {
      this.storeSubscription.unsubscribe();
    }
  }

  private updateStateFromStore(): void {
    const currentState = this.store.getState();
    this.stateSubject.next(currentState);
  }

  private applyThemeSettings(settings: AppState['settings']): void {
    // Apply theme, language, and other global settings
    if (settings?.system?.theme) {
      document.body.setAttribute('data-theme', settings.system.theme);
    }
    
    if (settings?.system?.language) {
      document.documentElement.lang = settings.system.language;
    }
  }
}
