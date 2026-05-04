"""
Simple Helper Functions

Essential utility functions for the application.
"""

from datetime import datetime
from typing import Any, Dict, Union


def format_timestamp(timestamp: Union[datetime, str, float]) -> str:
    """Format timestamp to ISO 8601 string."""
    if isinstance(timestamp, float):
        return datetime.fromtimestamp(timestamp).isoformat()
    elif isinstance(timestamp, str):
        return timestamp
    elif isinstance(timestamp, datetime):
        return timestamp.isoformat()
    else:
        return str(timestamp)


def calculate_percentage(current: float, total: float) -> float:
    """Calculate percentage safely."""
    if total == 0:
        return 0.0
    return round((current / total) * 100, 2)


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
