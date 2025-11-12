import json
from pathlib import Path
from drift_reports.aggregate_drift_summary import aggregate_summaries

def main():
    print("Running smoke test...")

    # Run aggregator (ensures output is produced)
    output = aggregate_summaries()

    assert output is not None
    assert Path(output).exists()

    print("Smoke test OK")

if __name__ == "__main__":
    main()
