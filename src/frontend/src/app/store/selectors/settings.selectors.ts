// Base Selectors
export const selectSettings = (state: any) => state.settings;
export const selectDatabase = (state: any) => state.settings?.database;
export const selectMonitoring = (state: any) => state.settings?.monitoring;
export const selectSystem = (state: any) => state.settings?.system;
export const selectNotifications = (state: any) => state.settings?.notifications;

// Loading Selectors
export const selectSettingsLoading = (state: any) => state.settings?.loading;
export const selectSettingsError = (state: any) => state.settings?.error;

// Database Selectors
export const selectDatabaseSettings = (state: any) => selectDatabase(state)?.settings;
export const selectDatabaseConnectionStatus = (state: any) => selectDatabase(state)?.connectionStatus;

// Monitoring Selectors
export const selectMonitoringSettings = (state: any) => selectMonitoring(state)?.settings;
export const selectMonitoringAlerts = (state: any) => selectMonitoring(state)?.alerts;
export const selectMonitoringMetrics = (state: any) => selectMonitoring(state)?.metrics;

// System Selectors
export const selectSystemSettings = (state: any) => selectSystem(state)?.settings;
export const selectSystemEnvironment = (state: any) => selectSystem(state)?.environment;
export const selectSystemLogLevel = (state: any) => selectSystem(state)?.logLevel;

// Notification Selectors
export const selectNotificationSettings = (state: any) => selectNotifications(state)?.settings;
export const selectNotificationEmailSettings = (state: any) => selectNotifications(state)?.email;
export const selectNotificationSlackSettings = (state: any) => selectNotifications(state)?.slack;

// Computed Selectors
export const selectSettingsSummary = (state: any) => {
  const settings = selectSettings(state);
  return {
    database: settings?.database ? 'configured' : 'not configured',
    monitoring: settings?.monitoring ? 'configured' : 'not configured',
    system: settings?.system ? 'configured' : 'not configured',
    notifications: settings?.notifications ? 'configured' : 'not configured'
  };
};

export const selectAllSettingsConfigured = (state: any) => {
  const summary = selectSettingsSummary(state);
  return summary.database === 'configured' && 
         summary.monitoring === 'configured' && 
         summary.system === 'configured' && 
         summary.notifications === 'configured';
};
