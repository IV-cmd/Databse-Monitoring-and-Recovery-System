"""
Clean Monitoring Routes

Production-grade monitoring API endpoints aligned with service layers.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from app.dependencies import get_monitoring_service, get_database_service, get_metrics_service
from app.models.schemas import MonitoringStatusResponse, MonitoringMetricsResponse
from app.services.monitoring_service import MonitoringService
from app.services.database_service import DatabaseService
from app.services.metrics_service import MetricsService
from app.core.config import settings
from prometheus_client import Counter, Gauge, generate_latest

router = APIRouter()

# Simple Prometheus metrics
MONITORING_REQUESTS = Counter('monitoring_requests_total', 'Total monitoring requests')
DATABASE_STATUS = Gauge('database_status', 'Database status (1=healthy, 0=unhealthy)')
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'Current CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'Current memory usage percentage')
SYSTEM_DISK_USAGE = Gauge('system_disk_usage_percent', 'Current disk usage percentage')


class PrometheusClient:
    """Simple Prometheus client for essential operations."""
    
    def __init__(self):
        self.base_url = getattr(settings, 'PROMETHEUS_URL', 'http://localhost:9090')
        self.timeout = 30
    
    async def get_targets(self) -> Dict[str, Any]:
        """Get Prometheus targets status."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/targets")
                response.raise_for_status()
                return response.json()
        except httpx.RequestError:
            return {"status": "error", "message": "Failed to connect to Prometheus"}
        except httpx.HTTPStatusError:
            return {"status": "error", "message": "Prometheus service unavailable"}
    
    async def get_alerts(self) -> Dict[str, Any]:
        """Get current Prometheus alerts."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/alerts")
                response.raise_for_status()
                return response.json()
        except httpx.RequestError:
            return {"status": "error", "message": "Failed to connect to Prometheus"}
        except httpx.HTTPStatusError:
            return {"status": "error", "message": "Prometheus service unavailable"}


# Global Prometheus client instance
prometheus_client = PrometheusClient()

@router.get("/status", response_model=MonitoringStatusResponse)
async def get_monitoring_status(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    database_service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get current monitoring status."""
    MONITORING_REQUESTS.inc()
    
    try:
        # Get database status
        db_status = await database_service.get_database_status()
        
        # Get system metrics
        system_metrics = await metrics_service.collect_all_metrics()
        
        # Get latest monitoring data
        monitoring_data = await monitoring_service.get_latest_monitoring(limit=1)
        
        # Update Prometheus metrics
        is_healthy = db_status.get("status") == "healthy"
        DATABASE_STATUS.set(1 if is_healthy else 0)
        
        # Update system metrics
        system_data = system_metrics.get("system", {})
        SYSTEM_CPU_USAGE.set(system_data.get("cpu", {}).get("percent", 0))
        SYSTEM_MEMORY_USAGE.set(system_data.get("memory", {}).get("percent", 0))
        SYSTEM_DISK_USAGE.set(system_data.get("disk", {}).get("percent", 0))
        
        # Combine metrics
        combined_metrics = {
            "database": db_status,
            "system": system_metrics
        }
        
        return MonitoringStatusResponse(
            status="healthy" if is_healthy else "degraded",
            is_monitoring=True,
            last_check=datetime.utcnow(),
            interval_seconds=30,
            metrics=combined_metrics
        )
        
    except Exception as e:
        DATABASE_STATUS.set(0)
        raise HTTPException(status_code=500, detail="Failed to get monitoring status")

@router.get("/metrics", response_model=MonitoringMetricsResponse)
async def get_monitoring_metrics(
    monitoring_service: MonitoringService = Depends(get_monitoring_service),
    database_service: DatabaseService = Depends(get_database_service),
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get current monitoring metrics."""
    try:
        # Get database status
        db_status = await database_service.get_database_status()
        
        # Get system metrics
        system_metrics = await metrics_service.collect_all_metrics()
        
        # Get latest monitoring data
        monitoring_data = await monitoring_service.get_latest_monitoring(limit=10)
        
        # Combine metrics
        combined_metrics = {
            "database": db_status,
            "system": system_metrics,
            "monitoring": monitoring_data
        }
        
        return MonitoringMetricsResponse(
            timestamp=datetime.utcnow(),
            metrics=combined_metrics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get monitoring metrics")

@router.post("/data")
async def store_monitoring_data(
    data: Dict[str, Any],
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Store monitoring data."""
    try:
        result = await monitoring_service.store_monitoring_data(data)
        return {"success": True, "id": result["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store monitoring data")

@router.get("/data")
async def get_monitoring_data(
    limit: int = 50,
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get latest monitoring data."""
    try:
        data = await monitoring_service.get_latest_monitoring(limit)
        return {"monitoring_data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get monitoring data")

@router.get("/prometheus")
async def get_prometheus_metrics(
    metrics_service: MetricsService = Depends(get_metrics_service)
):
    """Get Prometheus metrics."""
    try:
        # Update system metrics
        system_metrics = await metrics_service.collect_all_metrics()
        system_data = system_metrics.get("system", {})
        
        # Update Prometheus gauges
        SYSTEM_CPU_USAGE.set(system_data.get("cpu", {}).get("percent", 0))
        SYSTEM_MEMORY_USAGE.set(system_data.get("memory", {}).get("percent", 0))
        SYSTEM_DISK_USAGE.set(system_data.get("disk", {}).get("percent", 0))
        
        # Generate Prometheus metrics
        metrics_data = generate_latest()
        
        return Response(
            content=metrics_data,
            media_type="text/plain"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate Prometheus metrics")

@router.get("/alerts")
async def get_monitoring_alerts(
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Get current monitoring alerts."""
    try:
        # Get latest monitoring data
        monitoring_data = await monitoring_service.get_latest_monitoring(limit=10)
        
        # Get system alerts using DatabaseMonitor
        system_alerts = []
        for data in monitoring_data:
            alerts = await monitoring_service.check_monitoring_alerts(data)
            system_alerts.extend(alerts)
        
        # Get alerts from Prometheus
        prometheus_alerts = await prometheus_client.get_alerts()
        
        return {
            "prometheus_alerts": prometheus_alerts,
            "system_alerts": system_alerts,
            "total_count": len(system_alerts) + len(prometheus_alerts.get("data", {}).get("alerts", [])),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get monitoring alerts")

@router.get("/query")
async def query_monitoring_data(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
    monitoring_service: MonitoringService = Depends(get_monitoring_service)
):
    """Query monitoring data with time range filtering."""
    try:
        # Get monitoring data
        monitoring_data = await monitoring_service.get_latest_monitoring(limit)
        
        # Simple time filtering
        if start_time or end_time:
            filtered_data = []
            for data in monitoring_data:
                data_time = data.get("timestamp")
                if isinstance(data_time, str):
                    data_time = datetime.fromisoformat(data_time.replace('Z', '+00:00'))
                
                if start_time and data_time < start_time:
                    continue
                if end_time and data_time > end_time:
                    continue
                filtered_data.append(data)
            monitoring_data = filtered_data
        
        return {
            "monitoring_data": monitoring_data,
            "count": len(monitoring_data),
            "query_params": {
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to query monitoring data")

@router.get("/targets")
async def get_monitoring_targets():
    """Get monitoring targets status."""
    try:
        # Get targets from Prometheus
        prometheus_targets = await prometheus_client.get_targets()
        
        return {
            "prometheus_targets": prometheus_targets,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get monitoring targets")

