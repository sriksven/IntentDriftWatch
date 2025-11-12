import json
from pathlib import Path
from models.train_xgb import train_model

THRESHOLD = 0.20

def main():
    summaries = list(Path("drift_reports/summaries").glob("*.json"))
    if not summaries:
        print("No summary files found")
        return

    latest = max(summaries, key=lambda p: p.stat().st_mtime)
    data = json.loads(latest.read_text())

    drift_values = [
        item.get("semantic_drift", 0) for item in data.get("topics", [])
    ]

    if any(d > THRESHOLD for d in drift_values):
        print("Retraining triggered...")
        model_path = train_model()
        print(f"Model retrained and saved to {model_path}")
    else:
        print("No retraining required.")

if __name__ == "__main__":
    main()
