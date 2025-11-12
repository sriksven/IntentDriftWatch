from fastapi import APIRouter
from pathlib import Path
import json, os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

SUMMARY_DIR = Path("/Users/sriks/Documents/Projects/IntentDriftWatch/drift_reports/summaries")

SEMANTIC_THR = float(os.getenv("SEMANTIC_DRIFT_THRESHOLD", "0.35"))
ACC_DROP_THR = float(os.getenv("CONCEPT_ACC_DROP_THRESHOLD", "0.08"))

@router.get("/alert_status")
def alert_status():
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return {"has_alert": False, "alerts": []}
    with open(files[-1]) as f:
        summary = json.load(f)
    alerts = []
    for row in summary.get("rows", []):
        sem = row.get("semantic_score")
        acc = row.get("accuracy_drop")
        if (sem and sem >= SEMANTIC_THR) or (acc and abs(acc) >= ACC_DROP_THR):
            alerts.append(row)
    return {"has_alert": bool(alerts), "alerts": alerts, "date": summary.get("date")}
