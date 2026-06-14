"""Health and status endpoint — shows API health, DB connectivity, RAG readiness, and version."""

import logging

from fastapi import APIRouter
from sqlalchemy import text

from config import APP_ENV, APP_VERSION, OPENROUTER_API_KEY, OPENROUTER_MODEL
from database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter(tags=["status"])


@router.get("/status")
def health_check():
    db_status = "ok"
    db_detail = None
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as exc:
        db_status = "error"
        db_detail = str(exc)
        logger.error("DB health check failed: %s", exc)

    rag_ready = bool(OPENROUTER_API_KEY)

    status_payload = {
        "status": "healthy" if db_status == "ok" else "degraded",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "checks": {
            "api": "ok",
            "database": db_status,
            "rag": "ready" if rag_ready else "no-api-key",
            "openrouter_model": OPENROUTER_MODEL,
        },
    }
    if db_detail:
        status_payload["checks"]["database_error"] = db_detail

    return status_payload
