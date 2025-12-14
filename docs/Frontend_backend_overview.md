# IntentDriftWatch – UI and Backend Overview

This document explains only the **UI and Backend features**, how they work, how data flows through the system, and what each component measures. This is not the full project README. It is a focused technical overview of the monitoring application.

---

## 1. Purpose of the System

IntentDriftWatch monitors how topics change over time using two types of drift:

1. **Semantic Drift**  
   Measures change in meaning by comparing embedding vectors across snapshot dates.

2. **Concept Drift**  
   Measures if the classification behavior of the model changes between past and present data.

The platform provides:

- Daily drift analysis
- Per-topic history
- Alerting
- Embedding snapshot exploration
- Visual comparison through charts and tables

---

## 2. Backend (FastAPI)

The backend exposes structured JSON APIs that power every part of the UI.

### 2.1 Responsibilities

- Load drift summary  
- Return semantic drift metrics  
- Return concept drift metrics  
- Return alerts  
- Provide embedding metadata  
- Provide historical drift per topic  

All drift computations happen offline in the data pipeline.  
The backend only reads processed files and serves them.

---

## 3. Backend Endpoints and Their Roles

### `GET /drift_summary`
Returns the latest daily drift summary:
- Semantic drift score (global)
- Concept drift score (global)
- Alert count
- Topics monitored
- Summary date

Used by:
- Dashboard summary cards

---

### `GET /semantic_drift?time_range=&model=`
Returns semantic drift items for each topic:
- drift_score  
- delta_freq  
- p_value  

Used by:
- Semantic Drift table  
- DriftCharts semantic line

---

### `GET /concept_drift?time_range=&model=`
Returns concept drift metrics:
- test_name  
- statistic  
- p_value  
- accuracy_drop  
- is_drifting  

Used by:
- Concept Drift table  
- DriftCharts concept line

---

### `GET /alert_status`
Returns alert history:
- severity  
- timestamp  
- message  

Used by:
- Alerts panel on Dashboard

---

### `GET /embeddings/info`
Returns:
- All available topics  
- All snapshot dates  

Used by:
- ExplorePage topic grid

---

### `GET /embeddings/{topic}`
Returns:
- List of embedding files across dates
- Dates
- Paths
- Links to semantic and concept drift HTML reports

Used by:
- ExplorePage topic details panel

---

### `GET /topic_history/{topic}`
Returns:
- Daily semantic drift timeline
- Daily concept drift accuracy timeline
- Per-date metrics table

Used by:
- TopicModal charts and metrics table

---

## 4. UI (Vite + React)

The UI visualizes all drift data and provides three main pages.

```
UI Structure
src/
 ├── components/
 │    ├── NavBar.jsx
 │    ├── ThemeToggle.jsx
 │    ├── DriftCharts.jsx
 │    └── TopicModal.jsx
 ├── pages/
 │    ├── Dashboard.jsx
 │    ├── ExplorePage.jsx
 │    └── SettingsPage.jsx
 └── styles/
      └── App.css
```

---

## 5. UI Pages and Components

### 5.1 Dashboard

The main monitoring view.  
Fetches four backend endpoints simultaneously.

Contains:

1. **Summary Cards**
   - Semantic drift score
   - Concept drift score
   - Topics monitored
   - Alert count

2. **DriftCharts Component**
   - Semantic drift line
   - Concept drift line
   - Shows drift relationship between topics

3. **Semantic Drift Table**
   - drift_score  
   - delta_freq  
   - p_value  
   - Click a row to open TopicModal

4. **Concept Drift Table**
   - statistic  
   - p_value  
   - test_name  
   - drift status  
   - Click a row to open TopicModal

5. **Alerts Panel**
   - severity
   - timestamp
   - alert message

6. **TopicModal**
   - Appears when a topic row is clicked

Dashboard auto-refreshes using the interval from Settings.

---

### 5.2 TopicModal

Displays complete historical drift for a topic.

Provides:

- Semantic Drift Over Time chart
- Concept Drift (Accuracy Drop) Over Time chart
- Per-date metrics table

Modal closes when clicking outside or pressing the close button.

---

### 5.3 ExplorePage

Lets users browse embedding snapshots.

Features:

- Topic grid (one card per topic)
- Date count per topic
- On click, loads all snapshots for that topic
- Links to:
  - semantic drift HTML report  
  - concept drift HTML report  
- Useful for audit and debugging model changes

---

### 5.4 SettingsPage

Allows runtime configuration:

- API base URL
- Auto-refresh interval
- Theme toggle (light and dark)
- Stores settings in localStorage

Everything updates instantly without page reloads.

---

## 6. Data Flow Summary

1. Pipelines generate embeddings and drift JSON files.
2. Backend routes read the latest processed results.
3. UI fetches data on:
   - Page load
   - User actions (topic click)
   - Auto-refresh
4. UI components render:
   - Charts
   - Tables
   - Alerts
   - Modals
5. Explore page gives direct access to drift HTML reports.

The system is intentionally decoupled. The backend never computes drift; it only serves structured metadata.

---

## 7. What This System Measures

- How much embeddings change across dates (semantic drift)
- Whether model behavior has shifted (concept drift)
- Frequency changes in topics across snapshots
- Statistical tests on feature distributions
- Accuracy differences caused by shifts
- Whether drift severity justifies alerting
- Availability and consistency of embeddings
- Per-topic historical changes
- Audit trails through HTML drift reports

---

## 8. Summary

This documentation covers only the UI and backend architecture.  
Together, they form a complete monitoring interface enabling:

- Drift detection
- Historical analysis
- Snapshot comparison
- Semantic interpretation of shifts
- Concept-level analysis of model stability

The design is modular, transparent, and suitable for production MLOps workflows.

