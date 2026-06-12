def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "DRINKOO"


def test_status_endpoint(client):
    response = client.get("/api/status")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "degraded"}
    assert body["components"]["database"]["ok"] is True
    assert body["components"]["rag"]["ok"] is True
    assert body["components"]["llm"]["model"] == "nvidia/nemotron-3-ultra-550b-a55b:free"
