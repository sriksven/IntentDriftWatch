# IntentDriftWatch
**End-to-End Local MLOps System for Detecting Semantic and Concept Drift in Trending Topics**

---

## Overview

IntentDriftWatch is a fully local, production-grade MLOps system that monitors both **semantic drift** (how topic meaning changes over time) and **concept drift** (how model performance degrades due to that change). The system continuously collects multi-source data, computes embeddings, detects drift, and triggers retraining workflows.

---

## Objectives

1. Identify changes in the meaning of topics over time using unsupervised embeddings.
2. Quantify the effect of semantic drift on model accuracy (concept drift).
3. Automate the full workflow of collection, processing, embedding, drift analysis, and retraining.
4. Provide UI dashboards for both drift types using FastAPI and React.

---

## Core Components

| Component | Description |
|------------|-------------|
| **Semantic Drift** | Unsupervised detection of meaning change between embeddings across time windows. |
| **Concept Drift** | Supervised detection of model performance degradation using XGBoost trained on topic embeddings. |
| **Data Collectors** | Fetches real-world data from Reddit, Wikipedia, RSS feeds, and X. |
| **Drift Analytics** | Computes cosine, JSD, and accuracy decay metrics for interpretation. |
| **Pipelines** | Orchestrates the end-to-end execution using modular scripts. |

---

## Architecture Overview

```
               ┌───────────────────────────┐
               │      Data Collectors      │
               │ Reddit | Wiki | RSS | X   │
               └───────────────────────────┘
                          │
                          ▼
               ┌───────────────────────────┐
               │     Combine + Clean       │
               │ Text normalization + merge│
               └───────────────────────────┘
                          │
                          ▼
               ┌───────────────────────────┐
               │  Embedding Generation     │
               │ SentenceTransformer (MiniLM)│
               └───────────────────────────┘
                          │
               ┌────────────┴────────────┐
               ▼                         ▼
   ┌────────────────────┐     ┌─────────────────────┐
   │  Semantic Drift     │     │  Concept Drift      │
   │  (Cosine, JSD)      │     │  (Accuracy decay)   │
   └────────────────────┘     └─────────────────────┘
                          │
                          ▼
               ┌───────────────────────────┐
               │ Visualization & Alerts    │
               │ React Dashboard | Kibana  │
               └───────────────────────────┘
```

---

## Semantic Drift Visualization (Unsupervised)

- Measures change in topic embeddings across time snapshots.
- Uses **Cosine Distance** and **Jensen–Shannon Divergence** to capture both direction and distributional drift.
- Output: JSON reports in `/drift_reports/`.

### Example Visualization (to be shown in React Dashboard)

| Topic | Cosine Drift | JSD Drift | Drift Score | Status |
|--------|---------------|------------|--------------|---------|
| Artificial Intelligence | 0.22 | 0.18 | 0.20 | Stable |
| Cryptocurrency | 0.47 | 0.44 | 0.46 | Drift Detected |

---

## Concept Drift Visualization (Supervised)

- Trains **XGBoost** on embeddings as a baseline classifier.
- Tests the same model on newer embeddings to track performance decay.
- Accuracy decline over time indicates concept drift.

### Example Visualization

| Date | Mean Semantic Drift | Model Accuracy | Status |
|------|----------------------|----------------|---------|
| 2025-11-06 | 0.12 | 0.88 | Stable |
| 2025-11-07 | 0.27 | 0.75 | Minor Drift |
| 2025-11-08 | 0.42 | 0.63 | Drift Detected |

---

## Data Flow Summary

| Stage | Input | Output | Module |
|--------|--------|----------|---------|
| Data Collection | Reddit/Wiki/RSS | Raw JSON | `data_pipeline/data_collectors/*` |
| Combining | Raw JSONs | Merged topic data | `combine_sources.py` |
| Cleaning | Merged data | Normalized text | `clean_combined_data.py` |
| Embedding | Cleaned text | Vector representations (.npy) | `generate_embeddings.py` |
| Semantic Drift | Embedding pairs | Drift scores | `analytics/drift_utils.py` |
| Concept Drift | Embeddings + labels | Accuracy metrics | `models/train_xgb.py` |

---

## Updated Project Structure

