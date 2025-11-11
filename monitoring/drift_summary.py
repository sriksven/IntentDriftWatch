"""
Aggregate semantic and concept drift JSONs into a single daily summary.
Outputs:
- monitoring/drift_summary_<date>.json
- monitoring/drift_summary_<date>.csv
"""

import os, json, csv, datetime as dt
from glob import glob
from pathlib import Path

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
    Path("monitoring").mkdir(exist_ok=True)
    today = dt.datetime.utcnow().strftime("%Y-%m-%d")

    semantic = load_jsons("drift_reports/semantic/*.json")
    concept = load_jsons("drift_reports/concept/*.json")

    # Index by (topic, new_date)
    sem_idx = {(s["topic"], s["new_date"]): s for s in semantic if "topic" in s}
    con_idx = {(c["topic"], c["new_date"]): c for c in concept if "topic" in c}

    rows = []
    topics = set([k[0] for k in sem_idx.keys()]) | set([k[0] for k in con_idx.keys()])
    dates = set([k[1] for k in sem_idx.keys()]) | set([k[1] for k in con_idx.keys()])
    latest_date = sorted(dates)[-1] if dates else today

    for t in sorted(topics):
        s = sem_idx.get((t, latest_date))
        c = con_idx.get((t, latest_date))
        row = {
            "topic": t,
            "date": latest_date,
            "semantic_status": s["status"] if s else "N/A",
            "semantic_score": s["drift_score"] if s else None,
            "cosine_drift": s["cosine_drift"] if s else None,
            "jsd_drift": s["jsd_drift"] if s else None,
            "concept_status": c["status"] if c else "N/A",
            "test_acc": c["test_acc"] if c else None,
            "test_f1": c["test_f1"] if c else None,
            "accuracy_drop": c["accuracy_drop"] if c else None,
        }
        rows.append(row)

    # Write JSON
    jpath = f"monitoring/drift_summaries/drift_summary_{latest_date}.json"
    with open(jpath, "w") as f:
        json.dump({"generated_at": today, "date": latest_date, "rows": rows}, f, indent=2)

    # Write CSV
    cpath = f"monitoring/drift_summaries/drift_summary_{latest_date}.csv"
    with open(cpath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)

    print(f"Summary written to {jpath} and {cpath}")

if __name__ == "__main__":
    main()
