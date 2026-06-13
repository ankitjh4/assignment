"""Health / status endpoint tests."""


def test_status_returns_200(client):
    res = client.get("/api/status")
    assert res.status_code == 200


def test_status_structure(client):
    res = client.get("/api/status")
    data = res.json()
    required_keys = {"api_healthy", "database_connected", "rag_ready", "version", "environment", "timestamp"}
    assert required_keys.issubset(data.keys()), f"Missing keys: {required_keys - data.keys()}"


def test_status_api_healthy(client):
    res = client.get("/api/status")
    assert res.json()["api_healthy"] is True


def test_status_database_connected(client):
    res = client.get("/api/status")
    assert res.json()["database_connected"] is True


def test_status_no_auth_required(client):
    """Status endpoint must be public."""
    res = client.get("/api/status")
    assert res.status_code != 401


def test_status_has_version(client):
    res = client.get("/api/status")
    assert res.json()["version"]


def test_status_has_timestamp(client):
    res = client.get("/api/status")
    ts = res.json().get("timestamp", "")
    assert "T" in ts or "-" in ts  # ISO format
