"""Shared pytest fixtures for the DRINKOO test suite."""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

# Use a temp file so all sqlite3.connect() calls within a session share the same DB
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_PATH"] = _tmp.name

import Backend.services.db_service as db_service  # noqa: E402
db_service.set_db_path(_tmp.name)

from Backend.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    """TestClient backed by a shared temp-file SQLite database."""
    db_service.init_db()
    with TestClient(app) as c:
        yield c
    os.unlink(_tmp.name)


_auth_counter = [0]


@pytest.fixture()
def auth_headers(client):
    """Sign up a unique test user and return Bearer auth headers."""
    _auth_counter[0] += 1
    username = f"testuser{_auth_counter[0]}"
    email = f"testuser{_auth_counter[0]}@drinkoo.test"
    client.post("/api/auth/signup", json={
        "username": username,
        "email": email,
        "password": "testpassword123",
    })
    res = client.post("/api/auth/login", json={
        "username": username,
        "password": "testpassword123",
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
