
# IntentDriftWatch — Local Development Guide

This document provides the minimal set of steps required to run the backend and UI locally during development.

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/IntentDriftWatch.git
cd IntentDriftWatch
```

---

## 2. Create Python Environment (Backend)

```bash
python3 -m venv intentdriftwatch
source intentdriftwatch/bin/activate   # macOS/Linux
intentdriftwatch\Scripts\activate    # Windows
```

---

## 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Prepare Local Data

Make sure the following directories exist:

```
data_pipeline/data/raw
data_pipeline/data/processed/embeddings
drift_reports/summaries
drift_reports/semantic
drift_reports/concept
```

Place your JSON summary files under:

```
drift_reports/summaries/
```

---

## 5. Run Backend Locally

```bash
uvicorn backend.app:app --reload --port 8000
```

The API will run at:

```
http://127.0.0.1:8000
```

---

## 6. Configure Frontend to Use Local Backend

Edit:

```
intentdriftwatch-ui/src/config.js
```

Set:

```js
export const API_BASE_URL = "http://127.0.0.1:8000";
```

---

## 7. Run Frontend (UI)

```bash
cd intentdriftwatch-ui
npm install
npm run dev
```

UI will run here:

```
http://localhost:5173
```

---

## 8. Generate Drift Summaries Locally

To produce new reports:

```bash
python data_pipeline/generate_summaries.py
```

Make sure they land in:

```
drift_reports/summaries/
```

---

## 9. Run Backend Tests

```bash
pytest -q
```

---

## 10. Troubleshooting

### Backend shows CORS errors
Ensure CORS middleware is enabled in:

```
backend/app.py
```

### UI cannot reach backend
Check:
- API URL in Settings page  
- Backend is running  
- No VPN/firewall blocking localhost  

### Summaries not showing
Ensure filenames match:

```
drift_summary_YYYY-MM-DD.json
```

---

## Local Workflow Summary

1. Start backend  
2. Start frontend  
3. Ensure summaries and embeddings exist  
4. UI communicates with http://127.0.0.1:8000  

---

Minimal and fast for local development.
