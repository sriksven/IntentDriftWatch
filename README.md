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
- The word "apple" shifting between meaning a fruit vs. the company.
- "AI safety" shifting from academic alignment to political or regulatory contexts.

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

# Detailed Command Explanations

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
```bash
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

```bash
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
```bash
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
```bash
python data_pipeline/clean_combined_data.py
```

Explanation:
- Does text normalization, stopword removal, deduplication.
- Output: `cleaned.json` under `data_pipeline/data/processed/cleaned/`.

---

## 4. Generate Embeddings

### Command
```bash
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
```bash
python analytics/semantic_drift.py
```

Explanation:
- Computes cosine distance and JSD between new embeddings and previous snapshots.
- Output: `semantic_drift_<date>.json` under `drift_reports/semantic/`.
- Debug tip: ensure at least two embedding snapshots exist.

---

## 6. Concept Drift

### Command
```bash
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
```bash
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
```bash
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

# Backend and Frontend Documentation

## Backend Details

The backend is a FastAPI service that serves drift summaries and analytical artifacts produced by the pipeline. It is fully file‑system based and does not use any external database.

All summaries, semantic drift reports, concept drift reports, and logs are read directly from:

```
drift_reports/semantic/
drift_reports/concept/
drift_reports/summaries/
logging/logs/
```

### Starting the Backend

```bash
uvicorn backend.app:app --reload --port 8000
```

Explanation:
- Serves API endpoints at `http://localhost:8000`
- Automatically reloads on code changes (development mode)
- Logs under `logging/logs/`

---

## Backend API Endpoints

### 1. GET /latest_summary

**Purpose**
- Returns the most recent drift summary JSON file from `drift_reports/summaries`.

**How it works**
- Backend scans the folder for files named:
  ```
  drift_summary_YYYY-MM-DD.json
  ```
- Parses dates
- Selects the newest file
- Returns its full JSON

**Example JSON Response**
```json
{
  "generated_at": "2025-11-12",
  "date": "2025-11-12",
  "rows": [
    {
      "topic": "Artificial Intelligence",
      "date": "2025-11-12",
      "semantic_status": "Stable",
      "semantic_score": 0.18,
      "cosine_drift": 0.20,
      "jsd_drift": 0.16,
      "concept_status": "Stable",
      "test_acc": 0.87,
      "test_f1": 0.84,
      "accuracy_drop": 0.02
    }
  ]
}
```

**Common Errors**
- No summary files present.
  - Fix: run `python drift_reports/aggregate_drift_summary.py` first.

---

### 2. GET /alert_status

**Purpose**
- Performs threshold checks on the latest summary.
- Returns simplified structure containing only alerting topics.

**Example JSON Response**
```json
{
  "alerts": [
    {
      "topic": "Cryptocurrency",
      "type": "semantic",
      "value": 0.52,
      "threshold": 0.35
    }
  ]
}
```

---

### 3. GET /semantic_drift?topic=<name>&n=<k>

**Purpose**
- Returns last k drift records for a named topic.

**Example URL**
```
/semantic_drift?topic=AI&n=10
```

**Example JSON Response**
```json
{
  "topic": "AI",
  "history": [
    {
      "date": "2025-11-09",
      "cosine_drift": 0.21,
      "jsd_drift": 0.13,
      "drift_score": 0.17
    }
  ]
}
```

---

### 4. GET /concept_drift?topic=<name>&n=<k>

**Purpose**
- Returns recent test accuracy, F1, and accuracy drops for a specific topic.

**Example JSON Response**
```json
{
  "topic": "AI",
  "history": [
    {
      "date": "2025-11-09",
      "test_acc": 0.82,
      "test_f1": 0.80,
      "accuracy_drop": 0.05
    }
  ]
}
```

---

## Backend File Selection Strategy

When the backend loads any data:

- It lists all files in the directory.
- Extracts dates from filenames.
- Picks the latest date.
- Loads the file.
- Returns contents as-is.

This keeps the backend stateless and simple.

---

## Backend Logging

Logs are located here:

```
logging/logs/
```

Every request writes:
- Timestamp
- Endpoint hit
- Response status
- Any errors

---

## Backend-to-Frontend Data Flow

```
Frontend (React)
       |
       |  polls every 30 sec
       ▼
Backend (FastAPI)
/latest_summary
       |
       ▼
Reads newest summary from:
drift_reports/summaries/
       |
       ▼
Returns structured JSON
       |
       ▼
UI parses rows and updates:
- tables
- graphs
- alert banner
```

---

# Frontend Details

The frontend is a React and Vite application that continuously fetches drift summaries and visualizes them.

Directory structure:

```
intentdriftwatch-ui/src/
├── App.jsx
├── components/
├── hooks/
├── config.js
└── main.jsx
```

---

## Frontend Commands

### Start UI in Development

```bash
cd intentdriftwatch-ui
npm install
npm run dev
```

Explanation:
- Starts local development UI at `http://localhost:5173`
- UI polls backend every 30 seconds for updates
- Hot module reloading enabled for development

