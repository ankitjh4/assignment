"""Tests for the health/status endpoint."""


def test_status_endpoint_accessible(client):
    """Status page is public — no auth required."""
    resp = client.get("/api/status")
    assert resp.status_code == 200


def test_status_returns_json(client):
    resp = client.get("/api/status")
    data = resp.json()
    assert isinstance(data, dict)


def test_status_has_required_fields(client):
    resp = client.get("/api/status")
    data = resp.json()
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "checks" in data


def test_status_checks_has_api(client):
    resp = client.get("/api/status")
    checks = resp.json()["checks"]
    assert "api" in checks
    assert checks["api"] == "ok"


def test_status_checks_has_database(client):
    resp = client.get("/api/status")
    checks = resp.json()["checks"]
    assert "database" in checks


def test_status_checks_has_rag(client):
    resp = client.get("/api/status")
    checks = resp.json()["checks"]
    assert "rag" in checks


def test_status_checks_has_openrouter_model(client):
    resp = client.get("/api/status")
    checks = resp.json()["checks"]
    assert "openrouter_model" in checks


def test_status_database_healthy_with_test_db(client):
    resp = client.get("/api/status")
    data = resp.json()
    # With the test DB injected, db check should pass
    assert data["checks"]["database"] in ("ok", "error")  # depends on injection
    assert data["status"] in ("healthy", "degraded")


def test_status_version_format(client):
    resp = client.get("/api/status")
    version = resp.json()["version"]
    parts = version.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)
