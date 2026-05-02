"""
API Schemas

Clean, simple API schemas for request/response models.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .base import BaseSchema, BaseResponse, StatusEnum, SeverityEnum, RecoveryStatusEnum


# Health Schemas
class HealthResponse(BaseResponse):
    """Health check response schema."""
    
    status: StatusEnum = Field(description="Current health status")
    service: str = Field(default="Database Monitor Service", description="Service name")
    version: str = Field(default="1.0.0", description="Service version")
    uptime_seconds: Optional[float] = Field(default=None, description="Uptime in seconds")
    components: Optional[Dict[str, Any]] = Field(default=None, description="Component status details")


class DetailedHealthResponse(HealthResponse):
    """Detailed health check response schema."""
    
    database: Dict[str, Any] = Field(description="Database component details")
    monitoring: Dict[str, Any] = Field(description="Monitoring component details")
    recovery: Dict[str, Any] = Field(description="Recovery component details")
    metrics: Dict[str, Any] = Field(description="Metrics component details")


# Monitoring Schemas
class MonitoringStatusResponse(BaseResponse):
    """Monitoring status response schema."""
    
    status: StatusEnum = Field(description="Monitoring status")
    is_monitoring: bool = Field(description="Whether monitoring is active")
    last_check: Optional[datetime] = Field(default=None, description="Last check timestamp")
    interval_seconds: int = Field(ge=1, description="Monitoring interval in seconds")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="Current metrics")


class MonitoringMetricsResponse(BaseResponse):
    """Monitoring metrics response schema."""
    
    timestamp: datetime = Field(description="Metrics timestamp")
    metrics: Dict[str, Any] = Field(description="Metrics data")
    alerts: Optional[List[Dict[str, Any]]] = Field(default=None, description="Active alerts")


# Recovery Schemas
class RecoveryRequest(BaseSchema):
    """Recovery request schema."""
    
    type: str = Field(min_length=1, description="Type of recovery: automatic or manual")
    reason: Optional[str] = Field(default=None, description="Reason for recovery")
    severity: SeverityEnum = Field(description="Severity level")
    force: bool = Field(default=False, description="Force recovery even if not needed")


class RecoveryResponse(BaseResponse):
    """Recovery response schema."""
    
    recovery_id: str = Field(min_length=1, description="Unique recovery identifier")
    status: RecoveryStatusEnum = Field(description="Recovery status")
    attempts: int = Field(ge=0, description="Number of attempts made")
    max_attempts: int = Field(ge=1, description="Maximum allowed attempts")
    started_at: datetime = Field(description="Recovery start timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Recovery completion timestamp")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional recovery details")


class RecoveryHistoryResponse(BaseResponse):
    """Recovery history response schema."""
    
    recoveries: List[Dict[str, Any]] = Field(description="List of recovery actions")
    total: int = Field(ge=0, description="Total number of recoveries")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, description="Number of items per page")


# Metrics Schemas
class MetricsResponse(BaseResponse):
    """Metrics response schema."""
    
    timestamp: datetime = Field(description="Metrics timestamp")
    current: Dict[str, Any] = Field(description="Current metrics")
    historical: Optional[List[Dict[str, Any]]] = Field(default=None, description="Historical metrics")
    thresholds: Optional[Dict[str, Any]] = Field(default=None, description="Metric thresholds")


class MetricsQueryRequest(BaseSchema):
    """Metrics query request schema."""
    
    start_time: Optional[datetime] = Field(default=None, description="Start time for query")
    end_time: Optional[datetime] = Field(default=None, description="End time for query")
    metric_names: Optional[List[str]] = Field(default=None, description="Specific metrics to retrieve")
    aggregation: str = Field(default="avg", description="Aggregation method: avg, min, max, sum")
    interval: str = Field(default="1m", description="Time interval for aggregation")


# Settings Schemas
class ThresholdSettings(BaseSchema):
    """Threshold settings schema."""
    
    max_connections: int = Field(default=100, ge=1, le=1000, description="Maximum database connections")
    slow_query_threshold: float = Field(default=1.0, ge=0.1, le=60.0, description="Slow query threshold in seconds")
    cpu_threshold: float = Field(default=80.0, ge=0.0, le=100.0, description="CPU threshold percentage")
    memory_threshold: float = Field(default=1024.0, ge=0.0, description="Memory threshold in MB")
    replication_lag_threshold: float = Field(default=10.0, ge=0.0, description="Replication lag threshold in seconds")


class DatabaseSettings(BaseSchema):
    """Database connection settings schema."""
    
    primary_url: str = Field(min_length=1, description="Primary database connection URL")
    replica_url: Optional[str] = Field(default=None, description="Replica database connection URL")


class MonitoringSettings(BaseSchema):
    """Monitoring settings schema."""
    
    interval: int = Field(default=30, ge=1, le=3600, description="Monitoring interval in seconds")
    health_check_interval: int = Field(default=10, ge=1, le=300, description="Health check interval in seconds")
    auto_recovery_enabled: bool = Field(default=True, description="Enable automatic recovery")
    max_recovery_attempts: int = Field(default=3, ge=1, le=10, description="Maximum recovery attempts")


class AlertSettings(BaseSchema):
    """Alert settings schema."""
    
    email_enabled: bool = Field(default=False, description="Enable email alerts")
    email_recipient: Optional[str] = Field(default=None, description="Email recipient for alerts")
    cooldown: int = Field(default=300, ge=60, le=3600, description="Alert cooldown period in seconds")


class SettingsRequest(BaseSchema):
    """Complete settings request schema."""
    
    database: DatabaseSettings = Field(description="Database configuration")
    monitoring: MonitoringSettings = Field(description="Monitoring configuration")
    alerts: AlertSettings = Field(description="Alert configuration")
    thresholds: ThresholdSettings = Field(description="Threshold configuration")


class SettingsResponse(BaseResponse):
    """Settings response schema."""
    
    settings: Dict[str, Any] = Field(description="Current settings")
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last update timestamp"
    )
