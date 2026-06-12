"""SQLAlchemy engine + session + schema bootstrap for DRINKOO."""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from .config import PROJECT_ROOT, get_settings

settings = get_settings()


def _make_engine(url: str) -> Engine:
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, future=True, connect_args=connect_args)


engine: Engine = _make_engine(settings.db_url)


@event.listens_for(engine, "connect")
def _enable_sqlite_fk(dbapi_connection, connection_record):  # noqa: ANN001
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception:
        pass


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _has_table(session: Session, name: str) -> bool:
    row = session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:n"), {"n": name}
    ).fetchone()
    return row is not None


def _exec_sql_script(session: Session, script: str) -> None:
    """Execute a multi-statement SQL script using sqlite raw connection."""
    raw = session.connection().connection
    raw.executescript(script)


def init_db_if_needed() -> None:
    """Apply schema.sql and seed.sql when the DB is empty.

    Idempotent: safe to call on every app startup. Skips work when the `users`
    table already exists AND already has rows.
    """
    schema_path = PROJECT_ROOT / "Database" / "schema.sql"
    seed_path = PROJECT_ROOT / "Database" / "seed.sql"

    db_file_param = settings.db_url.replace("sqlite:///", "", 1)
    if db_file_param and not settings.db_url.endswith(":memory:"):
        Path(db_file_param).parent.mkdir(parents=True, exist_ok=True)

    with session_scope() as session:
        needs_schema = not _has_table(session, "users")
        if needs_schema and schema_path.exists():
            _exec_sql_script(session, _read_sql(schema_path))

        if seed_path.exists():
            count = session.execute(text("SELECT COUNT(*) FROM products")).scalar() or 0
            if count == 0:
                _exec_sql_script(session, _read_sql(seed_path))


def reset_db() -> None:
    """Drop all DRINKOO tables and rebuild them (used by tests and scripts/seed_db.py)."""
    tables = [
        "order_items",
        "orders",
        "product_ingredients",
        "ingredients",
        "promotions",
        "support_articles",
        "chat_sessions",
        "products",
        "users",
    ]
    with session_scope() as session:
        for name in tables:
            session.execute(text(f"DROP TABLE IF EXISTS {name}"))
    init_db_if_needed()
