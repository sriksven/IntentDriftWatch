from monitoring.drift_summary import load_jsons

def test_load_jsons():
    samples = load_jsons("drift_reports/summaries/*.json")

    assert isinstance(samples, list)
    assert samples, "No summary JSON files found. Run the summary generator first."

    assert isinstance(samples[0], dict)
