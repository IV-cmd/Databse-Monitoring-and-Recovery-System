"""
Core Monitoring Module

Enterprise-grade monitoring system with clean architecture.
"""

from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Alert:
    """Alert data structure."""
    type: str
    severity: str
    value: float
    message: str
    timestamp: str


class DatabaseMonitor:
    """Enterprise-grade database monitoring system."""
    
    def __init__(self):
        # Monitoring thresholds
        self.cpu_warning = 80.0
        self.cpu_critical = 95.0
        self.memory_warning = 85.0
        self.memory_critical = 95.0
        self.disk_warning = 85.0
        self.disk_critical = 95.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_active": True
        }
    
    def _check_cpu_thresholds(self, cpu_percent: float) -> List[Alert]:
        """Check CPU thresholds and generate alerts."""
        alerts = []
        if cpu_percent >= self.cpu_critical:
            alerts.append(Alert(
                type="cpu",
                severity="critical",
                value=cpu_percent,
                message=f"CPU usage is critically high: {cpu_percent}%",
                timestamp=datetime.utcnow().isoformat()
            ))
        elif cpu_percent >= self.cpu_warning:
            alerts.append(Alert(
                type="cpu",
                severity="warning", 
                value=cpu_percent,
                message=f"CPU usage is high: {cpu_percent}%",
                timestamp=datetime.utcnow().isoformat()
            ))
        return alerts
    
    def _check_memory_thresholds(self, memory_percent: float) -> List[Alert]:
        """Check memory thresholds and generate alerts."""
        alerts = []
        if memory_percent >= self.memory_critical:
            alerts.append(Alert(
                type="memory",
                severity="critical",
                value=memory_percent,
                message=f"Memory usage is critically high: {memory_percent}%",
                timestamp=datetime.utcnow().isoformat()
            ))
        elif memory_percent >= self.memory_warning:
            alerts.append(Alert(
                type="memory",
                severity="warning",
                value=memory_percent,
                message=f"Memory usage is high: {memory_percent}%",
                timestamp=datetime.utcnow().isoformat()
            ))
        return alerts
    
    def _check_disk_thresholds(self, disk_percent: float) -> List[Alert]:
        """Check disk thresholds and generate alerts."""
        alerts = []
        if disk_percent >= self.disk_critical:
            alerts.append(Alert(
                type="disk",
                severity="critical",
                value=disk_percent,
                message=f"Disk usage is critically high: {disk_percent}%",
                timestamp=datetime.utcnow().isoformat()
            ))
        elif disk_percent >= self.disk_warning:
            alerts.append(Alert(
                type="disk",
                severity="warning",
                value=disk_percent,
                message=f"Disk usage is high: {disk_percent}%",
                timestamp=datetime.utcnow().isoformat()
            ))
        return alerts
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against thresholds and return alerts."""
        alerts = []
        
        # Check CPU
        cpu_percent = metrics.get("cpu_percent", 0)
        alerts.extend(self._check_cpu_thresholds(cpu_percent))
        
        # Check Memory
        memory_percent = metrics.get("memory_percent", 0)
        alerts.extend(self._check_memory_thresholds(memory_percent))
        
        # Check Disk
        disk_percent = metrics.get("disk_percent", 0)
        alerts.extend(self._check_disk_thresholds(disk_percent))
        
        return alerts
    
    def get_monitoring_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive monitoring summary."""
        status = self.get_status()
        alerts = self.check_thresholds(metrics)
        
        return {
            "status": status["status"],
            "timestamp": status["timestamp"],
            "monitoring_active": status["monitoring_active"],
            "alerts": [
                {
                    "type": alert.type,
                    "severity": alert.severity,
                    "value": alert.value,
                    "message": alert.message,
                    "timestamp": alert.timestamp
                }
                for alert in alerts
            ],
            "alerts_count": len(alerts),
            "metrics": metrics
        }
