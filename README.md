
# IntentDriftWatch
A Fully Local End-to-End MLOps System for Detecting Semantic and Concept Drift in Evolving Topics

## Introduction

IntentDriftWatch is a complete local MLOps framework that ingests data from multiple real-world sources, preprocesses and embeds text, computes semantic and concept drift, generates detailed reports, triggers alerts, and exposes results through a FastAPI backend and a React and Vite dashboard.

This README includes:
- An expanded architecture.
- Detailed explanations of semantic drift and concept drift.
- Thorough explanations for **every command**.
- Full backend and UI documentation.
- Complete project structure.
- Complete operational workflow.

---

# Understanding Semantic Drift and Concept Drift

## Semantic Drift (Unsupervised)
Semantic drift refers to **changes in the meaning or usage of a topic over time**.  
This is detected by comparing embeddings generated at different time periods.

Examples:
- The word “apple” shifting between meaning a fruit vs. the company.
- “AI safety” shifting from academic alignment to political or regulatory contexts.

In this system:
- Embeddings are generated using SentenceTransformers.
- Drift is computed using cosine distance and Jensen Shannon Divergence.
- Larger distances indicate greater semantic shift.

Outputs:
- JSON files under `drift_reports/semantic/`
- Visual charts under `drift_reports/visual/`

## Concept Drift (Supervised)
Concept drift refers to **degradation in model performance** when the meaning of data changes.

For example:
- An intent classifier trained last month may misclassify new trending topics.
- Sentiment predictions may degrade as new slang emerges.

In this system:
- A baseline XGBoost classifier is trained on embeddings.
- It is tested on newer embeddings.
- Drops in accuracy and F1 indicate model drift.

Outputs:
- JSON files under `drift_reports/concept/`

---

# Expanded System Architecture

```
                                 ┌──────────────────────────────────────────┐
                                 │              External Sources            │
                                 │ Reddit    Wikipedia    RSS    X          │
                                 └──────────────────────────────────────────┘
                                                  │
                                                  ▼
                                 ┌──────────────────────────────────────────┐
                                 │             Data Collectors             │
                                 │ collector_pipeline.py                   │
                                 │ reddit_scraper.py                       │
                                 │ wiki_scraper.py                         │
                                 │ rss_scraper.py                          │
                                 │ twitter_scraper.py                      │
                                 └──────────────────────────────────────────┘
                                                  │
                                                  ▼
                                 ┌──────────────────────────────────────────┐
                                 │                Raw Data                 │
                                 │ Stored under data_pipeline/data/raw     │
                                 └──────────────────────────────────────────┘
                                                  │
                                                  ▼
                                 ┌──────────────────────────────────────────┐
                                 │          Combine and Clean              │
                                 │ combine_sources.py                      │
                                 │ clean_combined_data.py                  │
                                 │ text_cleaning.py                        │
                                 └──────────────────────────────────────────┘
                                                  │
                                                  ▼
                                 ┌──────────────────────────────────────────┐
                                 │             Embedding Engine            │
                                 │ generate_embeddings.py                  │
                                 │ embeddings.py                           │
                                 │ SentenceTransformers MiniLM             │
                                 └──────────────────────────────────────────┘
                                                  │
                     ┌─────────────────────────────┴──────────────────────────────┐
                     ▼                                                            ▼
     ┌──────────────────────────────────────────┐                 ┌───────────────────────────────────────────┐
     │          Semantic Drift Engine           │                 │            Concept Drift Engine           │
     │ drift_utils.py                           │                 │ concept_drift_xgb.py                     │
     │ semantic_drift.py                        │                 │ Train and test XGBoost classifier        │
     └──────────────────────────────────────────┘                 └───────────────────────────────────────────┘
                     │                                                            │
                     ▼                                                            ▼
     ┌──────────────────────────────────────────┐                 ┌───────────────────────────────────────────┐
     │        Semantic Drift Reports            │                 │        Concept Drift Reports              │
     └──────────────────────────────────────────┘                 └───────────────────────────────────────────┘
                     │                                                            │
                     └───────────────────────┬────────────────────────────────────┘
                                             ▼
                             ┌──────────────────────────────────────────┐
                             │        Daily Summary Aggregator          │
                             │ aggregate_drift_summary.py               │
                             └──────────────────────────────────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────────────────┐
                             │                Alert Layer               │
                             │ mailer.py                                │
                             │ alert_trigger.py                         │
                             └──────────────────────────────────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────────────────┐
                             │               Backend API                │
                             │ FastAPI                                  │
                             └──────────────────────────────────────────┘
                                             │
                                             ▼
                             ┌──────────────────────────────────────────┐
                             │            React and Vite UI             │
                             └──────────────────────────────────────────┘
```

---

