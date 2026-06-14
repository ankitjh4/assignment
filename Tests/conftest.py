"""Shared pytest fixtures for DRINKOO tests."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add Backend to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "Backend"))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_drinkoo.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

from database import Base, get_db  # noqa: E402
from main import app  # noqa: E402

TEST_DB_URL = "sqlite:///./test_drinkoo.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables at the start of the test session, drop at the end."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    db_file = Path("test_drinkoo.db")
    if db_file.exists():
        db_file.unlink()


@pytest.fixture()
def db():
    """Fresh DB session for each test, rolled back after."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSession(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """FastAPI TestClient with the test DB injected."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_client(client):
    """TestClient with a registered + logged-in user. Returns (client, token)."""
    client.post("/api/auth/signup", json={
        "email": "testuser@drinkoo.com",
        "password": "TestPass123!",
        "full_name": "Test User",
    })
    resp = client.post(
        "/api/auth/login",
        data={"username": "testuser@drinkoo.com", "password": "TestPass123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = resp.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client, token
