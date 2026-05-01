"""
Monitoring Routes
This module contains all monitoring related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Header
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
import base64

from app.models.schemas import MonitoringStatusResponse, MonitoringMetricsResponse
from app.services.database_service import DatabaseService
from app.services.metrics_service import MetricsService
from app.repositories.metrics_repo import MetricsRepository
from app.utils.logger import get_logger
from app.core.config import settings
import asyncpg
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest

router = APIRouter()
logger = get_logger(__name__)

async def get_database_service() -> DatabaseService:
    """
    Dependency to get database service instance.
    """
    return DatabaseService(
        primary_url=settings.DATABASE_URL,
        replica_url=settings.REPLICA_URL
    )

# Prometheus metrics definitions
MONITORING_REQUESTS_TOTAL = Counter(
    'monitoring_requests_total',
    'Total number of monitoring requests',
    ['endpoint', 'method']
)

MONITORING_REQUEST_DURATION = Histogram(
    'monitoring_request_duration_seconds',
    'Time spent processing monitoring requests',
    ['endpoint', 'method']
)

DATABASE_CONNECTIONS_ACTIVE = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

SLOW_QUERIES_COUNT = Gauge(
    'slow_queries_count',
    'Number of slow queries detected'
)

MONITORING_STATUS = Gauge(
    'monitoring_status',
    'Monitoring system status (1=healthy, 0=degraded)'
)


# Prometheus client configuration
class PrometheusClient:
    def __init__(self):
        self.base_url = settings.PROMETHEUS_URL
        self.username = settings.PROMETHEUS_USERNAME
        self.password = settings.PROMETHEUS_PASSWORD
        self.timeout = settings.PROMETHEUS_TIMEOUT
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for Prometheus API."""
        if self.username and self.password:
            credentials = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            return {"Authorization": f"Basic {credentials}"}
        return {}
    
    async def query(self, query: str, time: Optional[datetime] = None) -> Dict[str, Any]:
        """Execute PromQL query against Prometheus."""
        params = {"query": query}
        if time:
            params["time"] = time.timestamp()
        
        headers = self.get_auth_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/query",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Prometheus query failed: {e}")
                raise HTTPException(status_code=502, detail="Prometheus service unavailable")
            except httpx.RequestError as e:
                logger.error(f"Prometheus connection error: {e}")
                raise HTTPException(status_code=503, detail="Failed to connect to Prometheus")
    
    async def query_range(
        self, 
        query: str, 
        start: datetime, 
        end: datetime, 
        step: str = "1m"
    ) -> Dict[str, Any]:
        """Execute PromQL range query against Prometheus."""
        params = {
            "query": query,
            "start": start.timestamp(),
            "end": end.timestamp(),
            "step": step
        }
        
        headers = self.get_auth_headers()
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/query_range",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"Prometheus range query failed: {e}")
                raise HTTPException(status_code=502, detail="Prometheus service unavailable")
            except httpx.RequestError as e:
                logger.error(f"Prometheus connection error: {e}")
                raise HTTPException(status_code=503, detail="Failed to connect to Prometheus")


# Global Prometheus client instance
prometheus_client = PrometheusClient()


