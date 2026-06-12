"""Shared pytest fixtures for DRINKOO tests.

Each test session uses a fresh on-disk SQLite database in a temp directory,
seeded from `Database/schema.sql` and `Database/seed.sql`. The FastAPI app
uses lifespan, so the `TestClient` is created via context manager.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterator

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def _temp_workspace() -> Iterator[Path]:
    tmp = Path(tempfile.mkdtemp(prefix="drinkoo-test-"))
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="session", autouse=True)
def _configure_env(_temp_workspace: Path) -> Iterator[None]:
    tmp = _temp_workspace
    (tmp / "Database").mkdir(parents=True, exist_ok=True)
    (tmp / "uploads").mkdir(parents=True, exist_ok=True)
    db_file = tmp / "Database" / "drinkoo_test.db"

    os.environ["DB_URL"] = f"sqlite:///{db_file.as_posix()}"
    os.environ["UPLOAD_DIR"] = str(tmp / "uploads")
    os.environ["APP_SECRET"] = "test-secret-for-pytest-only-32-chars-minimum-x"
    os.environ["ENVIRONMENT"] = "test"
    os.environ["OPENROUTER_API_KEY"] = ""
    os.environ["TESTING"] = "1"

    from Backend.config import get_settings  # noqa: WPS433

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(scope="session")
def app_instance(_configure_env):
    """Build the FastAPI app once per session with fresh config."""
    import importlib
    import Backend.config as cfg_module
    import Backend.database as db_module
    import Backend.deps as deps_module
    import Backend.app as app_module

    importlib.reload(cfg_module)
    importlib.reload(db_module)
    importlib.reload(deps_module)
    importlib.reload(app_module)

    return app_module.app


@pytest.fixture()
def client(app_instance):
    from fastapi.testclient import TestClient

    with TestClient(app_instance) as test_client:
        yield test_client


@pytest.fixture()
def authed_client(client):
    """Sign up + login so subsequent calls carry the session cookie."""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "tester@example.com",
            "password": "PyTest123",
            "full_name": "Pytest User",
        },
    )
    assert response.status_code in (201, 409), response.text
    if response.status_code == 409:
        login = client.post(
            "/api/auth/login",
            json={"email": "tester@example.com", "password": "PyTest123"},
        )
        assert login.status_code == 200, login.text
    return client
