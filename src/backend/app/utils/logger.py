"""
Simple Logger

Essential logging utilities for the application.
Sends structured JSON logs to Logstash (TCP) when LOGSTASH_HOST is configured.
"""

import json
import logging
import os
import socket
import sys
from datetime import datetime, timezone
from typing import Optional


class LogstashTCPHandler(logging.Handler):
    """Sends JSON log records to a Logstash TCP input."""

    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                "@timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
                "level":   record.levelname,
                "logger":  record.name,
                "message": self.format(record),
                "service": "monitor-service",
                "host":    socket.gethostname(),
            }
            if record.exc_info:
                entry["exception"] = self.formatException(record.exc_info)
            payload = (json.dumps(entry) + "\n").encode("utf-8")
            with socket.create_connection((self.host, self.port), timeout=1) as sock:
                sock.sendall(payload)
        except Exception:
            pass  # never let logging errors crash the app


_logstash_handler: Optional[LogstashTCPHandler] = None


def _get_logstash_handler() -> Optional[LogstashTCPHandler]:
    global _logstash_handler
    if _logstash_handler is not None:
        return _logstash_handler
    try:
        from app.core.config import settings as _s
        host = _s.LOGSTASH_HOST or ""
        port = _s.LOGSTASH_PORT
    except Exception:
        host = os.getenv("LOGSTASH_HOST", "")
        port = int(os.getenv("LOGSTASH_PORT", "5010"))
    if host:
        _logstash_handler = LogstashTCPHandler(host, port)
        _logstash_handler.setLevel(logging.INFO)
    return _logstash_handler


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with stdout + optional Logstash forwarding."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(stdout_handler)

        lh = _get_logstash_handler()
        if lh:
            logger.addHandler(lh)

        logger.setLevel(logging.INFO)

    return logger