async def verify_prometheus_auth(authorization: Optional[str] = Header(None)) -> bool:
    """Verify Prometheus authentication token."""
    if not settings.PROMETHEUS_AUTH_REQUIRED:
        return True
    
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Prometheus authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify Bearer token
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove 'Bearer ' prefix
        if token == settings.PROMETHEUS_BEARER_TOKEN:
            return True
    
    raise HTTPException(
        status_code=401,
        detail="Invalid Prometheus authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )

@router.get("/status", response_model=MonitoringStatusResponse)
async def get_monitoring_status(
    service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends()
):
    """
    Get current monitoring status.
    
    Returns:
        Current monitoring system status
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/status", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/status", method="GET").inc()
        
        try:
            status = await service.get_status()
            primary_status = status.get("primary", {})
            
            # Get system metrics using MetricsService
            system_metrics = await metrics_service.collect_all_metrics()
            
            # Determine overall health
            is_healthy = primary_status.get("status") == "healthy"
            monitoring_status = "running" if is_healthy else "degraded"
            
            # Update Prometheus metrics
            MONITORING_STATUS.set(1 if is_healthy else 0)
            
            # Update database connections gauge
            connections = primary_status.get("connections", {})
            active_connections = connections.get("active", 0)
            DATABASE_CONNECTIONS_ACTIVE.set(active_connections)
            
            return MonitoringStatusResponse(
                status=monitoring_status,
                is_monitoring=True,
                last_check=status["timestamp"],
                interval_seconds=settings.MONITORING_INTERVAL_SECONDS,
                metrics={
                    **primary_status,
                    "system": system_metrics
                }
            )
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error in monitoring status: {e}")
            MONITORING_STATUS.set(0)
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in monitoring status: {e}")
            MONITORING_STATUS.set(0)
            raise HTTPException(status_code=500, detail="Internal server error while retrieving monitoring status")

@router.get("/metrics", response_model=MonitoringMetricsResponse)
async def get_current_metrics(
    include_slow_queries: bool = Query(False, description="Include slow queries in response"),
    service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends()
):
    """
    Get current monitoring metrics.
    
    Args:
        include_slow_queries: Whether to include slow queries analysis
        
    Returns:
        Current monitoring metrics
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/metrics", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/metrics", method="GET").inc()
        
        try:
            status = await service.get_status()
            primary_metrics = status.get("primary", {})
            
            # Get system metrics using MetricsService
            system_metrics = await metrics_service.collect_all_metrics()
            
            alerts = []
            
            # Add slow queries if requested
            if include_slow_queries:
                slow_queries = await service.get_slow_queries(
                    limit=settings.SLOW_QUERIES_DEFAULT_LIMIT, 
                    threshold_ms=settings.SLOW_QUERIES_THRESHOLD_MS
                )
                if slow_queries.get("success") and slow_queries["queries"]:
                    slow_query_count = len(slow_queries["queries"])
                    alerts.append({
                        "type": "slow_queries",
                        "severity": "medium",
                        "count": slow_query_count,
                        "details": slow_queries["queries"]
                    })
                    # Update Prometheus metrics
                    SLOW_QUERIES_COUNT.set(slow_query_count)
            
            # Combine metrics
            combined_metrics = {
                **primary_metrics,
                "system": system_metrics
            }
            
            return MonitoringMetricsResponse(
                timestamp=status["timestamp"],
                metrics=combined_metrics,
                alerts=alerts if alerts else None
            )
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error in current metrics: {e}")
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in current metrics: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving metrics")

@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = Query(settings.SLOW_QUERIES_DEFAULT_LIMIT, ge=1, le=100, description="Maximum number of queries to return"),
    threshold_ms: float = Query(settings.SLOW_QUERIES_THRESHOLD_MS, ge=100.0, le=60000.0, description="Minimum execution time threshold"),
    service: DatabaseService = Depends(get_database_service)
):
    """
    Get slow queries from the database.
    
    Args:
        limit: Maximum number of queries to return
        threshold_ms: Minimum execution time to consider "slow"
        
    Returns:
        List of slow queries
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/slow-queries", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/slow-queries", method="GET").inc()
        
        try:
            result = await service.get_slow_queries(limit, threshold_ms)
            
            # Update Prometheus metrics
            if result.get("success") and result["queries"]:
                SLOW_QUERIES_COUNT.set(len(result["queries"]))
            else:
                SLOW_QUERIES_COUNT.set(0)
            
            return result
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error in slow queries: {e}")
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except ValueError as e:
            logger.error(f"Invalid parameters in slow queries: {e}")
            raise HTTPException(status_code=400, detail="Invalid query parameters")
        except Exception as e:
            logger.error(f"Unexpected error in slow queries: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving slow queries")

@router.get("/table-sizes")
async def get_table_sizes(service: DatabaseService = Depends(get_database_service)):
    """
    Get table sizes from the database.
    
    Returns:
        List of tables with their sizes
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/table-sizes", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/table-sizes", method="GET").inc()
        
        try:
            result = await service.get_table_sizes()
            return result
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error in table sizes: {e}")
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in table sizes: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving table sizes")

