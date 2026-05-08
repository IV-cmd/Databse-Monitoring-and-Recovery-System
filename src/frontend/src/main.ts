import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { enableProdMode } from '@angular/core';

// Enable production mode if not in development
if (typeof process !== 'undefined' && process.env['NODE_ENV'] === 'production') {
  enableProdMode();
}

// Enhanced bootstrap with error handling and logging
console.log('🔧 Starting application bootstrap...');
bootstrapApplication(AppComponent, appConfig)
  .then(() => {
    console.log('🚀 Database Monitoring System started successfully');
    console.log('🌐 Checking router configuration...');
    
    // Remove loading state
    const loadingElement = document.querySelector('.app-loading');
    if (loadingElement) {
      console.log('🧹 Removing loading element');
      loadingElement.remove();
    } else {
      console.log('ℹ️ No loading element found');
    }
  })
  .catch((err: any) => {
    console.error('❌ Failed to bootstrap application:', err);
    
    // Show error message to user
    const appRoot = document.querySelector('app-root');
    if (appRoot) {
      appRoot.innerHTML = `
        <div style="
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          color: #ef4444;
          text-align: center;
          padding: 2rem;
        ">
          <h1>Application Error</h1>
          <p>Failed to load the Database Monitoring System.</p>
          <p style="font-size: 0.9rem; color: #6b7280;">Please refresh the page or contact support.</p>
          <details style="margin-top: 1rem; font-size: 0.8rem; color: #374151;">
            <summary>Error Details</summary>
            <pre style="text-align: left; margin-top: 0.5rem; padding: 1rem; background: #f3f4f6; border-radius: 4px; overflow: auto;">${err}</pre>
          </details>
        </div>
      `;
    }
  });
