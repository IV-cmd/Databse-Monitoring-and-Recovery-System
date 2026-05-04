"""
Simple Metrics Repository

Clean, production-grade metrics storage and retrieval.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BaseRepository


class MetricsRepository(BaseRepository):
    """Simple metrics repository for monitoring operations."""
    
    def __init__(self):
        self.metrics_data = []
    
    async def create(self, data: Dict[str, Any]) -> Any:
        """Store metrics data."""
        metric_record = {
            "id": len(self.metrics_data) + 1,
            "timestamp": datetime.utcnow(),
            "metric_name": data.get("name", "unknown"),
            "value": data.get("value", 0),
            "source": data.get("source", "system")
        }
        self.metrics_data.append(metric_record)
        return metric_record
    
    async def get_by_id(self, record_id: Any) -> Optional[Any]:
        """Get metric record by ID."""
        for record in self.metrics_data:
            if record["id"] == record_id:
                return record
        return None
    
    async def get_all(self, limit: Optional[int] = None) -> List[Any]:
        """Get all metric records."""
        if limit:
            return self.metrics_data[-limit:]
        return self.metrics_data
    
    async def update(self, record_id: Any, data: Dict[str, Any]) -> Any:
        """Update metric record."""
        for i, record in enumerate(self.metrics_data):
            if record["id"] == record_id:
                self.metrics_data[i].update(data)
                self.metrics_data[i]["updated_at"] = datetime.utcnow()
                return self.metrics_data[i]
        return None
    
    async def delete(self, record_id: Any) -> bool:
        """Delete metric record."""
        for i, record in enumerate(self.metrics_data):
            if record["id"] == record_id:
                del self.metrics_data[i]
                return True
        return False
    
    async def get_metrics_by_name(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics by name."""
        filtered_metrics = [
            record for record in self.metrics_data
            if record.get("metric_name") == metric_name
        ]
        return filtered_metrics[:limit]
    
    async def get_latest_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest metrics."""
        return sorted(self.metrics_data, key=lambda x: x["timestamp"], reverse=True)[:limit]
