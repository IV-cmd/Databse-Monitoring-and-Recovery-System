"""
API Router for Version 1

This module combines all v1 API routes into a single router.
"""

from fastapi import APIRouter
from app.api.v1.routes import health, monitoring, recovery, metrics

# Create API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    monitoring.router,
    prefix="/monitoring",
    tags=["Monitoring"]
)

api_router.include_router(
    recovery.router,
    prefix="/recovery",
    tags=["Recovery"]
)

api_router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Metrics"]
)
