"""
Health Check Routes

This module contains all health check related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.models.schemas import HealthResponse, DetailedHealthResponse
from app.services.database_service import DatabaseService
from app.utils.logger import get_logger
from app.core.config import settings
import httpx
import asyncpg
import psutil


router = APIRouter()
logger = get_logger(__name__)


async def get_database_service() -> DatabaseService:
    """
    Dependency to get database service instance.
    """
    return DatabaseService(
        primary_url=settings.DATABASE_URL,
        replica_url=settings.REPLICA_URL
    )


@router.get("/", response_model=HealthResponse)
async def health_check(service: DatabaseService = Depends(get_database_service)):
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status of the service
    """
    try:
        health = await service.health_check()
        
        return HealthResponse(
            status=health["overall"],
            message=f"Service is {health['overall']}",
            components=health
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(service: DatabaseService = Depends(get_database_service)):
    """
    Detailed health check endpoint.
    
    Returns:
        Comprehensive health status including all components
    """
    try:
        # Get database health
        health = await service.health_check()
        
        # Get detailed status
        status = await service.get_status()
        
        # Get system metrics
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": list(psutil.getloadavg()),
            "uptime": psutil.boot_time()
        }
        
        # Check external services
        external_services = {}
        
        # Check Prometheus
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://prometheus:9090/-/healthy", timeout=2)
                external_services["prometheus"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            external_services["prometheus"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Grafana
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://grafana:3000/api/health", timeout=2)
                external_services["grafana"] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
        except Exception as e:
            external_services["grafana"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        return DetailedHealthResponse(
            status=health["overall"],
            message=f"Detailed health check completed",
            components=health,
            database=status.get("primary", {}),
            system=system_metrics,
            external_services=external_services,
            monitoring={
                "status": "running",
                "last_check": health["timestamp"]
            },
            recovery={
                "status": "ready",
                "auto_recovery_enabled": True
            },
            metrics={
                "status": "collecting",
                "last_collection": health["timestamp"]
            }
        )
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@router.post("/check", response_model=HealthResponse)
async def force_health_check(service: DatabaseService = Depends(get_database_service)):
    """
    Force an immediate health check.
    
    Returns:
        Health status after forcing a check
    """
    try:
        logger.info("Forcing health check...")
        health = await service.health_check()
        
        return HealthResponse(
            status=health["overall"],
            message="Forced health check completed",
            components=health
        )
    except Exception as e:
        logger.error(f"Forced health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")


@router.get("/dependencies")
async def check_dependencies():
    """
    Check health of all external dependencies.
    
    Returns:
        Status of all external services
    """
    dependencies = {}
    
    # Check PostgreSQL Primary
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        dependencies["postgresql_primary"] = {"status": "healthy"}
    except Exception as e:
        dependencies["postgresql_primary"] = {"status": "unhealthy", "error": str(e)}
    
    # Check PostgreSQL Replica
    try:
        conn = await asyncpg.connect(settings.REPLICA_URL)
        await conn.execute("SELECT 1")
        await conn.close()
        dependencies["postgresql_replica"] = {"status": "healthy"}
    except Exception as e:
        dependencies["postgresql_replica"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Prometheus
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://grafana:3000/api/health", timeout=2)
            dependencies["prometheus"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            }
    except Exception as e:
        dependencies["prometheus"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Grafana
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://grafana:3000/api/health", timeout=2)
            dependencies["grafana"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            }
    except Exception as e:
        dependencies["grafana"] = {"status": "unhealthy", "error": str(e)}
    
    return dependencies