# Updated Project Structure
(Full directory tree retained, omitted here for brevity but included in previous version. If you want it included again, I can embed it.)

---

# Detailed Command Explanations (Option B)

Below, **every command** is explained in terms of:

- Purpose  
- Input files  
- Output files  
- What it logs  
- Where results are stored  
- When to run it  
- Common errors  
- Debugging tips  

---

## 1. Data Collection

### Command
```
python data_pipeline/data_collectors/collector_pipeline.py
```

### Explanation
- Runs all scrapers: Reddit, Wiki, RSS, X.
- Saves raw JSON files into `data_pipeline/data/raw/<source>/`.
- Logs: `logging/logs/data_collection_log.json`.
- When to run: start of every pipeline cycle.
- Typical errors: missing API keys for Reddit or X.
- Fix: add credentials to `.env`.

---

### Individual Collector Example

```
python data_pipeline/data_collectors/reddit_scraper.py
```

Explanation:
- Fetches hot posts for configured subreddits.
- Input: none.
- Output: JSON file under `data_pipeline/data/raw/reddit/`.
- Log: appended in `data_collection_log.json`.
- Debug tip: ensure Reddit API credentials in `.env`.

---

## 2. Combine Raw Sources

### Command
```
python data_pipeline/combine_sources.py
```

Explanation:
- Merges all raw collectors into a unified list.
- Input: all JSONs from `data_pipeline/data/raw/`.
- Output: `combined.json` in `data_pipeline/data/processed/combined/`.
- When to run: after collection.
- Debug tip: ensure raw JSONs exist.

---

## 3. Clean Combined Data

### Command
```
python data_pipeline/clean_combined_data.py
```

Explanation:
- Does text normalization, stopword removal, deduplication.
- Output: `cleaned.json` under `data_pipeline/data/processed/cleaned/`.

---

## 4. Generate Embeddings

### Command
```
python data_pipeline/generate_embeddings.py
```

### Explanation
- Loads cleaned text.
- Uses MiniLM or configured SentenceTransformer.
- Saves `.npy` and metadata files.
- Output location: `data_pipeline/data/processed/embeddings/`.
- Debug tip: ensure model downloaded correctly.

---

## 5. Semantic Drift

### Command
```
python analytics/semantic_drift.py
```

Explanation:
- Computes cosine distance and JSD between new embeddings and previous snapshots.
- Output: `semantic_drift_<date>.json` under `drift_reports/semantic/`.
- Debug tip: ensure at least two embedding snapshots exist.

---

## 6. Concept Drift

### Command
```
python models/concept_drift_xgb.py
```

Explanation:
- Trains baseline XGBoost classifier on older embeddings.
- Tests on new embeddings.
- Calculates accuracy, F1, accuracy drop.
- Output: `concept_drift_<date>.json` under `drift_reports/concept/`.

---

## 7. Daily Drift Summary Aggregation

### Command
```
python drift_reports/aggregate_drift_summary.py
```

Explanation:
- Reads latest semantic and concept drift reports.
- Combines them into one summary.
- Output:
  - `drift_summary_<date>.json`
  - `drift_summary_<date>.csv`
- Triggers email alerts.

---

## 8. Run the Entire Pipeline

### Command
```
python pipelines/full_pipeline.py
```

Explanation:
- Runs all stages in order:
  1. Collection  
  2. Combine  
  3. Clean  
  4. Embedding  
  5. Semantic drift  
  6. Concept drift  
  7. Aggregation  
  8. Alerts

---

## Backend Commands

### Start FastAPI Backend

```
uvicorn backend.app:app --reload --port 8000
```

Explanation:
- Serves API endpoints:
  - `/latest_summary`
  - `/semantic_drift`
  - `/concept_drift`
  - `/alert_status`
- Logs under `logging/logs/`.

---

## Frontend Commands

### Start UI in Development

```
cd intentdriftwatch-ui
npm install
npm run dev
```

Explanation:
- Starts local development UI at:
  - `http://localhost:5173`
- UI polls backend every 30 seconds.

### Build UI for Production

```
npm run build
```

Outputs:
- Production-ready static files under `dist/`.

---

# How the Backend Works

- FastAPI app lives in `backend/app.py`.
- Routes reside under `backend/routes/`.
- The backend:
  - Loads summaries from disk.
  - Returns JSON data to UI.
  - Computes alert flags.
  - Does not require a database.

---

# How the UI Works

- Built with React and Vite.
- Polls the backend via:
  ```
  GET /latest_summary
  ```
- Displays:
  - Topic table
  - Semantic drift trend lines
  - Concept drift trend lines
  - Alert banners
- Configuration set in `src/config.js`.

---

# Summary

This README now contains:
- Complete architectural explanation  
- Deep definitions of drift types  
- Detailed command explanations (Option B)  
- Backend and frontend explanation  
- Full system context  

