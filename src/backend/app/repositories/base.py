"""
Simple Base Repository

Clean, production-grade base repository for database operations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseRepository(ABC):
    """Simple base repository with essential CRUD operations."""
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Any:
        """Create a new record."""
        pass
        
    @abstractmethod
    async def get_by_id(self, record_id: Any) -> Optional[Any]:
        """Get a record by ID."""
        pass
        
    @abstractmethod
    async def get_all(self, limit: Optional[int] = None) -> List[Any]:
        """Get all records."""
        pass
        
    @abstractmethod
    async def update(self, record_id: Any, data: Dict[str, Any]) -> Any:
        """Update a record."""
        pass
        
    @abstractmethod
    async def delete(self, record_id: Any) -> bool:
        """Delete a record."""
        pass
