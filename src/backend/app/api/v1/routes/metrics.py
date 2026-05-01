"""
Metrics Routes

This module contains all metrics related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from ...models.schemas import MetricsResponse, MetricsQueryRequest
from ...services.database_service import DatabaseService
from ...utils.logger import get_logger


router = APIRouter()
logger = get_logger(__name__)


async def get_database_service() -> DatabaseService:
    """
    Dependency to get database service instance.
    """
    return DatabaseService(
        primary_url="postgresql://admin:admin123@postgres-primary:5432/monitoring_db",
        replica_url="postgresql://admin:admin123@postgres-replica:5432/monitoring_db"
    )


@router.get("/current", response_model=MetricsResponse)
async def get_current_metrics(service: DatabaseService = Depends(get_database_service)):
    """
    Get current system metrics.
    
    Returns:
        Current metrics from all monitoring sources
    """
    try:
        # Get database status
        status = await service.get_status()
        primary_status = status.get("primary", {})
        
        # Get system metrics (would use psutil in production)
        import psutil
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": list(psutil.getloadavg()),
            "network_io": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
        
        # Combine metrics
        current_metrics = {
            "database": primary_status,
            "system": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Define thresholds (would come from settings)
        thresholds = {
            "cpu_warning": 80.0,
            "cpu_critical": 95.0,
            "memory_warning": 85.0,
            "memory_critical": 95.0,
            "disk_warning": 85.0,
            "disk_critical": 95.0
        }
        
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            current=current_metrics,
            thresholds=thresholds
        )
        
    except Exception as e:
        logger.error(f"Failed to get current metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve current metrics")


@router.get("/query", response_model=MetricsResponse)
async def query_metrics(
    request: MetricsQueryRequest = Depends(),
    service: DatabaseService = Depends(get_database_service)
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
        
        # In production, this would query actual metrics storage
        # For now, return sample data
        historical_data = []
        current_time = start_time
        while current_time < end_time:
            # Generate sample metrics
            import psutil
            sample_metrics = {
                "timestamp": current_time.isoformat(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "connections": {
                    "active": 10,
                    "idle": 5,
                    "total": 15
                }
            }
            historical_data.append(sample_metrics)
            current_time += timedelta(minutes=5)  # 5-minute intervals
        
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
    except Exception as e:
        logger.error(f"Failed to query metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to query metrics")


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
        
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve database metrics")


@router.get("/system")
async def get_system_metrics():
    """
    Get system-level metrics.
    
    Returns:
        System performance metrics
    """
    try:
        import psutil
        
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
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")


@router.get("/prometheus")
async def get_prometheus_metrics():
    """
    Get metrics in Prometheus format.
    
    Returns:
        Metrics formatted for Prometheus scraping
    """
    try:
        import psutil
        
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
        
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Prometheus metrics")
