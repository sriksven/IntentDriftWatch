from fastapi import APIRouter, Query
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def load_summary_for_date(date: str = None):
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return None

    if date:
        target = SUMMARY_DIR / f"drift_summary_{date}.json"
        if target.exists():
            with open(target) as f:
                return json.load(f)

    # fallback: latest
    with open(files[-1]) as f:
        return json.load(f)

@router.get("/drift_summary")
def get_drift_summary(date: str = Query(None, description="YYYY-MM-DD")):
    """
    Returns summary for specific date or latest.
    """
    data = load_summary_for_date(date)
    if not data:
        return {"detail": "No summaries exist"}

    rows = data.get("rows", [])
    if not rows:
        return {"detail": "Empty summary"}

    semantic_scores = [r.get("semantic_score") for r in rows if isinstance(r.get("semantic_score"), (int, float))]
    concept_scores = [r.get("test_acc") for r in rows if isinstance(r.get("test_acc"), (int, float))]

    return {
        "date": data.get("date"),
        "semantic_drift_score": round(sum(semantic_scores)/len(semantic_scores), 4) if semantic_scores else None,
        "concept_drift_score": round(sum(concept_scores)/len(concept_scores), 4) if concept_scores else None,
        "topic_count": len(rows),
        "alert_count": len([r for r in rows if r.get("concept_status") not in ["Stable", "N/A"]]),
        "critical_alerts_last_window": len([r for r in rows if r.get("concept_status") == "Significant Drift"])
    }
