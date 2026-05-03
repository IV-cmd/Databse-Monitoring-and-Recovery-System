"""
Simple Database Connection Manager
Clean, production-grade database connections for monitoring system.
"""

import asyncpg
import ssl
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Global database manager instance
db_manager: Optional['DatabaseManager'] = None

async def get_database() -> 'DatabaseManager':
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
        await db_manager.initialize()
    return db_manager

class DatabaseManager:
    """Simple database connection manager."""
    
    def __init__(self):
        self.primary_pool: Optional[asyncpg.Pool] = None
        self.replica_pool: Optional[asyncpg.Pool] = None
        
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for secure database connections."""
        if not settings.DB_SSL_ENABLED:
            return None
        
        try:
            ssl_context = ssl.create_default_context()
            
            if settings.DB_SSL_VERIFY == "disable":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            elif settings.DB_SSL_VERIFY == "require":
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            if settings.DB_SSL_CERT_FILE:
                ssl_context.load_cert_chain(settings.DB_SSL_CERT_FILE)
            
            if settings.DB_SSL_CA_FILE:
                ssl_context.load_verify_locations(settings.DB_SSL_CA_FILE)
            
            return ssl_context
        except Exception as e:
            logger.error(f"Failed to create SSL context: {e}")
            return None
    
    async def initialize(self):
        """Initialize database connection pools."""
        try:
            ssl_context = self._create_ssl_context()
            
            # Initialize primary connection pool
            self.primary_pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=settings.DB_MIN_CONNECTIONS,
                max_size=settings.DB_MAX_CONNECTIONS,
                command_timeout=settings.DB_COMMAND_TIMEOUT,
                ssl=ssl_context
            )
            
            # Initialize replica connection pool if configured
            if settings.replica_url:
                try:
                    self.replica_pool = await asyncpg.create_pool(
                        settings.replica_url,
                        min_size=settings.DB_MIN_CONNECTIONS,
                        max_size=settings.DB_MAX_CONNECTIONS,
                        command_timeout=settings.DB_COMMAND_TIMEOUT,
                        ssl=ssl_context
                    )
                    logger.info("Replica connection pool initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize replica pool: {e}")
                    self.replica_pool = None
            
            logger.info("Database connection pools initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pools: {e}")
            await self.close()
            raise
    
    async def close(self):
        """Close database connection pools."""
        if self.primary_pool:
            await self.primary_pool.close()
        if self.replica_pool:
            await self.replica_pool.close()
        logger.info("Database connection pools closed")
    
    async def execute_primary(self, query: str, *args) -> Any:
        """Execute query on primary database."""
        if not self.primary_pool:
            raise RuntimeError("Primary database pool not initialized")
        
        async with self.primary_pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_primary(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch results from primary database."""
        if not self.primary_pool:
            raise RuntimeError("Primary database pool not initialized")
        
        async with self.primary_pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_replica(self, query: str, *args) -> List[asyncpg.Record]:
        """Fetch results from replica database with fallback to primary."""
        if self.replica_pool:
            try:
                async with self.replica_pool.acquire() as conn:
                    return await conn.fetch(query, *args)
            except Exception as e:
                logger.warning(f"Replica query failed, falling back to primary: {e}")
        
        # Fallback to primary
        return await self.fetch_primary(query, *args)
    
    async def check_connection(self, is_primary: bool = True) -> bool:
        """Check database connection health."""
        try:
            if is_primary:
                await self.fetch_primary("SELECT 1")
            else:
                await self.fetch_replica("SELECT 1")
            return True
        except Exception as e:
            logger.warning(f"Database connection check failed: {e}")
            return False
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get basic database statistics."""
        try:
            # Get connection stats
            connections = await self.fetch_primary("""
                SELECT count(*) as active_connections
                FROM pg_stat_activity
                WHERE state = 'active'
            """)
            
            # Get database size
            size = await self.fetch_primary("""
                SELECT pg_database_size(current_database()) as size_bytes
            """)
            
            return {
                "active_connections": connections[0]['active_connections'],
                "database_size_bytes": size[0]['size_bytes'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
