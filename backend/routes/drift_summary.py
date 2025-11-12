from fastapi import APIRouter
from pathlib import Path
import json

router = APIRouter()

# Dynamically resolve the project root no matter where this runs
BASE_DIR = Path(__file__).resolve().parents[2]
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

@router.get("/latest_summary")
def get_latest_summary():
    """
    Returns the most recent drift summary JSON from drift_reports/summaries.
    """
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return {"error": f"No summaries found in {SUMMARY_DIR}"}

    latest_file = files[-1]
    with open(latest_file) as f:
        data = json.load(f)
    return data
