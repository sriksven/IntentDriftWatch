import json
from pathlib import Path
from monitoring.drift_summary import main as run_summary

def main():
    print("Running smoke test...")

    # Run the summary generator
    run_summary()

    # Find the latest summary file to validate
    summaries_dir = Path("drift_reports/summaries")
    summaries = list(summaries_dir.glob("drift_summary_*.json"))

    assert summaries, "No summary files generated."

    latest = max(summaries, key=lambda p: p.stat().st_mtime)
    data = json.loads(latest.read_text())

    # Basic sanity checks
    assert "rows" in data, "Summary JSON missing 'rows' key."
    assert isinstance(data["rows"], list), "'rows' must be a list."

    print(f"Smoke test OK — summary generated at {latest}")

if __name__ == "__main__":
    main()
