"""
Simple Validators

Essential validation functions for the application.
"""

from typing import Dict, Any, Union


def validate_threshold(value: Union[int, float], min_val: float = 0, max_val: float = 100) -> Dict[str, Any]:
    """Validate threshold value."""
    try:
        numeric_value = float(value)
        
        if numeric_value < min_val:
            return {"valid": False, "error": f"Value {numeric_value} is below minimum {min_val}"}
        
        if numeric_value > max_val:
            return {"valid": False, "error": f"Value {numeric_value} is above maximum {max_val}"}
        
        return {"valid": True, "value": numeric_value}
        
    except (ValueError, TypeError):
        return {"valid": False, "error": f"Invalid numeric value: {value}"}


def validate_interval(interval: Union[int, float], min_interval: int = 1, max_interval: int = 3600) -> Dict[str, Any]:
    """Validate monitoring interval."""
    try:
        numeric_interval = int(interval)
        
        if numeric_interval < min_interval:
            return {"valid": False, "error": f"Interval {numeric_interval}s is below minimum {min_interval}s"}
        
        if numeric_interval > max_interval:
            return {"valid": False, "error": f"Interval {numeric_interval}s is above maximum {max_interval}s"}
        
        return {"valid": True, "interval": numeric_interval}
        
    except (ValueError, TypeError):
        return {"valid": False, "error": f"Invalid interval value: {interval}"}
