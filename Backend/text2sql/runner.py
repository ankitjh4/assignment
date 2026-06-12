"""Read-only SQL execution helper."""
from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import text

from ..database import session_scope


def run_select(sql: str, params: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    with session_scope() as session:
        result = session.execute(text(sql), params or {})
        rows = result.mappings().all()
        return [dict(row) for row in rows]


def row_signature(rows: List[Dict[str, Any]], keys: List[str]) -> List[tuple]:
    sig: List[tuple] = []
    for row in rows:
        sig.append(tuple(row.get(key) for key in keys))
    return sorted(sig, key=lambda t: tuple(str(v) for v in t))
