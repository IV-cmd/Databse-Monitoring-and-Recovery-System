"""
Recovery Routes

This module contains all recovery related API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import asyncio
import asyncpg

from app.models.schemas import (
    RecoveryRequest, 
    RecoveryResponse, 
    RecoveryHistoryResponse,
    RecoveryStatusEnum
)
from app.services.database_service import DatabaseService
from app.services.recovery_service import RecoveryService
from app.repositories.recovery_repo import RecoveryRepository
from app.utils.logger import get_logger
from app.core.config import settings
from prometheus_client import Counter, Histogram, Gauge


router = APIRouter()
logger = get_logger(__name__)


# Prometheus metrics for recovery operations
RECOVERY_REQUESTS_TOTAL = Counter(
    'recovery_requests_total',
    'Total number of recovery requests',
    ['type', 'severity', 'status']
)

RECOVERY_DURATION = Histogram(
    'recovery_duration_seconds',
    'Time spent performing recovery operations',
    ['type', 'severity']
)

ACTIVE_RECOVERIES = Gauge(
    'active_recoveries',
    'Number of currently active recovery operations'
)

RECOVERY_SUCCESS_RATE = Gauge(
    'recovery_success_rate',
    'Success rate of recovery operations'
)


# Global recovery repository and service instances
recovery_repo = RecoveryRepository()
recovery_service = RecoveryService(recovery_repo)


async def get_database_service() -> DatabaseService:
    """
    Dependency to get database service instance.
    """
    return DatabaseService(
        primary_url=settings.DATABASE_URL,
        replica_url=settings.REPLICA_URL
    )


async def verify_recovery_auth(authorization: Optional[str] = Header(None)) -> bool:
    """
    Verify recovery operation authorization.
    """
    if not settings.RECOVERY_AUTH_REQUIRED:
        return True
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Recovery operations require authentication",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify Bearer token
    if authorization.startswith("Bearer "):
        token = authorization[7:]
        if token == settings.RECOVERY_BEARER_TOKEN:
            return True
    
    raise HTTPException(
        status_code=401,
        detail="Invalid recovery authentication token",
        headers={"WWW-Authenticate": "Bearer"}
    )




@router.post("/start", response_model=RecoveryResponse)
async def start_recovery(
    request: RecoveryRequest,
    background_tasks: BackgroundTasks,
    service: DatabaseService = Depends(get_database_service),
    authenticated: bool = Depends(verify_recovery_auth)
):
    """
    Start a recovery operation with production-grade validation and tracking.
    
    Args:
        request: Recovery operation details
        background_tasks: FastAPI background tasks
        
    Returns:
        Recovery operation response
    """
    with RECOVERY_DURATION.labels(type=request.type, severity=request.severity).time():
        RECOVERY_REQUESTS_TOTAL.labels(type=request.type, severity=request.severity, status="started").inc()
        
        try:
            # Validate recovery request
            await recovery_service.validate_recovery_request(request)
            
            # Generate unique recovery ID
            recovery_id = str(uuid.uuid4())
            
            # Log recovery request with security context
            logger.info(f"Starting recovery {recovery_id}: {request.type} - {request.reason}")
            
            # Create recovery record in database
            recovery_record = await recovery_service.create_recovery_record(
                recovery_id=recovery_id,
                request=request,
                max_attempts=settings.RECOVERY_MAX_ATTEMPTS
            )
            
            # Update active recoveries gauge
            active_count = await recovery_repo.get_active_recoveries_count()
            ACTIVE_RECOVERIES.set(active_count)
            
            # Start recovery in background with proper tracking
            background_tasks.add_task(
                perform_recovery,
                recovery_id,
                service,
                request.dict()
            )
            
            return RecoveryResponse(
                recovery_id=recovery_id,
                status=RecoveryStatusEnum.IN_PROGRESS,
                attempts=0,
                max_attempts=settings.RECOVERY_MAX_ATTEMPTS,
                started_at=recovery_record["started_at"],
                details=recovery_record
            )
            
        except ValueError as e:
            logger.error(f"Invalid recovery request: {e}")
            RECOVERY_REQUESTS_TOTAL.labels(type=request.type, severity=request.severity, status="validation_failed").inc()
            raise HTTPException(status_code=400, detail=f"Invalid recovery request: {str(e)}")
        except asyncpg.PostgresConnectionError as e:
            logger.error(f"Database connection error in recovery start: {e}")
            RECOVERY_REQUESTS_TOTAL.labels(type=request.type, severity=request.severity, status="db_error").inc()
            raise HTTPException(status_code=503, detail="Database service unavailable")
        except Exception as e:
            logger.error(f"Failed to start recovery: {e}")
            RECOVERY_REQUESTS_TOTAL.labels(type=request.type, severity=request.severity, status="error").inc()
            raise HTTPException(status_code=500, detail="Internal server error while starting recovery")


async def perform_recovery(
    recovery_id: str,
    service: DatabaseService,
    request_data: Dict[str, Any]
):
    """
    Perform the actual recovery operation with production-grade error handling.
    
    Args:
        recovery_id: Unique recovery identifier
        service: Database service instance
        request_data: Recovery request data
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"Performing recovery {recovery_id} of type {request_data.get('type')}")
        
        # Update recovery status to in-progress in database
        await recovery_service.update_recovery_status(
            recovery_id, 
            RecoveryStatusEnum.IN_PROGRESS, 
            start_time
        )
        
        # Perform actual recovery based on type
        recovery_type = request_data.get("type")
        
        if recovery_type == "database_failover":
            await recovery_service.perform_database_failover(service, request_data)
        elif recovery_type == "service_restart":
            await recovery_service.perform_service_restart(request_data)
        elif recovery_type == "data_restoration":
            await recovery_service.perform_data_restoration(service, request_data)
        elif recovery_type == "configuration_reset":
            await recovery_service.perform_configuration_reset(request_data)
        else:
            raise ValueError(f"Unsupported recovery type: {recovery_type}")
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Update recovery record with success
        await recovery_service.update_recovery_status(
            recovery_id,
            RecoveryStatusEnum.SUCCESS,
            datetime.utcnow(),
            duration=duration,
            details={"message": "Recovery completed successfully"}
        )
        
        # Update metrics
        RECOVERY_REQUESTS_TOTAL.labels(
            type=recovery_type, 
            severity=request_data.get('severity', 'unknown'), 
            status="success"
        ).inc()
        
        # Update success rate
        await update_success_rate()
        
        # Update active recoveries gauge
        active_count = await recovery_repo.get_active_recoveries_count()
        ACTIVE_RECOVERIES.set(active_count)
        
        logger.info(f"Recovery {recovery_id} completed successfully in {duration:.2f}s")
        
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        logger.error(f"Recovery {recovery_id} failed after {duration:.2f}s: {e}")
        
        # Update recovery record with failure
        try:
            await recovery_service.update_recovery_status(
                recovery_id,
                RecoveryStatusEnum.FAILED,
                datetime.utcnow(),
                duration=duration,
                details={"error": str(e), "error_type": type(e).__name__}
            )
        except Exception as update_error:
            logger.error(f"Failed to update recovery status: {update_error}")
        
        # Update metrics
        RECOVERY_REQUESTS_TOTAL.labels(
            type=request_data.get('type', 'unknown'), 
            severity=request_data.get('severity', 'unknown'), 
            status="failed"
        ).inc()
        
        # Update success rate
        await update_success_rate()
        
        # Update active recoveries gauge
        active_count = await recovery_repo.get_active_recoveries_count()
        ACTIVE_RECOVERIES.set(active_count)


