import os

os.environ.setdefault("DATABASE_URL", "postgresql://invalid:invalid@127.0.0.1:1/none")

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok_structure() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "version" in data
    assert data["database"] in ("connected", "unreachable", "unchecked")
