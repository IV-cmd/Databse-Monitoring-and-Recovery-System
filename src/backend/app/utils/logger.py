"""
Simple Logger

Essential logging utilities for the application.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with standard formatting."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
