from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
import ssl
from contextlib import asynccontextmanager

from app.models.schemas import HealthResponse, DetailedHealthResponse
from app.dependencies import get_database_service
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
        self.connection_timeout = settings.DB_COMMAND_TIMEOUT
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
        url = settings.replica_url if is_replica else settings.database_url
        
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
    except asyncpg.InvalidPasswordError as e:
        logger.error(f"PostgreSQL authentication failed ({'replica' if is_replica else 'primary'}): {e}")
        raise HTTPException(status_code=401, detail="Database authentication failed")
    except Exception as e:
        logger.error(f"Unexpected database error ({'replica' if is_replica else 'primary'}): {e}")
        raise
    finally:
        if conn:
            await conn.close()

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
            version = await conn.fetchval("SELECT version()")
            active_connections = await conn.fetchval(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            total_connections = await conn.fetchval(
                "SELECT count(*) FROM pg_stat_activity"
            )
            db_size = await conn.fetchval(
                "SELECT pg_database_size(current_database())"
            )

            dependencies["postgresql_primary"] = {
                "status": "healthy",
                "version": version.split(",")[0],
                "active_connections": active_connections,
                "total_connections": total_connections,
                "database_size_bytes": db_size,
                "ssl_enabled": settings.DB_SSL_ENABLED,
                "authentication": "secure"
            }
    except HTTPException:
        raise
    except asyncpg.PostgresConnectionError as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": "Connection failed", "details": str(e)}
    except asyncpg.InvalidPasswordError as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": "Authentication failed", "details": str(e)}
    except Exception as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": "Unknown error", "details": str(e)}
    
    # Check PostgreSQL Replica with authentication
    if not settings.replica_url:
        dependencies["postgresql_replica"] = {"status": "not_configured", "message": "No REPLICA_URL set in environment"}
    else:
        try:
            async with get_authenticated_connection(is_replica=True) as conn:
                await conn.execute("SELECT 1")
                version = await conn.fetchval("SELECT version()")
                active_connections = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
                )
                total_connections = await conn.fetchval(
                    "SELECT count(*) FROM pg_stat_activity"
                )
                db_size = await conn.fetchval(
                    "SELECT pg_database_size(current_database())"
                )
                try:
                    lag = await conn.fetchval(
                        "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))"
                    )
                    replication_lag = float(lag) if lag else 0
                except Exception:
                    replication_lag = None
                dependencies["postgresql_replica"] = {
                    "status": "healthy",
                    "version": version.split(",")[0] if version else None,
                    "active_connections": active_connections,
                    "total_connections": total_connections,
                    "database_size_bytes": db_size,
                    "replication_lag_seconds": replication_lag,
                    "ssl_enabled": settings.DB_SSL_ENABLED,
                    "authentication": "secure"
                }
        except HTTPException:
            raise
        except asyncpg.PostgresConnectionError as e:
            dependencies["postgresql_replica"] = {"status": "unhealthy", "error": "Connection failed", "details": str(e)}
        except asyncpg.InvalidPasswordError as e:
            dependencies["postgresql_replica"] = {"status": "unhealthy", "error": "Authentication failed", "details": str(e)}
        except Exception as e:
            dependencies["postgresql_replica"] = {"status": "unhealthy", "error": "Unknown error", "details": str(e)}
    
    # Check Prometheus
    prometheus_url = getattr(settings, 'PROMETHEUS_URL', 'http://prometheus:9090')
    prometheus_user = getattr(settings, 'PROMETHEUS_USERNAME', None)
    prometheus_pass = getattr(settings, 'PROMETHEUS_PASSWORD', None)
    try:
        headers = {}
        if prometheus_user and prometheus_pass:
            import base64
            credentials = base64.b64encode(f"{prometheus_user}:{prometheus_pass}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{prometheus_url}/-/healthy", headers=headers)
            dependencies["prometheus"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
            }
    except Exception as e:
        dependencies["prometheus"] = {"status": "not_reachable", "error": str(e)}

    # Check Grafana
    grafana_url = getattr(settings, 'GRAFANA_URL', 'http://grafana:3000')
    grafana_key = getattr(settings, 'GRAFANA_API_KEY', None)
    try:
        headers = {}
        if grafana_key:
            headers["Authorization"] = f"Bearer {grafana_key}"
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(f"{grafana_url}/api/health", headers=headers)
            dependencies["grafana"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
            }
    except Exception as e:
        dependencies["grafana"] = {"status": "not_reachable", "error": str(e)}

    # Check Kibana
    kibana_url = getattr(settings, 'KIBANA_URL', 'http://localhost:5602')
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{kibana_url}/api/status")
            is_healthy = response.status_code == 200
            body = response.json()
            overall = body.get("status", {}).get("overall", {}).get("level", "unknown")
            dependencies["kibana"] = {
                "status": "healthy" if is_healthy and overall != "critical" else "unhealthy",
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "kibana_status": overall,
            }
    except Exception as e:
        dependencies["kibana"] = {"status": "not_reachable", "error": str(e)}

    dependencies["authentication_summary"] = {
        "postgresql_ssl_enabled": settings.DB_SSL_ENABLED,
        "postgresql_ssl_verify": settings.DB_SSL_VERIFY,
    }

    statuses = {k: v.get("status") for k, v in dependencies.items() if isinstance(v, dict) and "status" in v}
    logger.info("dependency health check", extra={"event": "health_check", "statuses": statuses})

    return dependencies
