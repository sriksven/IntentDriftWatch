from models.concept_drift_xgb import run_concept_drift
import json
from pathlib import Path

THRESHOLD = 0.20

def main():
    summaries = list(Path("drift_reports/summaries").glob("*.json"))
    if not summaries:
        print("No summary files found")
        return

    latest = max(summaries, key=lambda p: p.stat().st_mtime)
    data = json.loads(latest.read_text())

    rows = data.get("rows", [])
    drift_values = [row.get("semantic_score") for row in rows]

    # Safe drift comparison (handles None)
    if any(float(d or 0) > THRESHOLD for d in drift_values):
        print("Retraining triggered...")
        run_concept_drift()
        print("Retraining completed using run_concept_drift()")
    else:
        print("No retraining required.")

if __name__ == "__main__":
    main()
