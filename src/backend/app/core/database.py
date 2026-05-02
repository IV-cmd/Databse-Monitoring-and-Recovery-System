"""
Simple Database Management

Clean, simple database connection manager for the CERN Database Monitoring System.
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
            elif settings.DB_SSL_VERIFY == "prefer":
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_OPTIONAL
            elif settings.DB_SSL_VERIFY == "require":
                ssl_context.check_hostname = True
                ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Load custom certificates if provided
            if settings.DB_SSL_CERT_FILE:
                ssl_context.load_cert_chain(
                    settings.DB_SSL_CERT_FILE,
                    settings.DB_SSL_KEY_FILE
                )
            
            if settings.DB_SSL_CA_FILE:
                ssl_context.load_verify_locations(settings.DB_SSL_CA_FILE)
            
            logger.info("SSL context created successfully")
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
                self.replica_pool = await asyncpg.create_pool(
                    settings.replica_url,
                    min_size=settings.DB_MIN_CONNECTIONS,
                    max_size=settings.DB_MAX_CONNECTIONS,
                    command_timeout=settings.DB_COMMAND_TIMEOUT,
                    ssl=ssl_context
                )
                logger.info("Replica connection pool initialized")
            else:
                logger.info("No replica configured, using primary for all operations")
            
            logger.info("Database connection pools initialized successfully")
            
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
        """Fetch results from replica database."""
        if self.replica_pool:
            async with self.replica_pool.acquire() as conn:
                return await conn.fetch(query, *args)
        else:
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
        """Get database statistics."""
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
            
            # Get replication lag (if replica is available)
            replication_lag = 0
            if self.replica_pool:
                try:
                    lag_result = await self.fetch_replica("""
                        SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) as lag
                    """)
                    replication_lag = lag_result[0]['lag'] if lag_result else 0
                except:
                    pass  # Replica might not be available
            
            return {
                "active_connections": connections[0]['active_connections'],
                "database_size_bytes": size[0]['size_bytes'],
                "replication_lag_seconds": replication_lag,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    async def restart_database(self, is_primary: bool = True) -> bool:
        """Attempt to restart database (simulated)."""
        logger.info(f"Restart request for {'primary' if is_primary else 'replica'} database")
        
        # Simulate restart delay
        import asyncio
        await asyncio.sleep(5)
        
        # Check if database is back online
        return await self.check_connection(is_primary)
