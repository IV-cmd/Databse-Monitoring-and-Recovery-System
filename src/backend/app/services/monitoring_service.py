"""
Simple Monitoring Service

Clean, production-grade monitoring operations.
"""

from typing import Dict, Any, List
from datetime import datetime

from ..repositories.data_repo import DataRepository, DataType
from ..core.monitoring import DatabaseMonitor


class MonitoringService:
    """Simple monitoring service for monitoring operations."""
    
    def __init__(self, data_repo: DataRepository):
        self.data_repo = data_repo
        self.monitor = DatabaseMonitor()
    
    async def store_monitoring_data(self, data: Dict[str, Any]) -> Any:
        """Store monitoring data."""
        return await self.data_repo.create_monitoring(data)
    
    async def get_latest_monitoring(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest monitoring data."""
        records = await self.data_repo.get_latest(DataType.MONITORING, limit)
        return [record["data"] for record in records]
    
    async def check_monitoring_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check monitoring data for alerts using DatabaseMonitor."""
        alerts = self.monitor.check_thresholds(metrics)
        return [alert.__dict__ for alert in alerts]
    
    async def get_monitoring_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive monitoring summary using DatabaseMonitor."""
        return self.monitor.get_monitoring_summary(metrics)
