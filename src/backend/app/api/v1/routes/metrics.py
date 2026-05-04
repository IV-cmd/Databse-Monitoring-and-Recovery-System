"""
Simple Metrics Routes

Clean, production-grade metrics API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime

from app.dependencies import get_database_service, get_metrics_service
from app.models.schemas import MetricsResponse
from app.services.metrics_service import MetricsService
from app.services.database_service import DatabaseService

router = APIRouter()

@router.get("/current", response_model=MetricsResponse)
async def get_current_metrics(
    service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get current system metrics."""
    try:
        # Get database status
        db_status = await service.get_database_status()
        
        # Get system metrics
        system_metrics = await metrics_service.collect_all_metrics()
        
        # Combine metrics
        current_metrics = {
            "database": db_status,
            "system": system_metrics
        }
        
        return MetricsResponse(
            timestamp=datetime.utcnow(),
            current=current_metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@router.get("/query")
async def query_metrics(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    metric_name: Optional[str] = None,
    limit: int = 100,
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Query historical metrics with time range filtering."""
    try:
        # Get metrics by name if specified, otherwise get latest
        if metric_name:
            metrics = await metrics_service.get_metrics_by_name(metric_name, limit)
        else:
            metrics = await metrics_service.get_latest_metrics(limit)
        
        # Simple time filtering (if timestamps are available)
        if start_time or end_time:
            filtered_metrics = []
            for metric in metrics:
                metric_time = metric.get("timestamp")
                if metric_time:
                    if start_time and metric_time < start_time:
                        continue
                    if end_time and metric_time > end_time:
                        continue
                filtered_metrics.append(metric)
            metrics = filtered_metrics
        
        return {
            "metrics": metrics,
            "count": len(metrics),
            "query_params": {
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "metric_name": metric_name,
                "limit": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to query metrics")

@router.get("/database")
async def get_database_metrics(service: DatabaseService = Depends(get_database_service)):
    """Get database-specific metrics."""
    try:
        return await service.get_database_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get database metrics")

@router.get("/system")
async def get_system_metrics(metrics_service: MetricsService = Depends(get_metrics_service)):
    """Get system-level metrics."""
    try:
        return await metrics_service.collect_all_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

