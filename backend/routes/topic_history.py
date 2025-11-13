from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def load_history():
    out = []
    for file in sorted(SUMMARY_DIR.glob("drift_summary_*.json")):
        with open(file) as f:
            out.append(json.load(f))
    return out

@router.get("/topic/{topic_name}/history")
def topic_history(topic_name: str):
    """
    Returns semantic + concept drift over time for one topic.
    """
    data = load_history()
    topic = topic_name.replace("_", " ")

    history = []

    for summary in data:
        for row in summary.get("rows", []):
            if row.get("topic") == topic:
                history.append({
                    "date": summary.get("date"),
                    "semantic_score": row.get("semantic_score"),
                    "cosine_drift": row.get("cosine_drift"),
                    "jsd_drift": row.get("jsd_drift"),
                    "concept_accuracy_drop": row.get("accuracy_drop"),
                    "concept_status": row.get("concept_status")
                })

    return {
        "topic": topic,
        "history": history
    }
