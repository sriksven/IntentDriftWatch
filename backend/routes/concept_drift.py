from fastapi import APIRouter, Query
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def load_summary_by_date(date_str: str = None):
    if date_str:
        target_file = SUMMARY_DIR / f"drift_summary_{date_str}.json"
        if target_file.exists():
            with open(target_file) as f:
                return json.load(f)
        return None
    else:
        files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
        if not files:
            return None
        with open(files[-1]) as f:
            return json.load(f)

@router.get("/concept_drift")
def get_concept_drift(
    date: str = Query(None, description="Specific date YYYY-MM-DD"),
    time_range: str = Query("7d", description="Time range (24h, 7d, 30d)")
):
    data = load_summary_by_date(date)
    if not data:
        return {"items": []}

    rows = data.get("rows", [])

    items = []
    for r in rows:
        items.append({
            "feature": r.get("topic"),
            "test_name": "accuracy_drop",
            "statistic": r.get("accuracy_drop"),
            "p_value": None,
            "is_drifting": r.get("concept_status") not in ["Stable", "N/A"]
        })

    return {"items": items}