```
IntentDriftWatch/
├── analytics/
│   └── drift_utils.py
│
├── api/
│   ├── model_store/
│   └── utils/
│       └── embeddings.py
│
├── data_pipeline/
│   ├── data/
│   │   ├── raw/
│   │   │   ├── reddit/
│   │   │   ├── wiki/
│   │   │   ├── news/
│   │   │   └── x/
│   │   └── processed/
│   │       ├── cleaned/
│   │       ├── combined/
│   │       └── embeddings/
│   ├── data_collectors/
│   ├── utils/
│   ├── clean_combined_data.py
│   ├── combine_sources.py
│   └── generate_embeddings.py
│
├── drift_reports/
│
├── models/
│   └── train_xgb.py
│
├── logging/
│   ├── alerts/
│   └── logs/
│
├── monitoring/
│
├── pipelines/
│   └── full_pipeline.py
│
├── notebooks/
│   └── exploration.ipynb
│
├── requirements.txt
├── .env
└── README.md
```

---

## Usage

### Step 1: Setup

```bash
pip install -r requirements.txt
touch .env
# Add Reddit API keys and credentials
```

### Step 2: Run Full Pipeline

```bash
python -m pipelines.full_pipeline
```

### Step 3: Run Only Drift Analysis

```bash
python -m analytics.drift_utils
```

### Step 4: Train or Evaluate XGBoost Classifier

```bash
python -m models.train_xgb
```

---

## Recent Additions and Implementation Details

This section documents the latest implemented features and how to operate them in a reproducible way.

### Aggregated Drift Summaries

A daily summary aggregates both semantic and concept drift JSONs into a single artifact for visualization and alerting.

- Location of script  
  `drift_reports/aggregate_drift_summary.py`

- Inputs  
  `drift_reports/semantic/*.json`  
  `drift_reports/concept/*.json`

- Outputs  
  `drift_reports/summaries/drift_summary_<date>.json`  
  `drift_reports/summaries/drift_summary_<date>.csv`

- Behavior  
  The script indexes reports by topic and date, selects the latest date across available files, and constructs a table of rows with semantic drift metrics and concept drift metrics. After writing the summary files, it triggers the email alert check.

### Automated Email Alerts over SMTP

Email alerts are sent when drift exceeds configured thresholds. This works with any SMTP provider. For Gmail you must use an App Password.

- Script locations  
  `alerting/mailer.py`  
  `alerting/alert_trigger.py`

- Environment configuration in `.env`  
  ```
SEMANTIC_DRIFT_THRESHOLD=0.35
CONCEPT_ACC_DROP_THRESHOLD=0.08

MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM="IntentDriftWatch <your_email@gmail.com>"
MAIL_TO="recipient1@example.com, recipient2@example.com"
  ```

- Execution paths  
  1. Run the full pipeline or directly run `aggregate_drift_summary.py`.  
  2. The summary script writes the latest summary JSON and CSV.  
  3. The summary script calls `alert_trigger.py`, which loads the latest summary, checks thresholds, and sends email if necessary.

- Typical error and fix  
  If Gmail returns 535 with Username and Password not accepted, enable 2 Step Verification in your Google account, create an App Password for Mail, and use that app password in `MAIL_PASSWORD`.

### Data Formats

Defining the expected JSON fields allows downstream systems to validate inputs and build robust visualizations.

- Semantic report JSON fields (per topic and date)  
  ```
{
  "topic": "string",
  "new_date": "YYYY-MM-DD",
  "status": "Stable|Drift Detected|Minor Drift",
  "drift_score": float,
  "cosine_drift": float,
  "jsd_drift": float
}
  ```

- Concept report JSON fields (per topic and date)  
  ```
{
  "topic": "string",
  "new_date": "YYYY-MM-DD",
  "status": "Stable|Drift Detected|Minor Drift",
  "test_acc": float,
  "test_f1": float,
  "accuracy_drop": float
}
  ```

- Summary JSON schema  
  ```
{
  "generated_at": "YYYY-MM-DD",
  "date": "YYYY-MM-DD",
  "rows": [
    {
      "topic": "string",
      "date": "YYYY-MM-DD",
      "semantic_status": "string",
      "semantic_score": float|null,
      "cosine_drift": float|null,
      "jsd_drift": float|null,
      "concept_status": "string",
      "test_acc": float|null,
      "test_f1": float|null,
      "accuracy_drop": float|null
    }
  ]
}
  ```

### Logging and Reproducibility

- Each run writes timestamped outputs under `drift_reports` and `logging/logs`.  
- MLflow integration can store experiment parameters and metrics for semantic drift and concept drift.  
- Evidently report files can be generated and saved alongside summaries for deeper offline inspection.

---

## Backend Plan left to do

A minimal FastAPI service will expose the aggregated artifacts for the dashboard and any external monitoring system.

### Proposed Endpoints

- `GET /latest_summary`  
  Returns the most recent `drift_summary_<date>.json` content as JSON.

