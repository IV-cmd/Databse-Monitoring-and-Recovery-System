"""
Simple Data Repository

Clean, production-grade data storage for monitoring operations.
Eliminates duplication across metrics, monitoring, and recovery data.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from .base import BaseRepository


class DataType(str, Enum):
    """Data type enumeration for different data categories."""
    METRICS = "metrics"
    MONITORING = "monitoring"
    RECOVERY = "recovery"


class DataRepository(BaseRepository):
    """Simple unified repository for all monitoring data operations."""
    
    def __init__(self):
        self.data = {}  # Organized by data type
        self.data[DataType.METRICS] = []
        self.data[DataType.MONITORING] = []
        self.data[DataType.RECOVERY] = []
    
    async def create(self, data: Dict[str, Any], data_type: DataType) -> Any:
        """Store data with type classification."""
        record = {
            "id": len(self.data[data_type]) + 1,
            "timestamp": datetime.utcnow(),
            "data": data
        }
        self.data[data_type].append(record)
        return record
    
    async def get_by_id(self, record_id: Any, data_type: DataType) -> Optional[Any]:
        """Get record by ID and type."""
        for record in self.data[data_type]:
            if record["id"] == record_id:
                return record
        return None
    
    async def get_all(self, data_type: DataType, limit: Optional[int] = None) -> List[Any]:
        """Get all records by type."""
        if limit:
            return self.data[data_type][-limit:]
        return self.data[data_type]
    
    async def update(self, record_id: Any, data: Dict[str, Any], data_type: DataType) -> Any:
        """Update record by ID and type."""
        for i, record in enumerate(self.data[data_type]):
            if record["id"] == record_id:
                self.data[data_type][i].update(data)
                self.data[data_type][i]["updated_at"] = datetime.utcnow()
                return self.data[data_type][i]
        return None
    
    async def delete(self, record_id: Any, data_type: DataType) -> bool:
        """Delete record by ID and type."""
        for i, record in enumerate(self.data[data_type]):
            if record["id"] == record_id:
                del self.data[data_type][i]
                return True
        return False
    
    async def get_by_field(self, field: str, value: Any, data_type: DataType, limit: int = 50) -> List[Dict[str, Any]]:
        """Get records by field value and type."""
        filtered = [
            record for record in self.data[data_type]
            if record["data"].get(field) == value
        ]
        return filtered[:limit]
    
    async def get_latest(self, data_type: DataType, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest records by type."""
        return sorted(self.data[data_type], key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    # Convenience methods for specific data types
    async def create_metric(self, data: Dict[str, Any]) -> Any:
        """Create metric record."""
        return await self.create(data, DataType.METRICS)
    
    async def create_monitoring(self, data: Dict[str, Any]) -> Any:
        """Create monitoring record."""
        return await self.create(data, DataType.MONITORING)
    
    async def create_recovery(self, data: Dict[str, Any]) -> Any:
        """Create recovery record."""
        return await self.create(data, DataType.RECOVERY)
    
    async def get_metrics_by_name(self, name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics by name."""
        return await self.get_by_field("name", name, DataType.METRICS, limit)
    
    async def get_recoveries_by_status(self, status: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recoveries by status."""
        return await self.get_by_field("status", status, DataType.RECOVERY, limit)
    
    async def get_latest_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest metrics."""
        return await self.get_latest(DataType.METRICS, limit)
    
    async def get_latest_monitoring(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest monitoring."""
        return await self.get_latest(DataType.MONITORING, limit)
    
    async def get_latest_recoveries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest recoveries."""
        return await self.get_latest(DataType.RECOVERY, limit)
