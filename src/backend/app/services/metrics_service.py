"""
Simple Metrics Service
Clean, production-grade metrics collection.
"""

from typing import Dict, Any
from datetime import datetime
import psutil

from ..repositories.data_repo import DataRepository, DataType

class MetricsService:
    """Simple metrics service for monitoring operations."""
    
    def __init__(self, data_repo: DataRepository):
        self.data_repo = data_repo
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics."""
        cpu_metrics = {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count()
        }
        
        memory = psutil.virtual_memory()
        memory_metrics = {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        }
        
        disk = psutil.disk_usage('/')
        disk_metrics = {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent
        }
        
        network = psutil.net_io_counters()
        network_metrics = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv
        }
        
        return {
            "system": {
                "cpu": cpu_metrics,
                "memory": memory_metrics,
                "disk": disk_metrics,
                "network": network_metrics
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def store_metrics(self, name: str, value: float) -> Any:
        """Store a metric."""
        data = {"name": name, "value": value}
        return await self.data_repo.create_metric(data)
    
    async def get_metrics_by_name(self, name: str, limit: int = 50) -> list:
        """Get metrics by name."""
        records = await self.data_repo.get_metrics_by_name(name, limit)
        return [record["data"] for record in records]
    
    async def get_latest_metrics(self, limit: int = 50) -> list:
        """Get latest metrics."""
        records = await self.data_repo.get_latest_metrics(limit)
        return [record["data"] for record in records]
    
    
