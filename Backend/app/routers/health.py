"""
Health and status routes for DRINKOO API.
Provides observability endpoints.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from backend.config import Config
from backend.database import check_db_health
from backend.auth import TokenData
from backend.dependencies import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["health"])


class HealthStatus(BaseModel):
    status: str
    timestamp: str
    api_version: str
    environment: str
    database: dict
    rag_ready: bool


class StatusResponse(BaseModel):
    api_health: str
    database_health: dict
    rag_ready: bool
    timestamp: str


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Check API health status."""
    try:
        db_health = check_db_health()
        
        rag_ready = (
            Config.OPENROUTER_API_KEY is not None and
            db_health["status"] == "healthy"
        )
        
        return HealthStatus(
            status="healthy" if db_health["status"] == "healthy" else "degraded",
            timestamp=datetime.utcnow().isoformat(),
            api_version=Config.API_VERSION,
            environment=Config.ENV,
            database=db_health,
            rag_ready=rag_ready
        )
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            api_version=Config.API_VERSION,
            environment=Config.ENV,
            database={"status": "unknown", "message": str(e)},
            rag_ready=False
        )


@router.get("/status", response_model=StatusResponse)
async def status_check(current_user: Optional[TokenData] = Depends(get_current_user_optional)):
    """Get detailed status information."""
    try:
        db_health = check_db_health()
        
        rag_ready = (
            Config.OPENROUTER_API_KEY is not None and
            db_health["status"] == "healthy"
        )
        
        api_health = "healthy" if db_health["status"] == "healthy" else "degraded"
        
        logger.info(f"Status check: {api_health}")
        
        return StatusResponse(
            api_health=api_health,
            database_health=db_health,
            rag_ready=rag_ready,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Status check error: {e}")
        return StatusResponse(
            api_health="unhealthy",
            database_health={"status": "unknown", "message": str(e)},
            rag_ready=False,
            timestamp=datetime.utcnow().isoformat()
        )


@router.get("/version")
async def get_version():
    """Get API version."""
    return {
        "version": Config.API_VERSION,
        "api_title": Config.API_TITLE,
        "environment": Config.ENV
    }
