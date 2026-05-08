"""
Simple configuration management for Database Monitoring System.
Clean, production-grade settings without overkill.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import secrets
from enum import Enum


class Environment(str, Enum):
    """Environment enumeration."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Simple settings configuration."""
    
    # Core Settings
    ENVIRONMENT: Environment = Field(default=Environment.DEVELOPMENT)
    DEBUG: bool = Field(default=False)
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    
    # Database Configuration
    DATABASE_URL: SecretStr = Field(default=SecretStr("postgresql://localhost:5432/monitoring_db"))
    REPLICA_URL: Optional[SecretStr] = Field(default=None)
    
    # Database Connection Settings
    DB_SSL_ENABLED: bool = Field(default=False)
    DB_SSL_CERT_FILE: Optional[str] = Field(default=None)
    DB_SSL_KEY_FILE: Optional[str] = Field(default=None)
    DB_SSL_CA_FILE: Optional[str] = Field(default=None)
    DB_SSL_VERIFY: str = Field(default="disable")
    
    DB_COMMAND_TIMEOUT: float = Field(default=60.0)
    DB_MAX_CONNECTIONS: int = Field(default=100)
    DB_MIN_CONNECTIONS: int = Field(default=10)
    
    # Monitoring Configuration
    MONITORING_INTERVAL_SECONDS: int = Field(default=30)
    AUTO_RECOVERY_ENABLED: bool = Field(default=True)
    MAX_RECOVERY_ATTEMPTS: int = Field(default=3)
    
    # Thresholds
    MAX_CONNECTIONS: int = Field(default=100)
    REPLICATION_LAG_THRESHOLD: float = Field(default=10.0)
    DATABASE_SIZE_THRESHOLD_GB: float = Field(default=10.0)
    
    # Properties
    @property
    def database_url(self) -> str:
        """Get database URL as string."""
        return self.DATABASE_URL.get_secret_value()
    
    @property
    def replica_url(self) -> Optional[str]:
        """Get replica URL as string."""
        return self.REPLICA_URL.get_secret_value() if self.REPLICA_URL else None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

# Create global settings instance
settings = Settings()

# Export commonly used settings for easier access
__all__ = ["settings", "Environment", "Settings"]

