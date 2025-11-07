
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

## Dashboard Plans

### Semantic Drift Dashboard
- Displays drift scores per topic per date.
- Line graph of cosine drift over time.
- Color-coded status (green=stable, red=drifted).

### Concept Drift Dashboard
- Shows model accuracy trend.
- Plots semantic drift vs model accuracy correlation.
- Displays alerts when accuracy drops beyond threshold.

---

## Future Extensions

- Integrate Airflow for DAG-based orchestration.
- Enable retraining trigger when drift exceeds threshold.
- Push reports to MLflow and Evidently.
- Deploy a FastAPI service exposing drift summaries.
- Create React/Vite dashboard for both drift types.

---

## Summary

IntentDriftWatch now combines both unsupervised (semantic) and supervised (concept) drift detection in a unified, modular, and locally executable MLOps environment. The project offers a complete simulation of real-world data evolution monitoring and model retraining pipelines used in modern search and recommendation systems.
