import sqlite3
import logging
from pathlib import Path
from Backend import config

logger = logging.getLogger(__name__)

_db_path: str = config.DATABASE_PATH


def set_db_path(path: str) -> None:
    """Override database path (used in tests for in-memory SQLite)."""
    global _db_path
    _db_path = path


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute_query(sql: str, params: tuple = ()) -> list[dict]:
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def execute_one(sql: str, params: tuple = ()) -> dict | None:
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def execute_write(sql: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE; returns lastrowid."""
    with get_db() as conn:
        cursor = conn.execute(sql, params)
        conn.commit()
        return cursor.lastrowid


def init_db() -> None:
    schema_path = Path("Database/schema.sql")
    if not schema_path.exists():
        logger.warning("schema.sql not found at %s", schema_path)
        return
    sql = schema_path.read_text()
    if _db_path != ":memory:":
        Path(_db_path).parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.executescript(sql)
        conn.commit()
    logger.info("Database initialised from schema.sql")
