from fastapi import APIRouter, Query, HTTPException
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def load_summary_by_date(date_str: str = None):
    """
    Load summary for a specific date, or latest if None.
    Returns parsed JSON or None if not found.
    """
    if date_str:
        target_file = SUMMARY_DIR / f"drift_summary_{date_str}.json"
        if target_file.exists():
            with open(target_file) as f:
                return json.load(f)
        return None
    else:
        # Load latest
        files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
        if not files:
            return None
        with open(files[-1]) as f:
            return json.load(f)

@router.get("/semantic_drift")
def get_semantic_drift(
    date: str = Query(None, description="Specific date YYYY-MM-DD"),
    time_range: str = Query("7d", description="Time range (24h, 7d, 30d)")
):
    """
    Get semantic drift table for a specific date (snapshot).
    """
    data = load_summary_by_date(date)
    
    if not data:
        # If a specific date was requested but not found, return empty list (or could 404)
        if date:
             return {"items": []} # Graceful handling for UI
        else:
             return {"items": []}

    rows = data.get("rows", [])

    items = []
    for r in rows:
        items.append({
            "topic": r.get("topic"),
            "drift_score": r.get("semantic_score"),
            "delta_freq": None,
            "cosine_drift": r.get("cosine_drift"),
            "jsd_drift": r.get("jsd_drift"),
            "p_value": None
        })

    return {"items": items}
