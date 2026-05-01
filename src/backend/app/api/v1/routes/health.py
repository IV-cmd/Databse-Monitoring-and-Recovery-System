from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import ssl
from contextlib import asynccontextmanager

from app.models.schemas import HealthResponse, DetailedHealthResponse
from app.services.database_service import DatabaseService
from app.utils.logger import get_logger
from app.core.config import settings
import httpx
import asyncpg
import psutil

router = APIRouter()
logger = get_logger(__name__)


# PostgreSQL authentication configuration
class PostgreSQLAuthConfig:
    def __init__(self):
        self.ssl_context = self._create_ssl_context()
        self.connection_timeout = settings.DB_CONNECTION_TIMEOUT
        self.command_timeout = settings.DB_COMMAND_TIMEOUT
        self.max_connections = settings.DB_MAX_CONNECTIONS
        self.min_connections = settings.DB_MIN_CONNECTIONS
    
    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context for secure database connections."""
        if not settings.DB_SSL_ENABLED:
            return None
        
        ssl_context = ssl.create_default_context()
        
        if settings.DB_SSL_CERT_FILE:
            ssl_context.load_cert_chain(
                settings.DB_SSL_CERT_FILE,
                keyfile=settings.DB_SSL_KEY_FILE
            )
        
        if settings.DB_SSL_CA_FILE:
            ssl_context.load_verify_locations(settings.DB_SSL_CA_FILE)
        
        if settings.DB_SSL_VERIFY == "disable":
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        elif settings.DB_SSL_VERIFY == "prefer":
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_OPTIONAL
        
        return ssl_context
    
    def get_connection_params(self, is_replica: bool = False) -> Dict[str, Any]:
        """Get secure connection parameters."""
        url = settings.REPLICA_URL if is_replica else settings.DATABASE_URL
        
        params = {
            "timeout": self.connection_timeout,
            "command_timeout": self.command_timeout,
            "server_settings": {
                "application_name": "health_check",
                "jit": "off"  # Disable JIT for health checks
            }
        }
        
        if self.ssl_context:
            params["ssl"] = self.ssl_context
        
        return params, url


# Global authentication configuration
auth_config = PostgreSQLAuthConfig()


@asynccontextmanager
async def get_authenticated_connection(is_replica: bool = False):
    """Context manager for authenticated database connections."""
    params, url = auth_config.get_connection_params(is_replica)
    
    conn = None
    try:
        conn = await asyncpg.connect(url, **params)
        yield conn
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"PostgreSQL connection failed ({'replica' if is_replica else 'primary'}): {e}")
        raise
    except asyncpg.PostgresAuthenticationError as e:
        logger.error(f"PostgreSQL authentication failed ({'replica' if is_replica else 'primary'}): {e}")
        raise HTTPException(status_code=401, detail="Database authentication failed")
    except Exception as e:
        logger.error(f"Unexpected database error ({'replica' if is_replica else 'primary'}): {e}")
        raise
    finally:
        if conn:
            await conn.close()


async def get_database_service() -> DatabaseService:
    """
    Dependency to get database service instance.
    """
    return DatabaseService(
        primary_url=settings.DATABASE_URL,
        replica_url=settings.REPLICA_URL
    )

@router.get("/", response_model=HealthResponse)
async def health_check(service: DatabaseService = Depends(get_database_service)):
    """
    Basic health check endpoint.
    """
    try:
        health = await service.health_check()
        
        return HealthResponse(
            status=health["overall"],
            message=f"Service is {health['overall']}",
            components=health
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(service: DatabaseService = Depends(get_database_service)):
    """
    Detailed health check endpoint.
    """
    try:
        # Get database health
        health = await service.health_check()
        
        # Get detailed status
        status = await service.get_status()
        
        # Get system metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": list(psutil.getloadavg()),
            "uptime": psutil.boot_time()
        }
        
        # Check external services
        external_services = {}
        
        # Check Prometheus
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://prometheus:9090/-/healthy", timeout=2)
                external_services["prometheus"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            external_services["prometheus"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Grafana
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://grafana:3000/api/health", timeout=2)
                external_services["grafana"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            external_services["grafana"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return DetailedHealthResponse(
            status=health["overall"],
            message=f"Detailed health check completed",
            components=health,
            database=status.get("primary", {}),
            system=system_metrics,
            external_services=external_services,
            monitoring={
                "status": "running",
                "last_check": health["timestamp"]
            },
            recovery={
                "status": "ready",
                "auto_recovery_enabled": True
            },
            metrics={
                "status": "collecting",
                "last_collection": health["timestamp"]
            }
        )
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.post("/check", response_model=HealthResponse)
async def force_health_check(service: DatabaseService = Depends(get_database_service)):
    """
    Force an immediate health check.
    """
    try:
        logger.info("Forcing health check...")
        health = await service.health_check()
        
        return HealthResponse(
            status=health["overall"],
            message="Forced health check completed",
            components=health
        )
    except Exception as e:
        logger.error(f"Forced health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")


@router.get("/dependencies")
async def check_dependencies():
    """
    Check health of all external dependencies with secure authentication.
    """
    dependencies = {}
    
    # Check PostgreSQL Primary with authentication
    try:
        async with get_authenticated_connection(is_replica=False) as conn:
            await conn.execute("SELECT 1")
            # Get connection info for detailed health
            version = await conn.fetchval("SELECT version()")
            connections = await conn.fetchval("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            
            dependencies["postgresql_primary"] = {
                "status": "healthy",
                "version": version.split(",")[0],
                "active_connections": connections,
                "ssl_enabled": settings.DB_SSL_ENABLED,
                "authentication": "secure"
            }
    except HTTPException:
        raise
    except asyncpg.PostgresConnectionError as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": "Connection failed", "details": str(e)}
    except asyncpg.PostgresAuthenticationError as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": "Authentication failed", "details": str(e)}
    except Exception as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": "Unknown error", "details": str(e)}
    
    # Check PostgreSQL Replica with authentication
    try:
        async with get_authenticated_connection(is_replica=True) as conn:
            await conn.execute("SELECT 1")
            # Get replication lag info
            try:
                lag = await conn.fetchval("SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))")
                replication_lag = float(lag) if lag else 0
            except:
                replication_lag = None
            
            dependencies["postgresql_replica"] = {
                "status": "healthy",
                "replication_lag_seconds": replication_lag,
                "ssl_enabled": settings.DB_SSL_ENABLED,
                "authentication": "secure"
            }
    except HTTPException:
        raise
    except asyncpg.PostgresConnectionError as e:
        dependencies["postgresql_replica"] = {"status": "unhealthy", "error": "Connection failed", "details": str(e)}
    except asyncpg.PostgresAuthenticationError as e:
        dependencies["postgresql_replica"] = {"status": "unhealthy", "error": "Authentication failed", "details": str(e)}
    except Exception as e:
        dependencies["postgresql_replica"] = {"status": "unhealthy", "error": "Unknown error", "details": str(e)}
    
    # Check Prometheus with authentication
    try:
        headers = {}
        if settings.PROMETHEUS_USERNAME and settings.PROMETHEUS_PASSWORD:
            import base64
            credentials = base64.b64encode(f"{settings.PROMETHEUS_USERNAME}:{settings.PROMETHEUS_PASSWORD}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{settings.PROMETHEUS_URL}/-/healthy", 
                headers=headers,
                timeout=5
            )
            dependencies["prometheus"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "authentication": "enabled" if headers else "disabled"
            }
    except httpx.HTTPStatusError as e:
        dependencies["prometheus"] = {"status": "unhealthy", "error": "HTTP error", "details": f"Status: {e.response.status_code}"}
    except httpx.RequestError as e:
        dependencies["prometheus"] = {"status": "unhealthy", "error": "Connection failed", "details": str(e)}
    except Exception as e:
        dependencies["prometheus"] = {"status": "unhealthy", "error": "Unknown error", "details": str(e)}
    
    # Check Grafana with authentication
    try:
        headers = {}
        if settings.GRAFANA_API_KEY:
            headers["Authorization"] = f"Bearer {settings.GRAFANA_API_KEY}"
        
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{settings.GRAFANA_URL}/api/health", 
                headers=headers,
                timeout=5
            )
            dependencies["grafana"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "authentication": "enabled" if headers else "disabled"
            }
    except httpx.HTTPStatusError as e:
        dependencies["grafana"] = {"status": "unhealthy", "error": "HTTP error", "details": f"Status: {e.response.status_code}"}
    except httpx.RequestError as e:
        dependencies["grafana"] = {"status": "unhealthy", "error": "Connection failed", "details": str(e)}
    except Exception as e:
        dependencies["grafana"] = {"status": "unhealthy", "error": "Unknown error", "details": str(e)}
    
    # Add authentication summary
    dependencies["authentication_summary"] = {
        "postgresql_ssl_enabled": settings.DB_SSL_ENABLED,
        "postgresql_ssl_verify": settings.DB_SSL_VERIFY,
        "prometheus_auth_enabled": bool(settings.PROMETHEUS_USERNAME and settings.PROMETHEUS_PASSWORD),
        "grafana_auth_enabled": bool(settings.GRAFANA_API_KEY)
    }
    
    return dependencies
