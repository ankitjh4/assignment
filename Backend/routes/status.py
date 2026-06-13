import logging
from datetime import datetime, timezone

from fastapi import APIRouter

from Backend import config
from Backend.services import db_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["status"])


@router.get("/status")
def status_endpoint():
    # Database health check
    db_connected = False
    try:
        db_service.execute_one("SELECT 1")
        db_connected = True
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)

    # RAG readiness — requires API key
    rag_ready = bool(config.OPENROUTER_API_KEY)

    health = {
        "api_healthy": True,
        "database_connected": db_connected,
        "rag_ready": rag_ready,
        "version": config.APP_VERSION,
        "environment": config.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    logger.info("Status check: db=%s rag=%s", db_connected, rag_ready)
    return health
