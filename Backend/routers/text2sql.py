"""Protected Text2SQL endpoint."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..deps import require_user
from ..logging_config import get_logger
from ..models import User
from ..text2sql.generator import generate_sql
from ..text2sql.runner import run_select
from ..text2sql.validator import validate

router = APIRouter(prefix="/api/text2sql", tags=["text2sql"])
LOG = get_logger("drinkoo.text2sql")


class Text2SQLRequest(BaseModel):
    question: str = Field(min_length=3, max_length=400)
    execute: bool = True


class Text2SQLResponse(BaseModel):
    question: str
    generated_sql: str
    validated_sql: str
    rows: Optional[List[Dict[str, Any]]] = None
    used_fallback: bool
    issues: List[str] = []


@router.post("", response_model=Text2SQLResponse)
def text_to_sql(payload: Text2SQLRequest, user: User = Depends(require_user)) -> Text2SQLResponse:
    generated = generate_sql(payload.question)
    validation = validate(generated.sql)

    if not validation.ok:
        LOG.warning("text2sql_invalid", extra={"issues": validation.issues, "user_id": user.id})
        return Text2SQLResponse(
            question=payload.question,
            generated_sql=generated.sql,
            validated_sql="",
            rows=None,
            used_fallback=generated.used_fallback,
            issues=validation.issues,
        )

    rows: Optional[List[Dict[str, Any]]] = None
    if payload.execute:
        try:
            rows = run_select(validation.cleaned_sql)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL execution failed: {exc}",
            ) from exc

    LOG.info(
        "text2sql_event",
        extra={
            "user_id": user.id,
            "used_fallback": generated.used_fallback,
            "row_count": (len(rows) if rows is not None else None),
        },
    )

    return Text2SQLResponse(
        question=payload.question,
        generated_sql=generated.sql,
        validated_sql=validation.cleaned_sql,
        rows=rows,
        used_fallback=generated.used_fallback,
        issues=[],
    )
