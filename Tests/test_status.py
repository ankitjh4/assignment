def test_status_page_renders(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert "System status" in response.text
    assert "nvidia/nemotron-3-ultra-550b-a55b:free" in response.text


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "DRINKOO" in response.text
    assert "Ask the assistant" in response.text
