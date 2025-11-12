from fastapi import APIRouter, Query
from pathlib import Path
import json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

@router.get("/semantic_drift")
def get_semantic_drift(
    topic: str = Query(..., description="Topic name"),
    n: int = Query(10, description="Number of latest records")
):
    """
    Returns semantic drift trend for a given topic across recent summaries.
    """
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return {"topic": topic, "trend": []}

    trend = []
    for f in files[-n:]:
        try:
            with open(f) as json_file:
                data = json.load(json_file)
                for row in data.get("rows", []):
                    if row.get("topic") == topic:
                        trend.append({
                            "date": row.get("date"),
                            "semantic_score": row.get("semantic_score"),
                            "cosine_drift": row.get("cosine_drift"),
                            "jsd_drift": row.get("jsd_drift"),
                            "semantic_status": row.get("semantic_status")
                        })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue

    return {"topic": topic, "trend": trend}
