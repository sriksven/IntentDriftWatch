import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health():
    r = client.get("/")
    assert r.status_code == 200

def test_latest_summary():
    r = client.get("/latest_summary")
    assert r.status_code == 200
