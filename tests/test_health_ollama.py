from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ollama_health_endpoint_shape() -> None:
    response = client.get("/health/ollama")
    payload = response.json()
    assert response.status_code == 200
    assert "status" in payload
    assert "reachable" in payload
    assert "configured" in payload
    assert "chat_model_available" in payload
    assert "embedding_model_available" in payload

