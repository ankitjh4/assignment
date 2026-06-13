"""Authentication and authorization tests."""
import pytest


def test_signup_success(client):
    res = client.post("/api/auth/signup", json={
        "username": "newuser1",
        "email": "newuser1@drinkoo.test",
        "password": "securepass1",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "newuser1"
    assert "password_hash" not in data
    assert "id" in data


def test_signup_duplicate_username(client):
    client.post("/api/auth/signup", json={
        "username": "dupeuser",
        "email": "dupeuser@drinkoo.test",
        "password": "pass1234",
    })
    res = client.post("/api/auth/signup", json={
        "username": "dupeuser",
        "email": "other@drinkoo.test",
        "password": "pass1234",
    })
    assert res.status_code == 400


def test_signup_duplicate_email(client):
    client.post("/api/auth/signup", json={
        "username": "emailuser1",
        "email": "shared@drinkoo.test",
        "password": "pass1234",
    })
    res = client.post("/api/auth/signup", json={
        "username": "emailuser2",
        "email": "shared@drinkoo.test",
        "password": "pass1234",
    })
    assert res.status_code == 400


def test_login_success(client):
    client.post("/api/auth/signup", json={
        "username": "loginuser",
        "email": "loginuser@drinkoo.test",
        "password": "mypassword",
    })
    res = client.post("/api/auth/login", json={
        "username": "loginuser",
        "password": "mypassword",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/api/auth/signup", json={
        "username": "wrongpassuser",
        "email": "wrongpassuser@drinkoo.test",
        "password": "correctpass",
    })
    res = client.post("/api/auth/login", json={
        "username": "wrongpassuser",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_login_unknown_user(client):
    res = client.post("/api/auth/login", json={
        "username": "nobody",
        "password": "nopass",
    })
    assert res.status_code == 401


def test_protected_chat_without_token(client):
    res = client.post("/api/chat", json={"question": "hello"})
    assert res.status_code == 401


def test_protected_upload_without_token(client):
    res = client.post("/api/upload", files={"file": ("test.jpg", b"data", "image/jpeg")})
    assert res.status_code == 401


def test_logout_returns_ok(client):
    res = client.post("/api/auth/logout")
    assert res.status_code == 200
