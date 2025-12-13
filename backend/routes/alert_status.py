from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

@router.get("/alert_status")
def get_alert_status():
    """
    Returns alert-level status based on latest drift summary.
    """
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return {"status": "No data", "alerts": []}

    latest_file = files[-1]
    with open(latest_file) as f:
        data = json.load(f)

    alerts = []
    alerts = []
    for row in data.get("rows", []):
        sem_status = row.get("semantic_status")
        con_status = row.get("concept_status")
        
        # Check Semantic Drift
        if sem_status in ["Drift Detected", "Moderate Drift", "Significant Drift"]:
            severity = "critical" if sem_status == "Significant Drift" else "warning"
            alerts.append({
                "severity": severity,
                "timestamp": data.get("date", "N/A"),
                "message": f"Semantic drift detected in '{row.get('topic')}': {sem_status}"
            })

        # Check Concept Drift
        if con_status in ["Drift Detected", "Moderate Drift", "Significant Drift"]:
            severity = "critical" if con_status == "Significant Drift" else "warning"
            alerts.append({
                "severity": severity,
                "timestamp": data.get("date", "N/A"),
                "message": f"Concept drift detected in '{row.get('topic')}': {con_status}"
            })

    # Return list directly or wrapped? Frontend expects { alerts: [...] } based on Dashboard.jsx:
    # setAlerts(alertsJson.alerts || alertsJson || []);
    return {"status": "Drift Detected" if alerts else "Stable", "alerts": alerts}
