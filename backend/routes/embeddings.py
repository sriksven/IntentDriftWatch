from fastapi import APIRouter
import os
import json
import numpy as np
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EMB_DIR = BASE_DIR / "data_pipeline" / "data" / "processed" / "embeddings"
DRIFT_DIR = BASE_DIR / "data_pipeline" / "data" / "processed" / "drift_history"


@router.get("/embeddings/info")
def list_embeddings():
    """
    Lists available dates and topics for embeddings.
    """
    if not EMB_DIR.exists():
        return {"dates": [], "topics": []}

    dates = sorted([
        d for d in os.listdir(EMB_DIR)
        if (EMB_DIR / d).is_dir()
    ])

    topics = set()

    # Collect all topics from all dates
    for d in dates:
        date_dir = EMB_DIR / d
        for f in os.listdir(date_dir):
            if f.endswith(".npy"):
                topic_name = os.path.splitext(f)[0].replace("_", " ")
                topics.add(topic_name)

    return {
        "dates": dates,
        "topics": sorted(topics)
    }


@router.get("/embeddings/{topic_name}")
def get_embedding_metadata(topic_name: str):
    """
    Returns embedding file paths for one topic across dates.
    """
    topic_key = topic_name.replace(" ", "_")
    results = []

    if not EMB_DIR.exists():
        return {"topic": topic_name, "embeddings": []}

    for d in sorted(os.listdir(EMB_DIR)):
        date_dir = EMB_DIR / d
        if not date_dir.is_dir():
            continue

        fname = f"{topic_key}.npy"
        fpath = date_dir / fname

        if fpath.exists():
            results.append({
                "date": d,
                "path": str(fpath)
            })

    return {
        "topic": topic_name,
        "embeddings": results
    }


@router.get("/embeddings/{topic_name}/history")
def get_topic_history(topic_name: str):
    """
    Returns historical drift scores for TopicModal chart.
    Looks for drift_history/{topic}.json
    """
    topic_key = topic_name.replace(" ", "_")
    drift_file = DRIFT_DIR / f"{topic_key}.json"

    if not drift_file.exists():
        return {"topic": topic_name, "history": []}

    with open(drift_file, "r") as f:
        history = json.load(f)

    # Expected format: list of {date: "...", drift: float}
    return {
        "topic": topic_name,
        "history": history
    }