### Build UI for Production

```bash
npm run build
```

Outputs:
- Production-ready static files under `dist/`
- Optimized and minified assets
- Ready for deployment to any static hosting service

---

## How the UI Works

### 1. Fetching Data from Backend

UI polls this endpoint every 30 seconds by default:

```
GET http://localhost:8000/latest_summary
```

Or in production:

```
GET https://intentdriftwatch.onrender.com/latest_summary
```

Configured in:

```javascript
// src/config.js
export const API_BASE = "http://localhost:8000";
// or for production:
// export const API_BASE = "https://intentdriftwatch.onrender.com";
```

---

### 2. UI Data Flow

```
App.jsx
   |
   | fetch latest summary
   ▼
State update (setSummaryData)
   |
   | pass props to child components
   ▼
Dashboard components render
   |
   ├── SummaryTable
   ├── SemanticDriftChart
   ├── ConceptDriftChart
   └── AlertBanner
```

---

### 3. UI Components Explained

#### SummaryTable.jsx
- Displays the latest drift summary in tabular form.
- Columns: topic, semantic score, concept score, status.
- Color-coded status indicators for quick assessment.

#### SemanticDriftChart.jsx
- Plots time series of cosine drift and JSD.
- Interactive tooltips showing exact values.
- Threshold lines for visual reference.

#### ConceptDriftChart.jsx
- Plots accuracy and F1 over time.
- Highlights regions where accuracy drop crosses threshold.
- Shows model performance degradation trends.

#### AlertBanner.jsx
- Shows alert messages returned by `/alert_status`.
- Color-coded by severity (warning/critical).
- Dismissible notifications.

---

### 4. UI Fetch Logic

Example implementation:

```javascript
useEffect(() => {
    async function fetchSummary() {
        const response = await fetch(API_BASE + "/latest_summary");
        const json = await response.json();
        setSummary(json);
    }
    
    // Initial fetch
    fetchSummary();
    
    // Poll every 30 seconds
    const interval = setInterval(fetchSummary, 30000);
    
    // Cleanup on unmount
    return () => clearInterval(interval);
}, []);
```

**Key Features:**
- Automatic polling every 30 seconds
- Error handling for failed requests
- Loading states for better UX
- Cleanup on component unmount

---

### 5. UI Configuration

The UI behavior can be customized in `src/config.js`:

```javascript
export const CONFIG = {
  API_BASE: "http://localhost:8000",
  POLL_INTERVAL: 30000, // milliseconds
  SEMANTIC_THRESHOLD: 0.35,
  CONCEPT_THRESHOLD: 0.10,
  CHART_COLORS: {
    semantic: "#3b82f6",
    concept: "#10b981",
    alert: "#ef4444"
  }
};
```

---

### 6. UI Deployment

To deploy the UI to production:

1. **Build the production bundle:**
   ```bash
   npm run build
   ```

2. **The `dist/` folder contains:**
   - Optimized HTML, CSS, and JavaScript
   - Minified assets
   - Source maps (optional)

3. **Deploy to hosting service:**
   - Vercel: `vercel deploy`
   - Netlify: Drag and drop `dist/` folder
   - GitHub Pages: Push `dist/` contents
   - Any static hosting service

4. **Update API configuration:**
   - Set `API_BASE` in `config.js` to production backend URL
   - Rebuild after configuration changes

---

## Complete System Integration

### How Backend and Frontend Work Together

1. **Pipeline generates drift reports** → stored in `drift_reports/`
2. **Backend reads reports** → exposes via REST API
3. **Frontend polls backend** → fetches latest summaries
4. **UI renders visualizations** → displays drift trends and alerts
5. **Alerts propagate** → from reports → backend → UI → user notification

### Data Freshness

- **Pipeline runs:** Daily (configurable via cron or scheduler)
- **Reports generated:** After each pipeline run
- **Backend updates:** Automatic (reads latest files)
- **Frontend polls:** Every 30 seconds
- **User sees:** Near real-time drift status

---

# Summary

This comprehensive system provides:

**Data Pipeline:**
- Multi-source data collection (Reddit, Wikipedia, RSS, X)
- Automated preprocessing and cleaning
- Embedding generation with SentenceTransformers

**Drift Detection:**
- Semantic drift via cosine distance and JSD
- Concept drift via XGBoost classifier testing
- Automated threshold-based alerting

**Backend:**
- FastAPI REST endpoints
- File-system based (no database required)
- Automatic latest-file selection
- Per-topic historical queries
- Comprehensive logging

**Frontend:**
- React and Vite for modern, fast UI
- Real-time polling (30-second intervals)
- Interactive charts and visualizations
- Alert notifications
- Configurable thresholds and styling

**Complete MLOps Workflow:**
- Fully local execution
- End-to-end automation
- Production-ready deployment
- Scalable architecture
- Extensible design

The system enables continuous monitoring of semantic and concept drift across multiple topics, providing data scientists and ML engineers with actionable insights into model degradation and data distribution shifts over time.