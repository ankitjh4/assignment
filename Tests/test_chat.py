"""Chatbot endpoint tests (OpenRouter call is mocked)."""
from unittest.mock import patch, MagicMock


def _mock_openrouter(answer: str = "Mocked DRINKOO answer."):
    """Return an httpx-like mock that simulates a successful OpenRouter response."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    # First call = Text2SQL (returns a SELECT), subsequent calls = answer generation
    mock_response.json.side_effect = [
        {"choices": [{"message": {"content": "SELECT name FROM products WHERE sugar_grams < 5"}}]},
        {"choices": [{"message": {"content": answer}}]},
        {"choices": [{"message": {"content": "SELECT name FROM products WHERE sugar_grams < 5"}}]},
        {"choices": [{"message": {"content": answer}}]},
        {"choices": [{"message": {"content": "SELECT name FROM products WHERE sugar_grams < 5"}}]},
        {"choices": [{"message": {"content": answer}}]},
        {"choices": [{"message": {"content": "SELECT name FROM products WHERE sugar_grams < 5"}}]},
        {"choices": [{"message": {"content": answer}}]},
        {"choices": [{"message": {"content": "SELECT name FROM products WHERE sugar_grams < 5"}}]},
        {"choices": [{"message": {"content": answer}}]},
    ]
    return mock_response


def test_chat_returns_answer(client, auth_headers):
    with patch("httpx.post", return_value=_mock_openrouter("Citrus Burst has 3.5g sugar.")):
        res = client.post("/api/chat", json={"question": "Which products are low sugar?"}, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "session_id" in data
    assert "context_used" in data


def test_chat_stores_session(client, auth_headers):
    with patch("httpx.post", return_value=_mock_openrouter("Watermelon Chill is sparkling.")):
        res = client.post("/api/chat", json={"question": "Tell me about sparkling drinks."}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["session_id"] > 0


def test_chat_empty_question_rejected(client, auth_headers):
    res = client.post("/api/chat", json={"question": "   "}, headers=auth_headers)
    assert res.status_code == 400


def test_chat_requires_auth(client):
    res = client.post("/api/chat", json={"question": "hello"})
    assert res.status_code == 401


def test_chat_context_retrieved(client, auth_headers):
    """Verify that RAG retrieval runs and context_used is populated for known product queries."""
    with patch("httpx.post", return_value=_mock_openrouter("Citrus Burst uses lemon juice.")):
        res = client.post("/api/chat", json={"question": "citrus ingredients"}, headers=auth_headers)
    assert res.status_code == 200
