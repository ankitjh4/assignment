"""Tests for signup, login, JWT validation, and protected route access."""

import pytest


SIGNUP_PAYLOAD = {
    "email": "auth_test@drinkoo.com",
    "password": "SecurePass99!",
    "full_name": "Auth Tester",
}


def test_signup_creates_user(client):
    resp = client.post("/api/auth/signup", json=SIGNUP_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == SIGNUP_PAYLOAD["email"]
    assert data["full_name"] == SIGNUP_PAYLOAD["full_name"]
    assert "hashed_password" not in data


def test_signup_duplicate_email(client):
    client.post("/api/auth/signup", json=SIGNUP_PAYLOAD)
    resp = client.post("/api/auth/signup", json=SIGNUP_PAYLOAD)
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"].lower()


def test_signup_short_password(client):
    payload = {**SIGNUP_PAYLOAD, "email": "short@drinkoo.com", "password": "abc"}
    resp = client.post("/api/auth/signup", json=payload)
    assert resp.status_code == 422


def test_login_returns_token(client):
    client.post("/api/auth/signup", json=SIGNUP_PAYLOAD)
    resp = client.post(
        "/api/auth/login",
        data={"username": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/auth/signup", json=SIGNUP_PAYLOAD)
    resp = client.post(
        "/api/auth/login",
        data={"username": SIGNUP_PAYLOAD["email"], "password": "WrongPass!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401


def test_me_endpoint_returns_user(auth_client):
    client, _ = auth_client
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "testuser@drinkoo.com"


def test_protected_chat_requires_auth(client):
    resp = client.post("/api/chat", json={"question": "What drinks are low sugar?"})
    assert resp.status_code == 401


def test_protected_upload_requires_auth(client):
    resp = client.post("/api/upload", files={"file": ("test.jpg", b"fake", "image/jpeg")})
    assert resp.status_code == 401


def test_invalid_token_rejected(client):
    client.headers.update({"Authorization": "Bearer invalid.token.here"})
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
