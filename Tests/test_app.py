from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from Backend.app import app


def unique_email() -> str:
    return f"user{int(time.time() * 1000)}@example.com"


def signup_and_login(client: TestClient) -> str:
    email = unique_email()
    signup_response = client.post(
        "/api/signup",
        json={"email": email, "password": "StrongPass123", "full_name": "Test User"},
    )
    assert signup_response.status_code == 200

    login_response = client.post(
        "/api/login",
        json={"email": email, "password": "StrongPass123"},
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_status_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/status")
        assert response.status_code == 200
        body = response.json()
        assert body["api_health"] == "ok"
        assert body["database_connectivity"] in {"ok", "error"}


def test_auth_and_protected_route() -> None:
    with TestClient(app) as client:
        token = signup_and_login(client)
        me_response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        assert me_response.status_code == 200
        assert "email" in me_response.json()


def test_chat_requires_auth_and_returns_context() -> None:
    with TestClient(app) as client:
        unauthorized = client.post("/api/chat", json={"question": "low sugar products"})
        assert unauthorized.status_code == 401

        token = signup_and_login(client)
        authorized = client.post(
            "/api/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"question": "Which sparkling products are low sugar?", "image_metadata": "none"},
        )
        assert authorized.status_code == 200
        body = authorized.json()
        assert "answer" in body
        assert "retrieved_context" in body


def test_upload_validation_and_success() -> None:
    with TestClient(app) as client:
        token = signup_and_login(client)

        bad_upload = client.post(
            "/api/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("bad.txt", b"abc", "text/plain")},
        )
        assert bad_upload.status_code == 400

        good_upload = client.post(
            "/api/upload",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("sample.png", b"\x89PNG\r\n\x1a\n" + b"0" * 100, "image/png")},
        )
        assert good_upload.status_code == 200
        assert good_upload.json()["content_type"] == "image/png"


def test_schema_has_six_or_more_tables() -> None:
    schema_path = Path(__file__).resolve().parents[1] / "Database" / "schema.sql"
    text = schema_path.read_text(encoding="utf-8").lower()
    assert text.count("create table") >= 6
