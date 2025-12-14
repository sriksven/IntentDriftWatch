
from fastapi.testclient import TestClient
from backend.app import app
import json

client = TestClient(app)

def debug_drift_summary():
    # 1. Test missing date
    print("Requesting 2025-12-09...")
    res = client.get("/drift_summary?date=2025-12-09")
    print(f"Status: {res.status_code}")
    print(f"Body: {res.json()}")

    # 2. Test valid date
    print("\nRequesting 2025-11-11...")
    res = client.get("/drift_summary?date=2025-11-11")
    print(f"Status: {res.status_code}")
    print(f"Body Key 'date': {res.json().get('date')}")

if __name__ == "__main__":
    debug_drift_summary()
