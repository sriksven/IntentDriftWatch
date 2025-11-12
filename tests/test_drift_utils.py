from drift_reports.aggregate_drift_summary import load_json

def test_load_json():
    sample = load_json("drift_reports/summaries")
    assert isinstance(sample, dict)
