"""
Simple Recovery Service

Clean, production-grade recovery operations.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ..repositories.data_repo import DataRepository, DataType


class RecoveryService:
    """Simple recovery service for recovery operations."""
    
    def __init__(self, data_repo: DataRepository):
        self.data_repo = data_repo
    
    async def store_recovery_data(self, data: Dict[str, Any]) -> Any:
        """Store recovery data."""
        return await self.data_repo.create_recovery(data)
    
    async def get_latest_recovery(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get latest recovery data."""
        records = await self.data_repo.get_latest(DataType.RECOVERY, limit)
        return [record["data"] for record in records]
    
    async def start_recovery(self, recovery_type: str, reason: str, severity: str = "medium") -> Dict[str, Any]:
        """Start a recovery operation."""
        recovery_id = str(uuid.uuid4())
        
        recovery_record = {
            "id": recovery_id,
            "type": recovery_type,
            "reason": reason,
            "severity": severity,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat()
        }
        
        # Store the recovery record
        await self.data_repo.create_recovery(recovery_record)
        
        return recovery_record
    
    async def get_recovery_status(self, recovery_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a specific recovery operation.
        
        Args:
            recovery_id: Unique recovery identifier
            
        Returns:
            Recovery record if found, None otherwise
        """
        records = await self.data_repo.get_latest(DataType.RECOVERY)
        for record in records:
            if record["data"]["id"] == recovery_id:
                return record["data"]
        
        return None
    
    async def get_recovery_history(
        self, 
        limit: int = 50,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recovery operation history.
        
        Args:
            limit: Maximum number of records to return
            status_filter: Filter by recovery status
            
        Returns:
            List of recovery operations
        """
        records = await self.data_repo.get_latest(DataType.RECOVERY, limit)
        if status_filter:
            return [record["data"] for record in records if record["data"]["status"] == status_filter]
        else:
            return [record["data"] for record in records]
