from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_healthy_status():
    response = client.get("/health")
    assert response.json()["status"] == "healthy"


def test_health_returns_version_key():
    response = client.get("/health")
    assert "version" in response.json()
