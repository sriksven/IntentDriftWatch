from fastapi import APIRouter, Query
from pathlib import Path
import json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
SUMMARY_DIR = BASE_DIR / "reports" / "generated" / "summaries"

@router.get("/alert_status")
def get_alert_status(
    date: str = Query(None, description="Specific date YYYY-MM-DD"),
    time_range: str = Query("7d", description="Time range (24h, 7d, 30d)")
):
    """
    Returns alert-level status based on drift summary (latest or specific date).
    """
    if date:
        target_file = SUMMARY_DIR / f"drift_summary_{date}.json"
        if not target_file.exists():
            return {"status": "No data", "alerts": []}
        with open(target_file) as f:
            data = json.load(f)
    else:
        files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
        if not files:
            return {"status": "No data", "alerts": []}
        
        latest_file = files[-1]
        with open(latest_file) as f:
            data = json.load(f)

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

    return {"status": "Drift Detected" if alerts else "Stable", "alerts": alerts}
