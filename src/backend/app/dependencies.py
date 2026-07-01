"""
Simple Dependencies

Clean dependency injection for all services.
"""

from app.services.database_service import DatabaseService
from app.services.metrics_service import MetricsService
from app.services.monitoring_service import MonitoringService
from app.services.recovery_service import RecoveryService
from app.repositories.database_repo import DatabaseRepository
from app.repositories.data_repo import DataRepository
from app.core.database import DatabaseManager, get_database


def get_data_repository() -> DataRepository:
    """Get unified data repository instance."""
    return DataRepository()


async def get_database_repository() -> DatabaseRepository:
    """Get database repository instance with initialized pool."""
    try:
        db_manager = await get_database()
    except Exception:
        db_manager = DatabaseManager()
    return DatabaseRepository(db_manager)


async def get_database_service() -> DatabaseService:
    """Get database service instance."""
    return DatabaseService(await get_database_repository())


def get_metrics_service() -> MetricsService:
    """Get metrics service instance."""
    return MetricsService(get_data_repository())


def get_monitoring_service() -> MonitoringService:
    """Get monitoring service instance."""
    return MonitoringService(get_data_repository())


def get_recovery_service() -> RecoveryService:
    """Get recovery service instance."""
    return RecoveryService(get_data_repository())
