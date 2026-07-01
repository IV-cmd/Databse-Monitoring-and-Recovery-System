"""
Simple Database Service
Clean, production-grade database operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from ..repositories.database_repo import DatabaseRepository

class DatabaseService:
    """Simple database service for monitoring operations."""
    
    def __init__(self, db_manager: DatabaseRepository):
        self.db_repo = db_manager
    
    async def get_db_status(self) -> Dict[str, Any]:
        """Get current database status and metrics."""
        return await self.db_repo.get_database_status()

    async def get_database_status(self) -> Dict[str, Any]:
        """Alias for get_db_status used by routes."""
        try:
            return await self.db_repo.get_database_status()
        except Exception as e:
            return {
                "status": "unavailable",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "connections": {"total": 0, "active": 0, "idle": 0},
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0,
            }

    async def health_check(self) -> Dict[str, Any]:
        """Check database health, returns gracefully even if DB is down."""
        try:
            status = await self.db_repo.get_database_status()
            return {
                "overall": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": status,
            }
        except Exception as e:
            return {
                "overall": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get detailed service status."""
        try:
            db = await self.db_repo.get_database_status()
            return {"primary": db}
        except Exception as e:
            return {"primary": {"status": "unavailable", "error": str(e)}}

    async def get_table_sizes(self) -> List[Dict[str, Any]]:
        """Get table sizes from database."""
        return await self.db_repo.get_table_sizes()
