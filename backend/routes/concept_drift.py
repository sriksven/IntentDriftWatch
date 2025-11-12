from fastapi import APIRouter, Query
from pathlib import Path
import json

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

@router.get("/concept_drift")
def get_concept_drift(
    topic: str = Query(..., description="Topic name"),
    n: int = Query(10, description="Number of latest records")
):
    """
    Returns concept drift (accuracy and F1 trends) for a given topic.
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
                            "test_acc": row.get("test_acc"),
                            "test_f1": row.get("test_f1"),
                            "accuracy_drop": row.get("accuracy_drop"),
                            "concept_status": row.get("concept_status")
                        })
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue

    return {"topic": topic, "trend": trend}
