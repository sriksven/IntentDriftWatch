from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()

SUMMARY_DIR = Path("/Users/sriks/Documents/Projects/IntentDriftWatch/drift_reports/summaries")

@router.get("/latest_summary")
def get_latest_summary():
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return {"error": "No summaries found"}
    latest_file = files[-1]
    with open(latest_file) as f:
        data = json.load(f)
    return data
