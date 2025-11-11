import os
import json
from pathlib import Path
from dotenv import load_dotenv
from mailer import send_mail

load_dotenv()

BASE_DIR = "/Users/sriks/Documents/Projects/IntentDriftWatch"
SUMMARY_DIR = f"{BASE_DIR}/drift_reports/summaries"

SEMANTIC_THR = float(os.getenv("SEMANTIC_DRIFT_THRESHOLD", "0.35"))
ACC_DROP_THR = float(os.getenv("CONCEPT_ACC_DROP_THRESHOLD", "0.08"))

def load_latest_summary():
    p = Path(SUMMARY_DIR)
    if not p.exists():
        return None
    files = sorted(p.glob("drift_summary_*.json"))
    if not files:
        return None
    with open(files[-1]) as f:
        return json.load(f)

def find_alerts(summary):
    if not summary or "rows" not in summary:
        return []
    alerts = []
    for row in summary["rows"]:
        sem = row.get("semantic_score")
        acc = row.get("accuracy_drop")
        if (sem is not None and sem >= SEMANTIC_THR) or \
           (acc is not None and abs(acc) >= ACC_DROP_THR):
            alerts.append(row)
    return alerts

def format_email(alerts, date):
    lines = [f"🚨 IntentDriftWatch Alert — {date}", "", "Topics exceeding thresholds:"]
    for a in alerts:
        lines.append(f"- {a['topic']}: semantic={a.get('semantic_score')}  accuracy_drop={a.get('accuracy_drop')}")
    return "\n".join(lines)

def main():
    summary = load_latest_summary()
    if not summary:
        print("No drift summary found.")
        return
    alerts = find_alerts(summary)
    if not alerts:
        print("No alerts triggered.")
        return

    date = summary.get("date")
    body = format_email(alerts, date)
    subject = f"[IntentDriftWatch] Drift alert for {date} ({len(alerts)} topic(s))"
    send_mail(subject, body)

if __name__ == "__main__":
    main()
