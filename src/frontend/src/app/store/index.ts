// Simple Store Implementation without external dependencies

import { Injectable } from '@angular/core';

// Import action constants
import {
  SETTINGS_LOAD,
  SETTINGS_LOAD_SUCCESS,
  SETTINGS_LOAD_FAILURE,
  SETTINGS_UPDATE,
  SETTINGS_UPDATE_SUCCESS,
  SETTINGS_UPDATE_FAILURE,
  SETTINGS_RESET
} from './actions/settings.actions';

// Root State Interface
export interface AppState {
  settings: {
    database: any;
    monitoring: any;
    system: any;
    notifications: any;
    loading: boolean;
    error: string | null | undefined;
  };
}

// Base Action Interface
export interface Action {
  type: string;
  payload?: any;
  error?: string;
  meta?: any;
}

// Store Service
@Injectable({
  providedIn: 'root'
})
export class Store {
  private state: AppState = {
    settings: {
      database: null,
      monitoring: null,
      system: null,
      notifications: null,
      loading: false,
      error: null
    }
  };

  getState(): AppState {
    return this.state;
  }

  dispatch(action: Action): void {
    this.state = this.reducer(this.state, action);
  }

  // Simple reducer implementation
  private reducer(state: AppState, action: Action): AppState {
    switch (action.type) {
      case SETTINGS_LOAD:
        return {
          ...state,
          settings: { ...state.settings, loading: true, error: null }
        };

      case SETTINGS_LOAD_SUCCESS:
        return {
          ...state,
          settings: { ...state.settings, ...action.payload, loading: false, error: null }
        };

      case SETTINGS_LOAD_FAILURE:
        return {
          ...state,
          settings: { ...state.settings, loading: false, error: action.error }
        };

      case SETTINGS_UPDATE:
        return {
          ...state,
          settings: { ...state.settings, ...action.payload }
        };

      case SETTINGS_UPDATE_SUCCESS:
        return {
          ...state,
          settings: { ...state.settings, ...action.payload }
        };

      case SETTINGS_UPDATE_FAILURE:
        return {
          ...state,
          settings: { ...state.settings, error: action.error }
        };

      case SETTINGS_RESET:
        return {
          ...state,
          settings: { database: null, monitoring: null, system: null, notifications: null, loading: false, error: null }
        };

      default:
        return state;
    }
  }

  // Selectors
  selectSettings = (state: AppState) => state.settings;
  selectDatabase = (state: AppState) => state.settings?.database;
  selectMonitoring = (state: AppState) => state.settings?.monitoring;
  selectSystem = (state: AppState) => state.settings?.system;
  selectNotifications = (state: AppState) => state.settings?.notifications;
  selectSettingsLoading = (state: AppState) => state.settings?.loading;
  selectSettingsError = (state: AppState) => state.settings?.error;

  // Generic select method for reactive usage
  select<T>(selector: (state: AppState) => T): T {
    return selector(this.state);
  }
}
