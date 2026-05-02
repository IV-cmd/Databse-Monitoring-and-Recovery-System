"""
Simple Base Model Classes

Clean, simple base model classes for the Database Monitoring System.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, ClassVar
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class BaseSchema(BaseModel):
    """
    Base schema class with essential configuration.
    """
    
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid",
        str_strip_whitespace=True
    )


class TimestampMixin(BaseModel):
    """
    Mixin to add timezone-aware timestamp fields.
    """
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the record was created"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the record was last updated"
    )


class StatusEnum(str, Enum):
    """Status enumeration for system components."""
    
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class SeverityEnum(str, Enum):
    """Severity enumeration for alerts and events."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStatusEnum(str, Enum):
    """Recovery status enumeration."""
    
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class BaseResponse(BaseSchema):
    """
    Base response class for all API responses.
    """
    
    success: bool = Field(default=True, description="Whether the operation was successful")
    message: str = Field(
        default="Operation completed successfully",
        min_length=1,
        max_length=500,
        description="Human-readable message describing the result"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Response timestamp"
    )


class ErrorResponse(BaseSchema):
    """
    Error response class for API errors.
    """
    
    success: bool = Field(default=False, frozen=True, description="Always False for error responses")
    error: str = Field(description="Human-readable error description")
    message: str = Field(
        min_length=1,
        max_length=500,
        description="Detailed error message for the user"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Error timestamp"
    )
