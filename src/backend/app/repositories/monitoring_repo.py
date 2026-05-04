"""
Simple Monitoring Repository

Clean, production-grade monitoring data storage and retrieval.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BaseRepository


class MonitoringRepository(BaseRepository):
    """Simple monitoring repository for monitoring operations."""
    
    def __init__(self):
        self.monitoring_data = []
    
    async def create(self, data: Dict[str, Any]) -> Any:
        """Store monitoring data."""
        monitoring_record = {
            "id": len(self.monitoring_data) + 1,
            "timestamp": datetime.utcnow(),
            "data": data
        }
        self.monitoring_data.append(monitoring_record)
        return monitoring_record
    
    async def get_by_id(self, record_id: Any) -> Optional[Any]:
        """Get monitoring record by ID."""
        for record in self.monitoring_data:
            if record["id"] == record_id:
                return record
        return None
    
    async def get_all(self, limit: Optional[int] = None) -> List[Any]:
        """Get all monitoring records."""
        if limit:
            return self.monitoring_data[-limit:]
        return self.monitoring_data
    
    async def update(self, record_id: Any, data: Dict[str, Any]) -> Any:
        """Update monitoring record."""
        for i, record in enumerate(self.monitoring_data):
            if record["id"] == record_id:
                self.monitoring_data[i].update(data)
                self.monitoring_data[i]["updated_at"] = datetime.utcnow()
                return self.monitoring_data[i]
        return None
    
    async def delete(self, record_id: Any) -> bool:
        """Delete monitoring record."""
        for i, record in enumerate(self.monitoring_data):
            if record["id"] == record_id:
                del self.monitoring_data[i]
                return True
        return False
    
    async def get_latest_monitoring(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest monitoring records."""
        return sorted(self.monitoring_data, key=lambda x: x["timestamp"], reverse=True)[:limit]
