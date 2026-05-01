"""
Metrics Routes
This module contains all metrics related API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from app.models.schemas import MetricsResponse, MetricsQueryRequest
from app.services.database_service import DatabaseService
from app.services.metrics_service import MetricsService
from app.repositories.metrics_repo import MetricsRepository
from app.utils.logger import get_logger
from app.core.config import settings
import httpx
import asyncpg
import psutil
import random

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

@router.get("/current", response_model=MetricsResponse)
async def get_current_metrics(
    service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends()
):
    """
    Get current system metrics.
    Returns:
        Current metrics from all monitoring sources
    """
    try:
        # Get database status
        status = await service.get_status()
        primary_status = status.get("primary", {})
        
        # Get system metrics using MetricsService
        system_metrics = await metrics_service.collect_all_metrics()
        
        # Combine metrics
        current_metrics = {
            "database": primary_status,
            "system": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Define thresholds from settings
        thresholds = {
            "cpu_warning": settings.CPU_WARNING_THRESHOLD,
            "cpu_critical": settings.CPU_CRITICAL_THRESHOLD,
            "memory_warning": settings.MEMORY_WARNING_THRESHOLD,
            "memory_critical": settings.MEMORY_CRITICAL_THRESHOLD,
            "disk_warning": settings.DISK_WARNING_THRESHOLD,
            "disk_critical": settings.DISK_CRITICAL_THRESHOLD
        }
        
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            current=current_metrics,
            thresholds=thresholds
        )
        
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error in current metrics: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except psutil.AccessDenied as e:
        logger.error(f"System access denied in current metrics: {e}")
        raise HTTPException(status_code=403, detail="Insufficient permissions to access system metrics")
    except Exception as e:
        logger.error(f"Unexpected error in current metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving current metrics")

@router.get("/query", response_model=MetricsResponse)
async def query_metrics(
    request: MetricsQueryRequest = Depends(),
    service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends(),
    metrics_repo: MetricsRepository = Depends()
):
    """
    Query historical metrics with filtering and aggregation.
    Args:
        request: Metrics query parameters
        
    Returns:
        Historical metrics based on query parameters
    """
    try:
        # Validate time range
        if request.end_time and request.start_time and request.end_time <= request.start_time:
            raise HTTPException(status_code=400, detail="end_time must be after start_time")
        
        # Set default time range if not provided
        end_time = request.end_time or datetime.utcnow()
        start_time = request.start_time or (end_time - timedelta(hours=24))
        
        # Query actual metrics storage using MetricsService and MetricsRepository
        try:
            # Get historical metrics from repository
            historical_data = await metrics_repo.get_metrics_history(
                start_time=start_time,
                end_time=end_time,
                metric_types=request.metric_types or ["cpu", "memory", "disk", "network"]
            )
            
            # If no data found, collect current metrics as fallback
            if not historical_data:
                logger.warning(f"No historical data found for time range {start_time} to {end_time}")
                # Get current metrics using MetricsService
                current_metrics_data = await metrics_service.collect_all_metrics()
                historical_data = [{
                    "timestamp": datetime.utcnow().isoformat(),
                    **current_metrics_data
                }]
        except Exception as e:
            logger.error(f"Failed to query metrics repository: {e}")
            # Fallback to current metrics if repository fails
            current_metrics_data = await metrics_service.collect_all_metrics()
            historical_data = [{
                "timestamp": datetime.utcnow().isoformat(),
                **current_metrics_data
            }]
        
        # Apply aggregation if specified
        if request.aggregation == "avg":
            # Calculate averages
            aggregated = {}
            if historical_data:
                for key in historical_data[0].keys():
                    if key != "timestamp":
                        values = [item[key] for item in historical_data if isinstance(item[key], (int, float))]
                        if values:
                            aggregated[key] = sum(values) / len(values)
                        else:
                            aggregated[key] = values[0] if values else 0
        
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            current={
                "aggregation": request.aggregation,
                "data_points": len(historical_data),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "metrics": aggregated if request.aggregation == "avg" else historical_data[-1] if historical_data else {}
            },
            historical=historical_data if request.aggregation == "raw" else None
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid query parameters in metrics query: {e}")
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error in metrics query: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except psutil.AccessDenied as e:
        logger.error(f"System access denied in metrics query: {e}")
        raise HTTPException(status_code=403, detail="Insufficient permissions to access system metrics")
    except Exception as e:
        logger.error(f"Unexpected error in metrics query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while querying metrics")

@router.get("/database")
async def get_database_metrics(service: DatabaseService = Depends(get_database_service)):
    """
    Get database-specific metrics.
    
    Returns:
        Database performance and status metrics
    """
    try:
        status = await service.get_status()
        primary_status = status.get("primary", {})
        
        # Extract database-specific metrics
        db_metrics = {
            "connections": primary_status.get("connections", {}),
            "storage": primary_status.get("storage", {}),
            "replication": primary_status.get("replication", {}),
            "status": primary_status.get("status", "unknown"),
            "timestamp": primary_status.get("timestamp")
        }
        
        return db_metrics
        
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error in database metrics: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in database metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving database metrics")

@router.get("/system")
async def get_system_metrics():
    """
    Get system-level metrics.
    
    Returns:
        System performance metrics
    """
    try:
        
        # CPU metrics
        cpu_metrics = {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "load_average": list(psutil.getloadavg()),
            "frequency": psutil.cpu_freq()._asdict() if hasattr(psutil.cpu_freq(), '_asdict') else {}
        }
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_metrics = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        }
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_metrics = {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
        
        # Network metrics
        network = psutil.net_io_counters()
        network_metrics = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": cpu_metrics,
            "memory": memory_metrics,
            "disk": disk_metrics,
            "network": network_metrics
        }
        
    except psutil.AccessDenied as e:
        logger.error(f"System access denied in system metrics: {e}")
        raise HTTPException(status_code=403, detail="Insufficient permissions to access system metrics")
    except FileNotFoundError as e:
        logger.error(f"System resource not found in system metrics: {e}")
        raise HTTPException(status_code=404, detail="System resource not available")
    except Exception as e:
        logger.error(f"Unexpected error in system metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving system metrics")

@router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Get metrics in Prometheus format.
    Returns:
        Metrics formatted for Prometheus scraping
    """
    try:
        
        # Generate Prometheus metrics
        metrics = []
        
        # CPU metric
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(f"cern_db_cpu_percent {cpu_percent}")
        
        # Memory metric
        memory_percent = psutil.virtual_memory().percent
        metrics.append(f"cern_db_memory_percent {memory_percent}")
        
        # Disk metric
        disk_percent = psutil.disk_usage('/').percent
        metrics.append(f"cern_db_disk_percent {disk_percent}")
        
        # Combine into Prometheus format
        prometheus_data = "\n".join(metrics)
        
        return Response(
            content=prometheus_data,
            media_type="text/plain"
        )
        
    except psutil.AccessDenied as e:
        logger.error(f"System access denied in Prometheus metrics: {e}")
        raise HTTPException(status_code=403, detail="Insufficient permissions to access system metrics")
    except Exception as e:
        logger.error(f"Unexpected error in Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving Prometheus metrics")
