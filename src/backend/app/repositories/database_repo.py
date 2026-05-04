"""
Simple Database Repository

Clean, production-grade database operations and metrics.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncpg

class DatabaseRepository:
    """Simple database repository for monitoring operations."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    async def get_database_status(self) -> Dict[str, Any]:
        """Get current database status and metrics."""
        connections = await self.db_manager.fetch_primary("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections,
                count(*) FILTER (WHERE state = 'idle') as idle_connections
            FROM pg_stat_activity
        """)
        
        size = await self.db_manager.fetch_primary("""
            SELECT pg_database_size(current_database()) as size_bytes
        """)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "connections": {
                "total": connections[0]['total_connections'],
                "active": connections[0]['active_connections'],
                "idle": connections[0]['idle_connections']
            },
            "database_size_bytes": size[0]['size_bytes']
        }
    
    async def get_table_sizes(self) -> List[Dict[str, Any]]:
        """Get sizes of all tables in the database."""
        rows = await self.db_manager.fetch_primary("""
            SELECT 
                schemaname,
                tablename,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
            ORDER BY size_bytes DESC
        """)
        
        return [
            {
                "schema": row['schemaname'],
                "table": row['tablename'],
                "size_bytes": row['size_bytes']
            }
            for row in rows
        ]
