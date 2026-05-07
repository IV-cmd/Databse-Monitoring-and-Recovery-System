// Base Action Interface
export interface Action {
  type: string;
  payload?: any;
  error?: string;
}

// Settings Action Types
export const SETTINGS_LOAD = '[Settings] Load';
export const SETTINGS_LOAD_SUCCESS = '[Settings] Load Success';
export const SETTINGS_LOAD_FAILURE = '[Settings] Load Failure';
export const SETTINGS_UPDATE = '[Settings] Update';
export const SETTINGS_UPDATE_SUCCESS = '[Settings] Update Success';
export const SETTINGS_UPDATE_FAILURE = '[Settings] Update Failure';
export const SETTINGS_RESET = '[Settings] Reset';

// Database Settings Action Types
export const DATABASE_SETTINGS_UPDATE = '[Database Settings] Update';
export const DATABASE_SETTINGS_UPDATE_SUCCESS = '[Database Settings] Update Success';
export const DATABASE_SETTINGS_UPDATE_FAILURE = '[Database Settings] Update Failure';
export const DATABASE_SETTINGS_TEST_CONNECTION = '[Database Settings] Test Connection';
export const DATABASE_SETTINGS_TEST_CONNECTION_SUCCESS = '[Database Settings] Test Connection Success';
export const DATABASE_SETTINGS_TEST_CONNECTION_FAILURE = '[Database Settings] Test Connection Failure';

// Monitoring Settings Action Types
export const MONITORING_SETTINGS_UPDATE = '[Monitoring Settings] Update';
export const MONITORING_SETTINGS_UPDATE_SUCCESS = '[Monitoring Settings] Update Success';
export const MONITORING_SETTINGS_UPDATE_FAILURE = '[Monitoring Settings] Update Failure';
export const MONITORING_SETTINGS_TEST_ALERTS = '[Monitoring Settings] Test Alerts';

// System Settings Action Types
export const SYSTEM_SETTINGS_UPDATE = '[System Settings] Update';
export const SYSTEM_SETTINGS_UPDATE_SUCCESS = '[System Settings] Update Success';
export const SYSTEM_SETTINGS_UPDATE_FAILURE = '[System Settings] Update Failure';
export const SYSTEM_SETTINGS_GENERATE_SECRET = '[System Settings] Generate Secret';

// Notification Settings Action Types
export const NOTIFICATION_SETTINGS_UPDATE = '[Notification Settings] Update';
export const NOTIFICATION_SETTINGS_UPDATE_SUCCESS = '[Notification Settings] Update Success';
export const NOTIFICATION_SETTINGS_UPDATE_FAILURE = '[Notification Settings] Update Failure';
export const NOTIFICATION_SETTINGS_TEST_EMAIL = '[Notification Settings] Test Email';
export const NOTIFICATION_SETTINGS_TEST_SLACK = '[Notification Settings] Test Slack';

// Action Creators
export const loadSettings = (): Action => ({ type: SETTINGS_LOAD });

export const loadSettingsSuccess = (settings: any): Action => ({ 
  type: SETTINGS_LOAD_SUCCESS, 
  payload: settings 
});

export const loadSettingsFailure = (error: string): Action => ({ 
  type: SETTINGS_LOAD_FAILURE, 
  error 
});

export const updateSettings = (settings: any): Action => ({ 
  type: SETTINGS_UPDATE, 
  payload: settings 
});

export const updateSettingsSuccess = (settings: any): Action => ({ 
  type: SETTINGS_UPDATE_SUCCESS, 
  payload: settings 
});

export const updateSettingsFailure = (error: string): Action => ({ 
  type: SETTINGS_UPDATE_FAILURE, 
  error 
});

export const resetSettings = (): Action => ({ type: SETTINGS_RESET });

// Database Settings Action Creators
export const updateDatabaseSettings = (settings: any): Action => ({ 
  type: DATABASE_SETTINGS_UPDATE, 
  payload: settings 
});

export const updateDatabaseSettingsSuccess = (settings: any): Action => ({ 
  type: DATABASE_SETTINGS_UPDATE_SUCCESS, 
  payload: settings 
});

export const updateDatabaseSettingsFailure = (error: string): Action => ({ 
  type: DATABASE_SETTINGS_UPDATE_FAILURE, 
  error 
});

export const testDatabaseConnection = (): Action => ({ type: DATABASE_SETTINGS_TEST_CONNECTION });

export const testDatabaseConnectionSuccess = (result: boolean): Action => ({ 
  type: DATABASE_SETTINGS_TEST_CONNECTION_SUCCESS, 
  payload: result 
});

export const testDatabaseConnectionFailure = (error: string): Action => ({ 
  type: DATABASE_SETTINGS_TEST_CONNECTION_FAILURE, 
  error 
});

// Monitoring Settings Action Creators
export const updateMonitoringSettings = (settings: any): Action => ({ 
  type: MONITORING_SETTINGS_UPDATE, 
  payload: settings 
});

export const updateMonitoringSettingsSuccess = (settings: any): Action => ({ 
  type: MONITORING_SETTINGS_UPDATE_SUCCESS, 
  payload: settings 
});

export const updateMonitoringSettingsFailure = (error: string): Action => ({ 
  type: MONITORING_SETTINGS_UPDATE_FAILURE, 
  error 
});

export const testMonitoringAlerts = (): Action => ({ type: MONITORING_SETTINGS_TEST_ALERTS });

// System Settings Action Creators
export const updateSystemSettings = (settings: any): Action => ({ 
  type: SYSTEM_SETTINGS_UPDATE, 
  payload: settings 
});

export const updateSystemSettingsSuccess = (settings: any): Action => ({ 
  type: SYSTEM_SETTINGS_UPDATE_SUCCESS, 
  payload: settings 
});

export const updateSystemSettingsFailure = (error: string): Action => ({ 
  type: SYSTEM_SETTINGS_UPDATE_FAILURE, 
  error 
});

export const generateSystemSecret = (): Action => ({ type: SYSTEM_SETTINGS_GENERATE_SECRET });

// Notification Settings Action Creators
export const updateNotificationSettings = (settings: any): Action => ({ 
  type: NOTIFICATION_SETTINGS_UPDATE, 
  payload: settings 
});

export const updateNotificationSettingsSuccess = (settings: any): Action => ({ 
  type: NOTIFICATION_SETTINGS_UPDATE_SUCCESS, 
  payload: settings 
});

export const updateNotificationSettingsFailure = (error: string): Action => ({ 
  type: NOTIFICATION_SETTINGS_UPDATE_FAILURE, 
  error 
});

export const testNotificationEmail = (): Action => ({ type: NOTIFICATION_SETTINGS_TEST_EMAIL });

export const testNotificationSlack = (): Action => ({ type: NOTIFICATION_SETTINGS_TEST_SLACK });
