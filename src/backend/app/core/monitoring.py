"""
Simple Database Monitoring

Clean, simple database monitoring system for Database Monitoring System.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from .database import DatabaseManager
from .recovery import RecoveryManager
from .metrics import MetricsCollector
from .config import settings

logger = logging.getLogger(__name__)


class DatabaseMonitor:
    """Simple database monitoring service."""
    
    def __init__(self, db_manager: DatabaseManager, recovery_manager: RecoveryManager, metrics_collector: MetricsCollector):
        if not db_manager:
            raise ValueError("Database manager is required")
        if not recovery_manager:
            raise ValueError("Recovery manager is required")
        if not metrics_collector:
            raise ValueError("Metrics collector is required")
            
        self.db_manager = db_manager
        self.recovery_manager = recovery_manager
        self.metrics_collector = metrics_collector
        self.is_running = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        self.last_health_check = {}
        self.last_alert_time = {}
    
    async def start(self):
        """Start monitoring service."""
        if self.is_running:
            logger.warning("Monitor service is already running")
            return
        
        self.is_running = True
        logger.info("Starting database monitoring service")
        
        try:
            # Start monitoring tasks
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Database monitoring service started")
        except Exception as e:
            logger.error(f"Failed to start monitoring tasks: {e}")
            self.is_running = False
            await self._cleanup_tasks()
            raise
    
    async def stop(self):
        """Stop monitoring service gracefully."""
        if not self.is_running:
            logger.debug("Monitor service is not running")
            return
        
        self.is_running = False
        logger.info("Stopping database monitoring service")
        
        await self._cleanup_tasks()
        logger.info("Database monitoring service stopped")
    
    async def _cleanup_tasks(self):
        """Clean up monitoring tasks."""
        try:
            # Cancel tasks
            if self.monitor_task:
                self.monitor_task.cancel()
            if self.health_check_task:
                self.health_check_task.cancel()
            
            # Wait for tasks to complete with timeout
            await asyncio.gather(
                self.monitor_task if self.monitor_task else asyncio.sleep(0),
                self.health_check_task if self.health_check_task else asyncio.sleep(0),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error cleaning up tasks: {e}")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Collect metrics
                await self._collect_metrics()
                
                # Check for performance issues
                await self._check_for_issues()
                
                # Sleep until next iteration
                await asyncio.sleep(settings.MONITORING_INTERVAL_SECONDS)
                
            except asyncio.CancelledError:
                logger.debug("Monitor loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)  # Brief delay before retry
    
    async def _health_check_loop(self):
        """Health check loop for quick failure detection."""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
                
            except asyncio.CancelledError:
                logger.debug("Health check loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self):
        """Collect database metrics with error handling."""
        try:
            stats = await self.db_manager.get_database_stats()
            
            if stats:
                # Update metrics with validation
                connections = max(0, stats.get('active_connections', 0))
                size_bytes = max(0, stats.get('database_size_bytes', 0))
                replication_lag = max(0, stats.get('replication_lag_seconds', 0))
                
                self.metrics_collector.update_connections(connections)
                self.metrics_collector.update_database_size(size_bytes)
                self.metrics_collector.update_replication_lag(replication_lag)
                
                # Log metrics
                logger.debug(f"Collected metrics: connections={connections}, size_bytes={size_bytes}, lag={replication_lag}")
            else:
                logger.warning("No database stats available")
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    async def _perform_health_checks(self):
        """Perform health checks on databases."""
        timestamp = datetime.utcnow()
        
        try:
            # Check primary database
            primary_healthy = await self.db_manager.check_connection(is_primary=True)
            self.last_health_check['primary'] = {
                'healthy': primary_healthy,
                'timestamp': timestamp.isoformat()
            }
            
            # Check replica database
            replica_healthy = await self.db_manager.check_connection(is_primary=False)
            self.last_health_check['replica'] = {
                'healthy': replica_healthy,
                'timestamp': timestamp.isoformat()
            }
            
            # Trigger recovery if needed
            if not primary_healthy and settings.AUTO_RECOVERY_ENABLED:
                await self._handle_database_failure('primary')
            
            if not replica_healthy and settings.AUTO_RECOVERY_ENABLED:
                await self._handle_database_failure('replica')
                
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
    
    async def _check_for_issues(self):
        """Check for performance issues using config thresholds."""
        try:
            stats = await self.db_manager.get_database_stats()
            
            if not stats:
                return
            
            # Check connection count
            connections = stats.get('active_connections', 0)
            if connections > settings.MAX_CONNECTIONS:
                await self._trigger_alert('high_connections', f"High connection count: {connections}")
            
            # Check replication lag
            replication_lag = stats.get('replication_lag_seconds', 0)
            if replication_lag > settings.REPLICATION_LAG_THRESHOLD:
                await self._trigger_alert('high_replication_lag', f"High replication lag: {replication_lag}s")
            
            # Check database size using config threshold
            size_bytes = stats.get('database_size_bytes', 0)
            size_gb = size_bytes / (1024**3)
            if size_gb > settings.DATABASE_SIZE_THRESHOLD_GB:
                await self._trigger_alert('high_database_size', f"Database size: {size_gb:.2f}GB")
            
        except Exception as e:
            logger.error(f"Error checking for issues: {e}")
    
    async def _handle_database_failure(self, db_type: str):
        """Handle database failure with proper error handling."""
        if db_type not in ['primary', 'replica']:
            logger.warning(f"Invalid database type: {db_type}, using 'primary'")
            db_type = 'primary'
        
        try:
            logger.warning(f"Database failure detected: {db_type}")
            
            # Trigger recovery
            success = await self.recovery_manager.handle_failure(db_type)
            
            if success:
                await self._trigger_alert('recovery_success', f"Recovery successful for {db_type} database")
                self.metrics_collector.increment_recovery_counter()
            else:
                await self._trigger_alert('recovery_failed', f"Recovery failed for {db_type} database")
                
        except Exception as e:
            logger.error(f"Error handling database failure: {e}")
    
    async def _trigger_alert(self, alert_type: str, message: str):
        """Trigger alert with cooldown and validation."""
        if not alert_type or not isinstance(alert_type, str):
            logger.warning(f"Invalid alert type: {alert_type}, using 'unknown'")
            alert_type = 'unknown'
        
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid alert message: {message}")
            return
        
        try:
            now = datetime.utcnow()
            
            # Check cooldown
            if alert_type in self.last_alert_time:
                time_since_last = now - self.last_alert_time[alert_type]
                if time_since_last.total_seconds() < settings.ALERT_COOLDOWN:
                    logger.debug(f"Alert {alert_type} in cooldown, skipping")
                    return
            
            # Update last alert time
            self.last_alert_time[alert_type] = now
            
            # Log alert and increment counter
            logger.warning(f"ALERT [{alert_type}]: {message}")
            self.metrics_collector.increment_alert_counter(alert_type)
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status with health check counters."""
        try:
            # Increment health check counter
            self.metrics_collector.increment_health_check_counter('healthy')
            
            return {
                "is_running": self.is_running,
                "last_health_check": self.last_health_check,
                "metrics": self.metrics_collector.get_current_metrics(),
                "monitoring_interval": settings.MONITORING_INTERVAL_SECONDS,
                "health_check_interval": settings.HEALTH_CHECK_INTERVAL,
                "auto_recovery_enabled": settings.AUTO_RECOVERY_ENABLED,
                "database_size_threshold_gb": settings.DATABASE_SIZE_THRESHOLD_GB,
                "replication_lag_threshold": settings.REPLICATION_LAG_THRESHOLD,
                "max_connections": settings.MAX_CONNECTIONS,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def force_health_check(self) -> Dict[str, Any]:
        """Force immediate health check."""
        try:
            await self._perform_health_checks()
            return {
                "health_check": self.last_health_check,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error forcing health check: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