async def update_success_rate():
    """
    Update the recovery success rate gauge.
    """
    try:
        stats = await recovery_repo.get_recovery_statistics()
        if stats["total_recoveries"] > 0:
            success_rate = stats["successful_recoveries"] / stats["total_recoveries"]
            RECOVERY_SUCCESS_RATE.set(success_rate)
        else:
            RECOVERY_SUCCESS_RATE.set(0.0)
    except Exception as e:
        logger.error(f"Failed to update success rate: {e}")


@router.get("/status/{recovery_id}")
async def get_recovery_status(
    recovery_id: str,
    authenticated: bool = Depends(verify_recovery_auth)
):
    """
    Get status of a specific recovery operation from database.
    
    Args:
        recovery_id: Unique recovery identifier
        
    Returns:
        Recovery operation status
    """
    try:
        # Get recovery from database
        recovery = await recovery_repo.get_recovery_by_id(recovery_id)
        
        if not recovery:
            raise HTTPException(status_code=404, detail="Recovery not found")
        
        return recovery
        
    except HTTPException:
        raise
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error in recovery status: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except Exception as e:
        logger.error(f"Failed to get recovery status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving recovery status")


@router.get("/history", response_model=RecoveryHistoryResponse)
async def get_recovery_history(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    authenticated: bool = Depends(verify_recovery_auth)
):
    """
    Get recovery operation history from database with filtering and pagination.
    
    Args:
        page: Page number for pagination
        page_size: Number of items per page
        status: Filter by recovery status
        start_date: Filter by start date
        end_date: Filter by end date
        
    Returns:
        Paginated recovery history
    """
    try:
        # Validate pagination parameters
        if page < 1:
            raise HTTPException(status_code=400, detail="Page number must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
        
        # Get recovery history from database
        history_result = await recovery_repo.get_recovery_history(
            page=page,
            page_size=page_size,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return RecoveryHistoryResponse(
            recoveries=history_result["recoveries"],
            total=history_result["total"],
            page=page,
            page_size=page_size
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Invalid parameters in recovery history: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error in recovery history: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except Exception as e:
        logger.error(f"Failed to get recovery history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while retrieving recovery history")


@router.post("/cancel/{recovery_id}")
async def cancel_recovery(
    recovery_id: str,
    authenticated: bool = Depends(verify_recovery_auth)
):
    """
    Cancel an ongoing recovery operation with proper validation.
    
    Args:
        recovery_id: Unique recovery identifier
        
    Returns:
        Cancellation result
    """
    try:
        # Get recovery from database
        recovery = await recovery_repo.get_recovery_by_id(recovery_id)
        
        if not recovery:
            raise HTTPException(status_code=404, detail="Recovery not found")
        
        if recovery["status"] != RecoveryStatusEnum.IN_PROGRESS:
            raise HTTPException(status_code=400, detail="Recovery is not in progress")
        
        # Cancel recovery through service
        await recovery_service.cancel_recovery(recovery_id)
        
        # Update metrics
        RECOVERY_REQUESTS_TOTAL.labels(
            type=recovery.get("type", "unknown"), 
            severity=recovery.get("severity", "unknown"), 
            status="cancelled"
        ).inc()
        
        # Update active recoveries gauge
        active_count = await recovery_repo.get_active_recoveries_count()
        ACTIVE_RECOVERIES.set(active_count)
        
        logger.info(f"Recovery {recovery_id} cancelled")
        
        return {"success": True, "message": "Recovery cancelled", "recovery_id": recovery_id}
        
    except HTTPException:
        raise
    except asyncpg.PostgresConnectionError as e:
        logger.error(f"Database connection error in recovery cancel: {e}")
        raise HTTPException(status_code=503, detail="Database service unavailable")
    except Exception as e:
        logger.error(f"Failed to cancel recovery: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while cancelling recovery")
