from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Existing routes
from backend.routes.drift_summary import router as drift_summary_router
from backend.routes.alert_status import router as alert_router
from backend.routes.semantic_drift import router as semantic_router
from backend.routes.concept_drift import router as concept_router

# New routes
from backend.routes.drift_history import router as drift_history_router
from backend.routes.topic_history import router as topic_history_router
from backend.routes.embeddings import router as embeddings_router
from backend.routes.embeddings_info import router as emb_info_router
from backend.routes.embeddings_topic import router as emb_topic_router
from backend.routes.drift_details import router as drift_details_router

app = FastAPI(
    title="IntentDriftWatch API",
    version="2.0",
    description="Backend API for IntentDriftWatch Dashboard"
)

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # in production restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(drift_summary_router)
app.include_router(alert_router)
app.include_router(semantic_router)
app.include_router(concept_router)
app.include_router(drift_history_router)
app.include_router(topic_history_router)
app.include_router(embeddings_router)
app.include_router(emb_info_router)
app.include_router(emb_topic_router)
app.include_router(drift_details_router)

from fastapi.staticfiles import StaticFiles
import os

# Mount static reports
# backend/app.py -> backend/ -> drift_reports/ is at parent sibling
# Correct path resolution:
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT_DIR = os.path.join(BASE_DIR, "drift_reports")

if os.path.exists(REPORT_DIR):
    app.mount("/drift_reports", StaticFiles(directory=REPORT_DIR), name="drift_reports")
else:
    print(f"Warning: Report directory not found at {REPORT_DIR}")

@app.get("/")
def root():
    return {"message": "IntentDriftWatch backend is live", "version": "2.0"}
