import { Action } from '../actions/settings.actions';

// Import action constants
import {
  SETTINGS_LOAD,
  SETTINGS_LOAD_SUCCESS,
  SETTINGS_LOAD_FAILURE,
  SETTINGS_UPDATE,
  SETTINGS_UPDATE_SUCCESS,
  SETTINGS_UPDATE_FAILURE,
  SETTINGS_RESET,
  DATABASE_SETTINGS_UPDATE,
  DATABASE_SETTINGS_UPDATE_SUCCESS,
  DATABASE_SETTINGS_UPDATE_FAILURE,
  DATABASE_SETTINGS_TEST_CONNECTION,
  DATABASE_SETTINGS_TEST_CONNECTION_SUCCESS,
  DATABASE_SETTINGS_TEST_CONNECTION_FAILURE,
  MONITORING_SETTINGS_UPDATE,
  MONITORING_SETTINGS_UPDATE_SUCCESS,
  MONITORING_SETTINGS_UPDATE_FAILURE,
  MONITORING_SETTINGS_TEST_ALERTS,
  SYSTEM_SETTINGS_UPDATE,
  SYSTEM_SETTINGS_UPDATE_SUCCESS,
  SYSTEM_SETTINGS_UPDATE_FAILURE,
  SYSTEM_SETTINGS_GENERATE_SECRET,
  NOTIFICATION_SETTINGS_UPDATE,
  NOTIFICATION_SETTINGS_UPDATE_SUCCESS,
  NOTIFICATION_SETTINGS_UPDATE_FAILURE,
  NOTIFICATION_SETTINGS_TEST_EMAIL,
  NOTIFICATION_SETTINGS_TEST_SLACK
} from '../actions/settings.actions';

// State Interface
export interface SettingsState {
  database: any;
  monitoring: any;
  system: any;
  notifications: any;
  loading: boolean;
  error: string | null | undefined;
}

// Initial State
const initialState: SettingsState = {
  database: null,
  monitoring: null,
  system: null,
  notifications: null,
  loading: false,
  error: null
};

// Reducer Function
export function settingsReducer(
  state: SettingsState = initialState,
  action: Action
): SettingsState {
  switch (action.type) {
    case SETTINGS_LOAD:
      return {
        ...state,
        loading: true,
        error: null
      };

    case SETTINGS_LOAD_SUCCESS:
      return {
        ...state,
        loading: false,
        ...action.payload,
        error: null
      };

    case SETTINGS_LOAD_FAILURE:
      return {
        ...state,
        loading: false,
        error: action.error
      };

    case SETTINGS_UPDATE:
    case DATABASE_SETTINGS_UPDATE:
      return {
        ...state,
        database: action.payload
      };

    case DATABASE_SETTINGS_UPDATE_SUCCESS:
      return {
        ...state,
        database: action.payload
      };

    case DATABASE_SETTINGS_UPDATE_FAILURE:
      return {
        ...state,
        error: action.error
      };

    case MONITORING_SETTINGS_UPDATE:
      return {
        ...state,
        monitoring: action.payload
      };

    case MONITORING_SETTINGS_UPDATE_SUCCESS:
      return {
        ...state,
        monitoring: action.payload
      };

    case MONITORING_SETTINGS_UPDATE_FAILURE:
      return {
        ...state,
        error: action.error
      };

    case SYSTEM_SETTINGS_UPDATE:
      return {
        ...state,
        system: action.payload
      };

    case SYSTEM_SETTINGS_UPDATE_SUCCESS:
      return {
        ...state,
        system: action.payload
      };

    case SYSTEM_SETTINGS_UPDATE_FAILURE:
      return {
        ...state,
        error: action.error
      };

    case NOTIFICATION_SETTINGS_UPDATE:
      return {
        ...state,
        notifications: action.payload
      };

    case NOTIFICATION_SETTINGS_UPDATE_SUCCESS:
      return {
        ...state,
        notifications: action.payload
      };

    case NOTIFICATION_SETTINGS_UPDATE_FAILURE:
      return {
        ...state,
        error: action.error
      };

    case SETTINGS_RESET:
      return {
        database: null,
        monitoring: null,
        system: null,
        notifications: null,
        loading: false,
        error: null
      };

    default:
      return state;
  }
}
