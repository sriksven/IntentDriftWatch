from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def load_latest_summary():
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)

@router.get("/concept_drift")
def get_concept_drift():
    data = load_latest_summary()
    if not data:
        return {"items": []}

    rows = data.get("rows", [])

    items = []
    for r in rows:
        items.append({
            "feature": r.get("topic"),
            "test_name": "accuracy_drop",
            "statistic": r.get("accuracy_drop"),
            "p_value": None,                   # Not part of your concept drift pipeline
            "is_drifting": r.get("concept_status") not in ["Stable", "N/A"]
        })

    return {"items": items}