- `GET /alert_status`  
  Loads the latest summary and re-applies threshold rules to return a compact list of active alerts per topic. Used by the frontend banner.

- `GET /semantic_drift?topic=<name>&n=<k>`  
  Returns a simple time series of semantic drift metrics for a topic. Uses available historical files if present.

- `GET /concept_drift?topic=<name>&n=<k>`  
  Returns time series of accuracy and f1 with optional accuracy drop values.

### Hosting Approach

- Host on Render, Railway, Fly, or Deta at free tier.  
- The service reads the `drift_reports/summaries` directory and does not require a separate database.  
- For public dashboards, allow read-only endpoints. If you later need protection, add an API key header check.

---

## Frontend Plan left to do

A React and Vite dashboard will visualize both semantic and concept drift, and surface alerts.

### Key Views

- Overview page with status banner, last updated time, and a per topic table of the latest summary.  
- Semantic Drift page with a line chart of cosine drift and JSD drift.  
- Concept Drift page with model accuracy and f1 trend, with annotations when thresholds are breached.

### Data Fetch and Refresh

- The frontend polls `GET /latest_summary` every 30 seconds for incremental updates.  
- Optionally add a WebSocket or Server Sent Events endpoint in the backend for push-based updates later.

### Hosting

- Host static build on GitHub Pages or Vercel.  
- Set Vite `base` path to the repository name when deploying to GitHub Pages.  
- Configure the frontend to call the deployed backend URL instead of localhost.

---

## CI and CD Plan left to do

Once backend and frontend stabilize, introduce a GitHub Actions pipeline for quality checks, smoke tests, and artifact archiving.

### Pipeline Objectives

1. Lint and style checks using black and flake8.  
2. Unit and integration tests using pytest.  
3. Execute a minimal drift run to produce a summary.  
4. Upload the summary JSON as a workflow artifact.  
5. Later, optionally commit the summary to a reports branch for history.  
6. Later, optionally trigger retraining when drift exceeds threshold.

### Suggested Test Cases

- Unit tests  
  - `analytics/drift_utils.py`: verify cosine and JSD computations on known toy vectors.  
  - Data validators: assert incoming JSON shape for semantic and concept reports.  
  - Threshold checks: given a synthetic summary, verify that alerting logic flags the correct topics.

- Integration tests  
  - End-to-end smoke: run an ultra-small pipeline that produces one semantic and one concept report, then run the aggregator and check that the summary contains expected keys.  
  - API tests: when backend is added, hit `/latest_summary` and assert status code and fields.

- Fixtures and data  
  - Provide minimal sample raw inputs and small embedding arrays so the test runtime stays under seconds.  
  - Provide one or two precomputed semantic and concept JSONs for deterministic checks.

### Secrets and Configuration

- Store SMTP credentials as repository secrets in GitHub.  
- Thresholds can be provided through environment variables.  
- Cache Python dependencies to speed up repeated runs.  
- Protect main branch by requiring the CI checks to pass before merging.

---

## Troubleshooting

- Gmail SMTP returns 535 Username and Password not accepted  
  - Enable 2 Step Verification in your Google account.  
  - Generate an App Password for Mail and use it as `MAIL_PASSWORD`.

- No alerts are sent  
  - Verify that the latest summary exists in `drift_reports/summaries`.  
  - Verify that `MAIL_TO` is not empty.  
  - Verify that thresholds are set low enough for your test data to trigger alerts.

- Frontend loads but shows no data  
  - Confirm the backend URL is reachable from the browser.  
  - Confirm CORS settings on the backend if you restrict origins.  
  - Check that summaries are present on the server filesystem.

---

## Future Extensions

- Integrate Airflow for DAG-based orchestration.  
- Enable retraining trigger when drift exceeds threshold.  
- Push reports to MLflow and Evidently.  
- Deploy a FastAPI service exposing drift summaries.  
- Create React and Vite dashboard for both drift types.  
- Add Slack webhook alerts in parallel with SMTP if desired.  
- Add Grafana or Kibana panels for long-term drift trend monitoring.

---

## Summary

IntentDriftWatch now combines both unsupervised semantic drift and supervised concept drift detection in a unified and modular local MLOps environment. The project offers a complete simulation of real-world data evolution monitoring and model retraining pipelines used in modern search and recommendation systems. The latest additions include an aggregated daily summary and automated email alerts over SMTP. The remaining work focuses on hosting a lightweight FastAPI backend, delivering a React and Vite dashboard, and introducing CI and CD with strong tests and artifact archiving.
