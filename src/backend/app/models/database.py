"""
Database Models

Clean, simple database models for the Database Monitoring System.
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import Field

from .base import BaseSchema, TimestampMixin, StatusEnum, SeverityEnum, RecoveryStatusEnum


class DatabaseStatus(BaseSchema, TimestampMixin):
    """Database status model."""
    
    healthy: bool = Field(description="Whether the database is healthy")
    connections: int = Field(ge=0, description="Number of active connections")
    size_bytes: int = Field(ge=0, description="Database size in bytes")
    replication_lag: Optional[float] = Field(
        default=None, 
        ge=0, 
        description="Replication lag in seconds"
    )


class RecoveryAction(BaseSchema, TimestampMixin):
    """Recovery action model."""
    
    id: int = Field(ge=1, description="Unique identifier for the recovery action")
    action_type: str = Field(min_length=1, description="Type of recovery action")
    status: RecoveryStatusEnum = Field(description="Current status of the recovery action")
    details: str = Field(min_length=1, description="Details about the recovery action")


class AlertMessage(BaseSchema, TimestampMixin):
    """Alert message model."""
    
    alert_type: str = Field(min_length=1, description="Type of alert")
    message: str = Field(min_length=1, max_length=500, description="Alert message")
    severity: SeverityEnum = Field(description="Alert severity level")


class HealthCheckResult(BaseSchema, TimestampMixin):
    """Health check result model."""
    
    primary: DatabaseStatus = Field(description="Primary database status")
    replica: Optional[DatabaseStatus] = Field(
        default=None, 
        description="Replica database status"
    )
    overall_status: StatusEnum = Field(description="Overall system status")


class MetricsSnapshot(BaseSchema, TimestampMixin):
    """Metrics snapshot model."""
    
    connections: int = Field(ge=0, description="Number of active connections")
    database_size_bytes: int = Field(ge=0, description="Database size in bytes")
    replication_lag_seconds: Optional[float] = Field(
        default=None, 
        ge=0, 
        description="Replication lag in seconds"
    )


class RecoveryStatus(BaseSchema, TimestampMixin):
    """Recovery status model."""
    
    recovery_attempts: Dict[str, int] = Field(description="Recovery attempts per database")
    auto_recovery_enabled: bool = Field(description="Whether auto-recovery is enabled")
    max_recovery_attempts: int = Field(ge=1, description="Maximum recovery attempts allowed")
