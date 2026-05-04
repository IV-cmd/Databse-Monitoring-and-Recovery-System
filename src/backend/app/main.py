"""
Simple FastAPI Application
Database monitoring and recovery service.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

app = FastAPI(
    title="Database Monitor Service",
    description="PostgreSQL monitoring and auto-recovery system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Database Monitor Service",
        "version": "1.0.0"
    }
