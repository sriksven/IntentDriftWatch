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
    for row in data.get("rows", []):
        if (
            row.get("semantic_status") in ["Drift Detected", "Moderate Drift"]
            or row.get("concept_status") in ["Drift Detected", "Moderate Drift"]
        ):
            alerts.append({
                "topic": row.get("topic"),
                "semantic_status": row.get("semantic_status"),
                "concept_status": row.get("concept_status"),
                "semantic_score": row.get("semantic_score"),
                "accuracy_drop": row.get("accuracy_drop")
            })

    if alerts:
        return {"status": "Drift Detected", "alerts": alerts}
    else:
        return {"status": "Stable", "alerts": []}
