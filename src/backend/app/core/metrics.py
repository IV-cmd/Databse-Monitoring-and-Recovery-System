"""
Simple Metrics Collection
Clean, production-grade metrics for the Database Monitoring System.
"""

import logging
from typing import Dict, Any
from prometheus_client import Counter, Gauge, Histogram, generate_latest

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Simple metrics collection system."""
    
    def __init__(self):
        # Core database metrics
        self.db_connections = Gauge('db_active_connections', 'Number of active database connections')
        self.db_size = Gauge('db_size_bytes', 'Database size in bytes')
        self.replication_lag = Gauge('db_replication_lag_seconds', 'Replication lag in seconds')
        
        # System metrics
        self.recovery_actions = Counter('auto_recovery_actions_total', 'Total auto recovery actions')
        self.alerts_sent = Counter('alerts_sent_total', 'Total alerts sent', ['alert_type'])
        self.query_duration = Histogram('db_query_duration_seconds', 'Database query duration')
        self.health_checks = Counter('health_checks_total', 'Total health checks', ['status'])
    
    def update_connections(self, count: int):
        """Update active connections metric."""
        if count >= 0:
            self.db_connections.set(count)
    
    def update_database_size(self, size_bytes: int):
        """Update database size metric."""
        if size_bytes >= 0:
            self.db_size.set(size_bytes)
    
    def update_replication_lag(self, lag_seconds: float):
        """Update replication lag metric."""
        if lag_seconds >= 0:
            self.replication_lag.set(lag_seconds)
    
    def increment_recovery_counter(self):
        """Increment recovery actions counter."""
        self.recovery_actions.inc()
    
    def increment_alert_counter(self, alert_type: str):
        """Increment alert counter by type."""
        if alert_type:
            self.alerts_sent.labels(alert_type=alert_type).inc()
    
    def record_query_duration(self, duration_seconds: float):
        """Record database query duration."""
        if duration_seconds >= 0:
            self.query_duration.observe(duration_seconds)
    
    def increment_health_check_counter(self, status: str):
        """Increment health check counter."""
        if status:
            self.health_checks.labels(status=status).inc()
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format."""
        try:
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to generate Prometheus metrics: {e}")
            return "# Error generating metrics\n"
