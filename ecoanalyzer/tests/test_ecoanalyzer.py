from ecoanalyzer.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "ecoanalyzer"
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analysis():
    response = client.get("/analysis")

    assert response.status_code == 200

    data = response.json()

    assert "result" in data

    assert data["result"]["co2"] == 42
    assert data["result"]["energy"] == 120
    assert data["result"]["efficiency"] == "good"