import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json

from .database import DatabaseManager
from .metrics import MetricsCollector
from .config import settings

logger = logging.getLogger(__name__)


class RecoveryManager:
    """Manages database recovery operations and alerting."""
    
    def __init__(self, db_manager: DatabaseManager, metrics_collector: MetricsCollector):
        if not db_manager:
            raise ValueError("Database manager is required")
        if not metrics_collector:
            raise ValueError("Metrics collector is required")
            
        self.db_manager = db_manager
        self.metrics_collector = metrics_collector
        self.recovery_attempts = {}
        self.recovery_lock = asyncio.Lock()
    
    async def handle_failure(self, db_type: str) -> bool:
        """Handle database failure with recovery attempts."""
        if not db_type or db_type not in ['primary', 'replica']:
            logger.warning(f"Invalid database type: {db_type}, using 'primary'")
            db_type = 'primary'
        
        async with self.recovery_lock:
            try:
                # Check recovery attempts
                attempts = self.recovery_attempts.get(db_type, 0)
                if attempts >= settings.MAX_RECOVERY_ATTEMPTS:
                    logger.error(f"Max recovery attempts reached for {db_type} database")
                    return False
                
                # Increment attempts
                self.recovery_attempts[db_type] = attempts + 1
                
                # Log recovery attempt
                await self._log_recovery_action(db_type, "restart_attempt", f"Attempt {attempts + 1}")
                
                # Attempt restart
                success = await self._attempt_restart(db_type)
                
                if success:
                    # Reset attempts on success
                    self.recovery_attempts[db_type] = 0
                    await self._log_recovery_action(db_type, "restart_success", "Database restarted successfully")
                    self.metrics_collector.increment_recovery_counter()
                    return True
                else:
                    await self._log_recovery_action(db_type, "restart_failed", "Database restart failed")
                    return False
                
            except Exception as e:
                logger.error(f"Error during recovery for {db_type}: {e}")
                await self._log_recovery_action(db_type, "recovery_error", str(e))
                return False
    
    async def _attempt_restart(self, db_type: str) -> bool:
        """Attempt to restart database."""
        if db_type not in ['primary', 'replica']:
            logger.warning(f"Invalid database type: {db_type}, using 'primary'")
            db_type = 'primary'
        
        try:
            logger.info(f"Attempting to restart {db_type} database")
            
            # In a real environment, this would interface with Docker/systemd
            # For now, we simulate the restart process
            is_primary = (db_type == 'primary')
            
            # Attempt restart
            success = await self.db_manager.restart_database(is_primary)
            
            if success:
                logger.info(f"Successfully restarted {db_type} database")
                return True
            else:
                logger.warning(f"Failed to restart {db_type} database")
                return False
                
        except Exception as e:
            logger.error(f"Error during restart attempt: {e}")
            return False
    
    async def _log_recovery_action(self, db_type: str, action: str, details: str):
        """Log recovery action to database."""
        if not action or not isinstance(action, str):
            logger.warning(f"Invalid action: {action}")
            return
        
        if not details or not isinstance(details, str):
            logger.warning(f"Invalid details: {details}")
            return
        
        try:
            query = """
                INSERT INTO recovery_log (action_type, status, details)
                VALUES ($1, $2, $3)
            """
            await self.db_manager.execute_primary(query, action, db_type, details)
            
        except Exception as e:
            logger.error(f"Failed to log recovery action: {e}")
    
    async def send_alert(self, alert_type: str, message: str):
        """Send alert notification."""
        if not alert_type or not isinstance(alert_type, str):
            logger.warning(f"Invalid alert type: {alert_type}")
            return
        
        if not message or not isinstance(message, str):
            logger.warning(f"Invalid alert message: {message}")
            return
        
        try:
            # Log alert (API layer handles notifications)
            logger.warning(f"Alert sent: [{alert_type}] {message}")
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def get_recovery_history(self, limit: int = 50) -> list:
        """Get recovery action history."""
        if not isinstance(limit, int) or limit < 1:
            logger.warning(f"Invalid limit: {limit}, using default 50")
            limit = 50
        if limit > 1000:
            logger.warning(f"Limit too high: {limit}, capping at 1000")
            limit = 1000
        
        try:
            query = """
                SELECT action_type, status, details, timestamp
                FROM recovery_log
                ORDER BY timestamp DESC
                LIMIT $1
            """
            return await self.db_manager.fetch_primary(query, limit)
            
        except Exception as e:
            logger.error(f"Failed to get recovery history: {e}")
            return []
    
    async def reset_recovery_attempts(self, db_type: str):
        """Reset recovery attempts counter."""
        if not db_type or not isinstance(db_type, str):
            logger.warning(f"Invalid database type: {db_type}")
            return
        
        if db_type in self.recovery_attempts:
            self.recovery_attempts[db_type] = 0
            logger.info(f"Reset recovery attempts for {db_type} database")
        else:
            logger.debug(f"No recovery attempts found for {db_type} database")
    
    async def get_recovery_status(self) -> Dict[str, Any]:
        """Get current recovery status."""
        try:
            return {
                "recovery_attempts": self.recovery_attempts,
                "auto_recovery_enabled": settings.AUTO_RECOVERY_ENABLED,
                "max_recovery_attempts": settings.MAX_RECOVERY_ATTEMPTS,
                "recovery_timeout": settings.RECOVERY_TIMEOUT,
                "alert_cooldown": settings.ALERT_COOLDOWN,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
