def test_signup_and_login_and_logout(client):
    signup = client.post(
        "/api/auth/signup",
        json={
            "email": "alice@example.com",
            "password": "Sunshine9",
            "full_name": "Alice Drinkoo",
        },
    )
    assert signup.status_code == 201, signup.text
    body = signup.json()
    assert body["email"] == "alice@example.com"
    assert body["role"] == "customer"

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "alice@example.com"

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200

    after = client.get("/api/auth/me")
    assert after.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "Sunshine9"},
    )
    assert login.status_code == 200

    bad = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "Wrongpass1"},
    )
    assert bad.status_code == 401


def test_signup_rejects_weak_password(client):
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "weakuser@example.com",
            "password": "weakpass1",  # has digit but no uppercase letter
            "full_name": "Weak Pass",
        },
    )
    assert response.status_code == 400


def test_protected_route_requires_login(client):
    response = client.post("/api/chat", json={"message": "hello"})
    assert response.status_code == 401
