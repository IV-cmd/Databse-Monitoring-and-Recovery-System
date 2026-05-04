"""
Simple Database Service
Clean, production-grade database operations.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from ..repositories.database_repo import DatabaseRepository

class DatabaseService:
    """Simple database service for monitoring operations."""
    
    def __init__(self, db_manager: DatabaseRepository):
        self.db_repo = db_manager
    
    async def get_db_status(self) -> Dict[str, Any]:
        """Get current database status and metrics."""
        return await self.db_repo.get_database_status()
    
    async def get_table_sizes(self) -> List[Dict[str, Any]]:
        """Get table sizes from database."""
        return await self.db_repo.get_table_sizes()
