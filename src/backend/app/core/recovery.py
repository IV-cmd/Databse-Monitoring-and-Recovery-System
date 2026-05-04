import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from .database import DatabaseManager
from .metrics import MetricsCollector
from .config import settings

logger = logging.getLogger(__name__)


class RecoveryManager:
    """Simple database recovery manager."""
    
    def __init__(self, db_manager: DatabaseManager, metrics_collector: MetricsCollector):
        self.db_manager = db_manager
        self.metrics_collector = metrics_collector
        self.recovery_attempts = {}
        self.recovery_lock = asyncio.Lock()
    
    async def handle_failure(self, db_type: str) -> bool:
        """Handle database failure with recovery attempts."""
        if db_type not in ['primary', 'replica']:
            db_type = 'primary'
        
        async with self.recovery_lock:
            try:
                attempts = self.recovery_attempts.get(db_type, 0)
                if attempts >= settings.MAX_RECOVERY_ATTEMPTS:
                    logger.error(f"Max recovery attempts reached for {db_type}")
                    return False
                
                self.recovery_attempts[db_type] = attempts + 1
                
                success = await self._attempt_restart(db_type)
                
                if success:
                    self.recovery_attempts[db_type] = 0
                    self.metrics_collector.increment_recovery_counter()
                    logger.info(f"Successfully recovered {db_type} database")
                    return True
                else:
                    logger.warning(f"Failed to recover {db_type} database")
                    return False
                    
            except Exception as e:
                logger.error(f"Error during recovery for {db_type}: {e}")
                return False
    
    async def _attempt_restart(self, db_type: str) -> bool:
        """Attempt to restart database."""
        try:
            is_primary = (db_type == 'primary')
            return await self.db_manager.restart_database(is_primary)
        except Exception as e:
            logger.error(f"Error during restart attempt: {e}")
            return False
    
    async def get_recovery_status(self) -> Dict[str, Any]:
        """Get current recovery status."""
        try:
            return {
                "recovery_attempts": self.recovery_attempts,
                "auto_recovery_enabled": settings.AUTO_RECOVERY_ENABLED,
                "max_recovery_attempts": settings.MAX_RECOVERY_ATTEMPTS,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return {"error": str(e)}
