from fastapi import APIRouter, Query
from pathlib import Path
import json

router = APIRouter()

SUMMARY_DIR = Path("/Users/sriks/Documents/Projects/IntentDriftWatch/drift_reports/summaries")

@router.get("/concept_drift")
def get_concept_drift(topic: str = Query(..., description="Topic name"),
                      n: int = Query(10, description="Number of latest records")):
    """
    Returns concept drift (accuracy, f1, accuracy_drop) trend for a given topic.
    """
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    if not files:
        return {"topic": topic, "trend": []}

    trend = []
    for f in files[-n:]:
        try:
            data = json.load(open(f))
            for row in data.get("rows", []):
                if row.get("topic") == topic:
                    trend.append({
                        "date": row.get("date"),
                        "test_acc": row.get("test_acc"),
                        "test_f1": row.get("test_f1"),
                        "accuracy_drop": row.get("accuracy_drop"),
                        "concept_status": row.get("concept_status")
                    })
        except Exception:
            pass
    return {"topic": topic, "trend": trend}
