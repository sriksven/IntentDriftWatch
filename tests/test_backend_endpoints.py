import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health():
    r = client.get("/")
    assert r.status_code == 200
    assert "message" in r.json()


def test_latest_summary():
    r = client.get("/latest_summary")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, dict)
    assert "rows" in data or "date" in data or "generated_at" in data
