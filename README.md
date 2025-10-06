# IntentDriftWatch
# 🧠 IntentDriftWatch  
**End-to-End Local MLOps System for Detecting Semantic Drift in Trending Topics**

---

## 📘 Overview

**IntentDriftWatch** is a fully local, production-style **MLOps project** that tracks how the *meaning and intent* of trending topics change over time.  
It ingests data from **Reddit**, **X (Twitter)**, and **Wikipedia**, computes semantic embeddings, detects drift, and automatically retrains models when intent shifts.

> Think of it as a miniature simulation of Google’s internal “query understanding freshness” pipeline — but built locally with open-source tools.

---

## 🎯 Features

| Capability | Description |
|-------------|--------------|
| **Fully Local** | All components (Airflow, MLflow, FastAPI, ELK, MailHog) run via Docker on localhost |
| **Automated Orchestration** | Airflow DAGs manage data collection, embedding, drift detection, training, and alerts |
| **ML Models** | Uses `SentenceTransformer` for embeddings and `XGBoost` for intent classification |
| **CI / CT / CD** | GitHub Actions workflows for linting, testing, continuous training & deployment |
| **Monitoring Stack** | MLflow (model tracking), Evidently (drift reports), ELK (logs), MailHog (emails) |
| **Feedback Loop** | FastAPI `/feedback` endpoint stores user corrections for retraining |
| **Explainability** | Drift visualized via HTML reports & Kibana dashboards |

---

## 🧩 Architecture

X Trends + Reddit + Wikipedia
│
▼
┌────────────────────┐
│ Airflow DAGs │
│ ├─ collect topics │
│ ├─ collect data │
│ ├─ embed + drift │
│ ├─ train XGBoost │
│ ├─ report + alert │
└────────────────────┘
│
▼
SentenceTransformer (embeddings)
│
▼
XGBoost Classifier → MLflow Tracking
│
▼
Evidently Drift Reports + ELK Dashboards
│
▼
FastAPI Endpoints + Frontend Visualization


---

## 🧮 Models Used

| Component | Model | Purpose |
|------------|--------|----------|
| **Embedding Encoder** | `sentence-transformers/all-MiniLM-L6-v2` | Converts text into 384-dim semantic vectors |
| **Classifier** | `XGBoost` | Predicts or clusters topic intents |
| **Drift Metric** | Cosine Distance / JSD | Detects semantic change over time |

All models run **offline on CPU**.

---

## 🧱 Local Stack

| Service | Tool | Purpose |
|----------|------|----------|
| **Workflow Orchestration** | Apache Airflow | Schedule & execute DAGs |
| **Experiment Tracking** | MLflow | Track drift metrics, models, parameters |
| **Model Serving** | FastAPI | Serve predictions & drift status |
| **Monitoring** | Evidently AI | Generate HTML drift reports |
| **Logging** | ELK Stack (Elastic + Logstash + Kibana) | Log visualization |
| **Email Alerts** | MailHog | Local SMTP notifications |
| **Frontend** | React + Vite | Dashboard for topics, drift, reports |
| **CI / CD** | GitHub Actions | Automated build, test, retrain |

---

## ⚙️ Setup & Run (Local)

### 1️⃣ Clone & Install
```bash
git clone https://github.com/<your-username>/IntentDriftWatch.git
cd IntentDriftWatch


2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Run Docker Compose
docker compose up -d --build

4️⃣ Open Local Services
| Service            | URL                                                      |
| ------------------ | -------------------------------------------------------- |
| Airflow UI         | [http://localhost:8080](http://localhost:8080)           |
| MLflow UI          | [http://localhost:5000](http://localhost:5000)           |
| Kibana             | [http://localhost:5601](http://localhost:5601)           |
| MailHog (emails)   | [http://localhost:8025](http://localhost:8025)           |
| FastAPI docs       | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Frontend dashboard | [http://localhost:5173](http://localhost:5173)           |


🧩 Example Outputs
| Output Type                  | Example                                                                 |
| ---------------------------- | ----------------------------------------------------------------------- |
| **Drift Report (Evidently)** | `monitoring/reports/tesla_drift_2025-10-05.html`                        |
| **MLflow Log**               | `accuracy=0.86`, `drift_score=0.21`                                     |
| **Alert Email (MailHog)**    | “⚠️ Intent Drift Detected for Tesla (0.26)”                             |
| **API Output**               | `{ "topic": "Tesla", "drift_score": 0.26, "status": "Drift Detected" }` |

🔁 CI / CT / CD Workflows
| Workflow                       | Trigger               | Action                                  |
| ------------------------------ | --------------------- | --------------------------------------- |
| **CI**                         | On push               | Lint, test DAGs & API                   |
| **CT (Continuous Training)**   | Weekly or drift alert | Retrain XGBoost                         |
| **CD (Continuous Deployment)** | After new model       | Build + restart local FastAPI container |

```
Project structure(For now)


```bash
IntentDriftWatch/
├── README.md
├── docker-compose.yml
├── requirements.txt
│
├── airflow/
│   ├── dags/
│   │   ├── collect_trending_topics.py
│   │   ├── collect_multisource_data.py
│   │   ├── embed_and_detect_drift.py
│   │   ├── train_xgboost_classifier.py
│   │   ├── generate_drift_report.py
│   │   ├── log_and_alert.py
│   │   └── retrain_pipeline.py
│   ├── Dockerfile
│   └── airflow.cfg
│
├── api/
│   ├── app.py
│   ├── model_store/
│   │   ├── xgboost_model.json
│   │   └── label_encoder.pkl
│   └── utils/
│       └── embeddings.py
│
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       └── components/
│           └── DriftDashboard.jsx
│
├── models/
│   ├── train_xgb.py
│   ├── drift_utils.py
│   └── feature_engineering.py
│
├── data/
│   ├── metadata/
│   │   └── topics_2025-10-05.json
│   ├── raw/
│   │   ├── reddit/
│   │   ├── wiki/
│   │   └── x/
│   ├── processed/
│   │   └── embeddings/
│   └── drift_reports/
│
├── mlflow/
│   └── mlruns/
│
├── monitoring/
│   ├── logstash.conf
│   ├── filebeat.yml
│   └── kibana_dashboards/
│       └── drift_dashboard.json
│
├── logging/
│   ├── logs/
│   └── alerts/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── ct.yml
│       └── cd.yml
│
└── notebooks/
    └── exploration.ipynb
```

