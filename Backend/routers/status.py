"""Health and deep status endpoints."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Request
from sqlalchemy import text

from ..config import get_settings
from ..database import session_scope
from ..logging_config import get_logger

router = APIRouter(prefix="/api", tags=["status"])
LOG = get_logger("drinkoo.status")
SETTINGS = get_settings()


@router.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "service": SETTINGS.app_name, "version": SETTINGS.app_version}


def _db_check() -> Dict[str, Any]:
    try:
        with session_scope() as session:
            products = session.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
            users = session.execute(text("SELECT COUNT(*) FROM users")).scalar() or 0
        return {"ok": True, "products": int(products), "users": int(users)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _rag_check(request: Request) -> Dict[str, Any]:
    index = getattr(request.app.state, "rag_index", None)
    if not index:
        return {"ok": False, "documents": 0}
    return {"ok": True, "documents": len(index.documents)}


def _llm_check() -> Dict[str, Any]:
    return {
        "configured": SETTINGS.has_openrouter_key,
        "model": SETTINGS.openrouter_model,
        "base_url": SETTINGS.openrouter_base_url,
        "mode": "openrouter" if SETTINGS.has_openrouter_key else "offline-fallback",
    }


@router.get("/status")
def deep_status(request: Request) -> Dict[str, Any]:
    db = _db_check()
    rag = _rag_check(request)
    llm = _llm_check()
    overall = db["ok"] and rag["ok"]
    return {
        "status": "ok" if overall else "degraded",
        "service": SETTINGS.app_name,
        "version": SETTINGS.app_version,
        "environment": SETTINGS.environment,
        "components": {
            "api": {"ok": True},
            "database": db,
            "rag": rag,
            "llm": llm,
        },
    }
