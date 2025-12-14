"""
Aggregate semantic and concept drift JSONs into a single daily summary.

Inputs:
- drift_reports/semantic/*.json
- drift_reports/concept/*.json

Outputs:
- drift_reports/summaries/drift_summary_<date>.json
- drift_reports/summaries/drift_summary_<date>.csv
"""

import os
import json
import csv
import datetime as dt
from glob import glob
from pathlib import Path
import subprocess, sys


BASE_DIR = Path(__file__).resolve().parent.parent
DRIFT_DIR = BASE_DIR / "drift_reports"
SUMMARY_DIR = DRIFT_DIR / "summaries"

def load_jsons(pattern):
    out = []
    for p in glob(pattern):
        try:
            with open(p) as f:
                out.append(json.load(f))
        except Exception:
            pass
    return out

def main():
    Path(SUMMARY_DIR).mkdir(parents=True, exist_ok=True)
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")

    semantic = load_jsons(os.path.join(DRIFT_DIR, "semantic", "*.json"))
    concept = load_jsons(os.path.join(DRIFT_DIR, "concept", "*.json"))

    # Index by (topic, new_date)
    sem_idx = {(s["topic"], s["new_date"]): s for s in semantic if "topic" in s}
    con_idx = {(c["topic"], c["new_date"]): c for c in concept if "topic" in c}

    topics = set([k[0] for k in sem_idx.keys()]) | set([k[0] for k in con_idx.keys()])
    dates = set([k[1] for k in sem_idx.keys()]) | set([k[1] for k in con_idx.keys()])
    
    # Sort dates to ensure consistent processing
    sorted_dates = sorted(dates)
    latest_date = sorted_dates[-1] if sorted_dates else today

    print(f"Found {len(sorted_dates)} unique dates. generating summaries...")

    for d in sorted_dates:
        rows = []
        for t in sorted(topics):
            s = sem_idx.get((t, d))
            c = con_idx.get((t, d))

            # Only include row if we have data for this date
            if not s and not c:
                continue

            row = {
                "topic": t,
                "date": d,
                "semantic_status": s.get("status") if s else "N/A",
                "semantic_score": s.get("drift_score") if s else None,
                "cosine_drift": s.get("cosine_drift") if s else None,
                "jsd_drift": s.get("jsd_drift") if s else None,
                "concept_status": c.get("status") if c else "N/A",
                "test_acc": c.get("test_acc") if c else None,
                "test_f1": c.get("test_f1") if c else None,
                "accuracy_drop": c.get("accuracy_drop") if c else None,
            }
            rows.append(row)

        if not rows:
            continue

        # Write JSON for this date
        jpath = os.path.join(SUMMARY_DIR, f"drift_summary_{d}.json")
        with open(jpath, "w") as f:
            json.dump({"generated_at": today, "date": d, "rows": rows}, f, indent=2)

        # Write CSV for this date
        cpath = os.path.join(SUMMARY_DIR, f"drift_summary_{d}.csv")
        with open(cpath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            
        # print(f"Generated summary for {d}")

    print(f"✅ Generated {len(sorted_dates)} daily summaries in {SUMMARY_DIR}")

    # Trigger email alert check
    ALERT_SCRIPT = BASE_DIR / "alerting" / "alert_trigger.py"
    subprocess.run([sys.executable, str(ALERT_SCRIPT)], check=False)

if __name__ == "__main__":
    main()
