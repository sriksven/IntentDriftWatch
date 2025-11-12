from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.drift_summary import router as drift_summary_router
from backend.routes.alert_status import router as alert_router
from backend.routes.semantic_drift import router as semantic_router
from backend.routes.concept_drift import router as concept_router


app = FastAPI(title="IntentDriftWatch API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drift_summary_router)
app.include_router(alert_router)
app.include_router(semantic_router)
app.include_router(concept_router)

@app.get("/")
def root():
    return {"message": "IntentDriftWatch backend is live"}