@router.get("/connections")
async def get_connection_info(service: DatabaseService = Depends(get_database_service)):
    """
    Get database connection information.
    
    Returns:
        Current connection status and information
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/connections", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/connections", method="GET").inc()
        
        try:
            info = await service.get_connection_info()
            
            # Update Prometheus metrics
            if info.get("success") and info["connections"]:
                active_connections = info["connections"].get("active", 0)
                DATABASE_CONNECTIONS_ACTIVE.set(active_connections)
            
            return info
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error in connection info: {e}")
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in connection info: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving connection info")

@router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Get monitoring metrics in Prometheus format.
    
    Returns:
        Monitoring metrics formatted for Prometheus scraping
    """
    try:
        # Generate Prometheus metrics
        metrics_data = generate_latest()
        
        return Response(
            content=metrics_data,
            media_type="text/plain"
        )
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while generating Prometheus metrics")


@router.get("/prometheus/query")
async def prometheus_query(
    query: str = Query(..., description="PromQL query to execute"),
    time: Optional[datetime] = Query(None, description="Query timestamp (optional)"),
    authenticated: bool = Depends(verify_prometheus_auth)
):
    """
    Execute PromQL query against Prometheus.
    
    Args:
        query: PromQL query string
        time: Optional timestamp for query
        
    Returns:
        Prometheus query results
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/prometheus/query", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/prometheus/query", method="GET").inc()
        
        try:
            result = await prometheus_client.query(query, time)
            
            # Validate response format
            if result.get("status") != "success":
                error_type = result.get("errorType", "unknown")
                error_msg = result.get("error", "Unknown PromQL query error")
                logger.error(f"PromQL query error: {error_type} - {error_msg}")
                raise HTTPException(status_code=400, detail=f"PromQL query failed: {error_msg}")
            
            return {
                "status": result["status"],
                "data": result["data"],
                "query": query,
                "time": time.isoformat() if time else "now"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in PromQL query: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while executing PromQL query")


@router.get("/prometheus/query_range")
async def prometheus_query_range(
    query: str = Query(..., description="PromQL query to execute"),
    start: datetime = Query(..., description="Start time for range query"),
    end: datetime = Query(..., description="End time for range query"),
    step: str = Query("1m", description="Query step interval"),
    authenticated: bool = Depends(verify_prometheus_auth)
):
    """
    Execute PromQL range query against Prometheus.
    
    Args:
        query: PromQL query string
        start: Start time for range
        end: End time for range
        step: Step interval (e.g., '1m', '5m', '1h')
        
    Returns:
        Prometheus range query results
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/prometheus/query_range", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/prometheus/query_range", method="GET").inc()
        
        try:
            # Validate time range
            if start >= end:
                raise HTTPException(status_code=400, detail="start time must be before end time")
            
            # Validate step format
            if not step or len(step) < 2:
                raise HTTPException(status_code=400, detail="invalid step format")
            
            result = await prometheus_client.query_range(query, start, end, step)
            
            # Validate response format
            if result.get("status") != "success":
                error_type = result.get("errorType", "unknown")
                error_msg = result.get("error", "Unknown PromQL query error")
                logger.error(f"PromQL range query error: {error_type} - {error_msg}")
                raise HTTPException(status_code=400, detail=f"PromQL range query failed: {error_msg}")
            
            return {
                "status": result["status"],
                "data": result["data"],
                "query": query,
                "start": start.isoformat(),
                "end": end.isoformat(),
                "step": step
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in PromQL range query: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while executing PromQL range query")


@router.get("/prometheus/alerts")
async def get_prometheus_alerts(
    authenticated: bool = Depends(verify_prometheus_auth)
):
    """
    Get current Prometheus alerts.
    
    Returns:
        Active Prometheus alerts
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/prometheus/alerts", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/prometheus/alerts", method="GET").inc()
        
        try:
            # Query active alerts
            alerts_query = "ALERTS{alertstate=\"firing\"}"
            result = await prometheus_client.query(alerts_query)
            
            if result.get("status") != "success":
                error_msg = result.get("error", "Unknown alerts query error")
                logger.error(f"Prometheus alerts query error: {error_msg}")
                raise HTTPException(status_code=502, detail="Failed to retrieve alerts from Prometheus")
            
            alerts = []
            if result["data"]["result"]:
                for alert in result["data"]["result"]:
                    alert_info = {
                        "alertname": alert["metric"].get("alertname", "unknown"),
                        "severity": alert["metric"].get("severity", "warning"),
                        "instance": alert["metric"].get("instance", "unknown"),
                        "job": alert["metric"].get("job", "unknown"),
                        "value": alert["value"][1],
                        "timestamp": alert["value"][0]
                    }
                    alerts.append(alert_info)
            
            return {
                "status": "success",
                "alerts": alerts,
                "total_count": len(alerts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Prometheus alerts: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving Prometheus alerts")


@router.get("/prometheus/targets")
async def get_prometheus_targets(
    authenticated: bool = Depends(verify_prometheus_auth)
):
    """
    Get Prometheus targets status.
    
    Returns:
        Prometheus targets and their health status
    """
    with MONITORING_REQUEST_DURATION.labels(endpoint="/prometheus/targets", method="GET").time():
        MONITORING_REQUESTS_TOTAL.labels(endpoint="/prometheus/targets", method="GET").inc()
        
        try:
            headers = prometheus_client.get_auth_headers()
            
            async with httpx.AsyncClient(timeout=prometheus_client.timeout) as client:
                response = await client.get(
                    f"{prometheus_client.base_url}/api/v1/targets",
                    headers=headers
                )
                response.raise_for_status()
                result = response.json()
            
            if result.get("status") != "success":
                raise HTTPException(status_code=502, detail="Failed to retrieve targets from Prometheus")
            
            # Process targets data
            targets_info = {
                "active_targets": [],
                "dropped_targets": []
            }
            
            for target in result["data"]["activeTargets"]:
                target_info = {
                    "instance": target["labels"].get("instance", "unknown"),
                    "job": target["labels"].get("job", "unknown"),
                    "health": target["health"],
                    "last_error": target.get("lastError"),
                    "scrape_interval": target["labels"].get("scrape_interval", "unknown"),
                    "scrape_timeout": target["labels"].get("scrape_timeout", "unknown")
                }
                targets_info["active_targets"].append(target_info)
            
            for target in result["data"]["droppedTargets"]:
                target_info = {
                    "instance": target["labels"].get("instance", "unknown"),
                    "job": target["labels"].get("job", "unknown"),
                    "reason": target.get("reason", "unknown")
                }
                targets_info["dropped_targets"].append(target_info)
            
            return {
                "status": "success",
                "data": targets_info,
                "total_active": len(targets_info["active_targets"]),
                "total_dropped": len(targets_info["dropped_targets"]),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Prometheus targets request failed: {e}")
            raise HTTPException(status_code=502, detail="Prometheus service unavailable")
        except httpx.RequestError as e:
            logger.error(f"Prometheus connection error: {e}")
            raise HTTPException(status_code=503, detail="Failed to connect to Prometheus")
        except Exception as e:
            logger.error(f"Unexpected error in Prometheus targets: {e}")
            raise HTTPException(status_code=500, detail="Internal server error while retrieving Prometheus targets")
