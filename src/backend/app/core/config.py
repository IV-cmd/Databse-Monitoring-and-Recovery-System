"""
This module provides comprehensive configuration management with environment-based
settings, security, validation, and API alignment for the Database Monitoring System.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator, SecretStr
from typing import Optional, List, Union
import os
import secrets
from enum import Enum


class Environment(str, Enum):
    """Environment enumeration for configuration management."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Log level enumeration."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):

    # Environment and Core Settings
    ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment (development, testing, staging, production)"
    )
    
    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    LOG_LEVEL: LogLevel = Field(
        default=LogLevel.INFO,
        description="Application log level"
    )
    
    # Security Settings
    SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        description="Secret key for security operations"
    )
    
    API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="API key for external service authentication"
    )
    
    # Database Configuration
    DATABASE_URL: SecretStr = Field(
        default=SecretStr("postgresql://admin:admin123@localhost:5432/monitoring_db"),
        description="Primary database connection URL"
    )
    
    REPLICA_URL: Optional[SecretStr] = Field(
        default=None,
        description="Replica database connection URL"
    )
    
    # Database Connection Pool Settings
    DB_SSL_ENABLED: bool = Field(
        default=False,
        description="Enable SSL for database connections"
    )
    
    DB_SSL_CERT_FILE: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate file"
    )
    
    DB_SSL_KEY_FILE: Optional[str] = Field(
        default=None,
        description="Path to SSL key file"
    )
    
    DB_SSL_CA_FILE: Optional[str] = Field(
        default=None,
        description="Path to SSL CA file"
    )
    
    DB_SSL_VERIFY: str = Field(
        default="disable",
        description="SSL verification mode (disable/prefer/require)"
    )
    
    DB_CONNECTION_TIMEOUT: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Database connection timeout in seconds"
    )
    
    DB_COMMAND_TIMEOUT: float = Field(
        default=60.0,
        ge=1.0,
        le=600.0,
        description="Database command timeout in seconds"
    )
    
    DB_MAX_CONNECTIONS: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum database connections"
    )
    
    DB_MIN_CONNECTIONS: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Minimum database connections"
    )
    
    # Monitoring Configuration
    PROMETHEUS_URL: str = Field(
        default="http://localhost:9090",
        description="Prometheus server URL"
    )
    
    PROMETHEUS_USERNAME: Optional[str] = Field(
        default=None,
        description="Prometheus authentication username"
    )
    
    PROMETHEUS_PASSWORD: Optional[SecretStr] = Field(
        default=None,
        description="Prometheus authentication password"
    )
    
    PROMETHEUS_AUTH_REQUIRED: bool = Field(
        default=False,
        description="Require Prometheus authentication"
    )
    
    PROMETHEUS_BEARER_TOKEN: Optional[SecretStr] = Field(
        default=None,
        description="Prometheus bearer token for authentication"
    )
    
    PROMETHEUS_TIMEOUT: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        description="Prometheus request timeout in seconds"
    )
    
    MONITOR_INTERVAL: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Monitoring interval in seconds"
    )
    
    HEALTH_CHECK_INTERVAL: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Health check interval in seconds"
    )
    
    # Grafana Configuration
    GRAFANA_URL: str = Field(
        default="http://localhost:3000",
        description="Grafana server URL"
    )
    
    GRAFANA_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Grafana API key"
    )
    
    # Recovery Configuration
    AUTO_RECOVERY_ENABLED: bool = Field(
        default=True,
        description="Enable automatic recovery operations"
    )
    
    MAX_RECOVERY_ATTEMPTS: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum recovery attempts"
    )
    
    RECOVERY_TIMEOUT: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Recovery operation timeout in seconds"
    )
    
    RECOVERY_AUTH_REQUIRED: bool = Field(
        default=False,
        description="Require authentication for recovery operations"
    )
    
    RECOVERY_BEARER_TOKEN: Optional[SecretStr] = Field(
        default=None,
        description="Bearer token for recovery operations"
    )
    
    # Alert Configuration (removed Slack for development)
    ALERT_COOLDOWN: int = Field(
        default=300,
        ge=60,
        le=3600,
        description="Alert cooldown period in seconds"
    )
    
    # API Configuration (simplified for development)
    API_PREFIX: str = Field(
        default="/api/v1",
        description="API URL prefix"
    )
    
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        description="CORS allowed origins (simplified for development)"
    )
    
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        description="Allowed hosts for application (simplified for development)"
    )
    
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Rate limit requests per minute"
    )
    
    LOG_REQUEST_BODY: bool = Field(
        default=False,
        description="Enable request body logging"
    )
    
    # Monitoring Thresholds
    CPU_WARNING_THRESHOLD: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="CPU warning threshold percentage"
    )
    
    CPU_CRITICAL_THRESHOLD: float = Field(
        default=95.0,
        ge=0.0,
        le=100.0,
        description="CPU critical threshold percentage"
    )
    
    MEMORY_WARNING_THRESHOLD: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Memory warning threshold percentage"
    )
    
    MEMORY_CRITICAL_THRESHOLD: float = Field(
        default=95.0,
        ge=0.0,
        le=100.0,
        description="Memory critical threshold percentage"
    )
    
    DISK_WARNING_THRESHOLD: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Disk warning threshold percentage"
    )
    
    DISK_CRITICAL_THRESHOLD: float = Field(
        default=95.0,
        ge=0.0,
        le=100.0,
        description="Disk critical threshold percentage"
    )
    
    # Database Performance Thresholds
    SLOW_QUERY_THRESHOLD: float = Field(
        default=1.0,
        ge=0.1,
        le=60.0,
        description="Slow query threshold in seconds"
    )
    
    MAX_CONNECTIONS: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum database connections"
    )
    
    REPLICATION_LAG_THRESHOLD: float = Field(
        default=10.0,
        ge=1.0,
        le=300.0,
        description="Replication lag threshold in seconds"
    )
    
    # Metrics Collection Configuration
    METRICS_COLLECTION_INTERVAL: int = Field(
        default=5,
        ge=1,
        le=60,
        description="Metrics collection interval in minutes"
    )
    
    MONITORING_INTERVAL_SECONDS: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Monitoring interval in seconds"
    )
    
    SLOW_QUERIES_DEFAULT_LIMIT: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Default limit for slow queries"
    )
    
    SLOW_QUERIES_THRESHOLD_MS: float = Field(
        default=1000.0,
        ge=100.0,
        le=60000.0,
        description="Slow queries threshold in milliseconds"
    )
    
    
    @validator("CPU_CRITICAL_THRESHOLD")
    def validate_cpu_thresholds(cls, v, values):
        """Validate CPU thresholds are logical."""
        if "CPU_WARNING_THRESHOLD" in values and v <= values["CPU_WARNING_THRESHOLD"]:
            raise ValueError("CPU critical threshold must be greater than warning threshold")
        return v
    
    @validator("MEMORY_CRITICAL_THRESHOLD")
    def validate_memory_thresholds(cls, v, values):
        """Validate memory thresholds are logical."""
        if "MEMORY_WARNING_THRESHOLD" in values and v <= values["MEMORY_WARNING_THRESHOLD"]:
            raise ValueError("Memory critical threshold must be greater than warning threshold")
        return v
    
    @validator("DISK_CRITICAL_THRESHOLD")
    def validate_disk_thresholds(cls, v, values):
        """Validate disk thresholds are logical."""
        if "DISK_WARNING_THRESHOLD" in values and v <= values["DISK_WARNING_THRESHOLD"]:
            raise ValueError("Disk critical threshold must be greater than warning threshold")
        return v
    
    @validator("DB_MAX_CONNECTIONS")
    def validate_db_connections(cls, v, values):
        """Validate database connection pool sizes."""
        if "DB_MIN_CONNECTIONS" in values and v < values["DB_MIN_CONNECTIONS"]:
            raise ValueError("Max connections must be greater than or equal to min connections")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    @property
    def database_url(self) -> str:
        """Get database URL as string."""
        return self.DATABASE_URL.get_secret_value()
    
    @property
    def replica_url(self) -> Optional[str]:
        """Get replica URL as string."""
        return self.REPLICA_URL.get_secret_value() if self.REPLICA_URL else None
    
    @property
    def prometheus_password(self) -> Optional[str]:
        """Get Prometheus password as string."""
        return self.PROMETHEUS_PASSWORD.get_secret_value() if self.PROMETHEUS_PASSWORD else None
    
    @property
    def prometheus_bearer_token(self) -> Optional[str]:
        """Get Prometheus bearer token as string."""
        return self.PROMETHEUS_BEARER_TOKEN.get_secret_value() if self.PROMETHEUS_BEARER_TOKEN else None
    
    @property
    def recovery_bearer_token(self) -> Optional[str]:
        """Get recovery bearer token as string."""
        return self.RECOVERY_BEARER_TOKEN.get_secret_value() if self.RECOVERY_BEARER_TOKEN else None
    
    @property
    def slack_webhook_url(self) -> Optional[str]:
        """Get Slack webhook URL as string."""
        return self.SLACK_WEBHOOK_URL.get_secret_value() if self.SLACK_WEBHOOK_URL else None
    
    @property
    def grafana_api_key(self) -> Optional[str]:
        """Get Grafana API key as string."""
        return self.GRAFANA_API_KEY.get_secret_value() if self.GRAFANA_API_KEY else None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        validate_assignment=True,
        extra="forbid",
        env_prefix="DB_MONITOR_"
    )

# Create global settings instance
settings = Settings()

# Export commonly used settings for easier access
__all__ = ["settings", "Environment", "LogLevel", "Settings"]

