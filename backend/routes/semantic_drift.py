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

@router.get("/semantic_drift")
def get_semantic_drift():
    data = load_latest_summary()
    if not data:
        return {"items": []}

    rows = data.get("rows", [])

    items = []
    for r in rows:
        items.append({
            "topic": r.get("topic"),
            "drift_score": r.get("semantic_score"),
            "delta_freq": None,         # Not part of your pipeline yet
            "cosine_drift": r.get("cosine_drift"),
            "jsd_drift": r.get("jsd_drift"),
            "p_value": None             # Semantic drift does not produce p-values
        })

    return {"items": items}
