"""
Simple Database Monitoring
Clean, production-grade database monitoring system.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .database import DatabaseManager
from .recovery import RecoveryManager
from .metrics import MetricsCollector
from .config import settings

logger = logging.getLogger(__name__)

class DatabaseMonitor:
    """Simple database monitoring service."""
    
    def __init__(self, db_manager: DatabaseManager, recovery_manager: RecoveryManager, metrics_collector: MetricsCollector):
        self.db_manager = db_manager
        self.recovery_manager = recovery_manager
        self.metrics_collector = metrics_collector
        self.is_running = False
        self.monitor_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start monitoring service."""
        if self.is_running:
            logger.warning("Monitor service is already running")
            return
        
        self.is_running = True
        logger.info("Starting database monitoring service")
        
        self.monitor_task = asyncio.create_task(self._monitor_loop())
    
    async def stop(self):
        """Stop monitoring service."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.monitor_task:
            self.monitor_task.cancel()
        
        logger.info("Database monitoring service stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                await self._collect_metrics()
                await self._check_for_issues()
                await asyncio.sleep(settings.MONITORING_INTERVAL_SECONDS)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                await asyncio.sleep(5)
    
    async def _collect_metrics(self):
        """Collect database metrics."""
        try:
            stats = await self.db_manager.get_database_stats()
            if stats:
                self.metrics_collector.update_connections(stats.get('active_connections', 0))
                self.metrics_collector.update_database_size(stats.get('database_size_bytes', 0))
                self.metrics_collector.update_replication_lag(stats.get('replication_lag_seconds', 0))
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    async def _check_for_issues(self):
        """Check for performance issues."""
        try:
            stats = await self.db_manager.get_database_stats()
            if not stats:
                return
            
            # Check connection count
            connections = stats.get('active_connections', 0)
            if connections > settings.MAX_CONNECTIONS:
                logger.warning(f"High connection count: {connections}")
            
            # Check replication lag
            replication_lag = stats.get('replication_lag_seconds', 0)
            if replication_lag > settings.REPLICATION_LAG_THRESHOLD:
                logger.warning(f"High replication lag: {replication_lag}s")
            
        except Exception as e:
            logger.error(f"Error checking for issues: {e}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        try:
            return {
                "is_running": self.is_running,
                "monitoring_interval": settings.MONITORING_INTERVAL_SECONDS,
                "auto_recovery_enabled": settings.AUTO_RECOVERY_ENABLED,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {"error": str(e)}
