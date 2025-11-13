from fastapi import APIRouter, Query
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def load_summary_file(path: Path):
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)

@router.get("/drift_history")
def get_drift_history():
    """
    Returns drift summary history for all available dates.
    Used for line charts and history views.
    """
    history = []

    for file in sorted(SUMMARY_DIR.glob("drift_summary_*.json")):
        data = load_summary_file(file)
        if not data:
            continue
        rows = data.get("rows", [])
        if not rows:
            continue

        # compute averages
        semantic_scores = [r.get("semantic_score") for r in rows if isinstance(r.get("semantic_score"), (int, float))]
        concept_scores = [r.get("test_acc") for r in rows if isinstance(r.get("test_acc"), (int, float))]

        history.append({
            "date": data.get("date"),
            "semantic_drift_score": round(sum(semantic_scores)/len(semantic_scores), 4) if semantic_scores else None,
            "concept_drift_score": round(sum(concept_scores)/len(concept_scores), 4) if concept_scores else None
        })

    return {"history": history}
