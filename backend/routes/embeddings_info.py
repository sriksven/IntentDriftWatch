from fastapi import APIRouter
import os
import json

router = APIRouter()

BASE = "data_pipeline/data/processed/embeddings"

@router.get("/embeddings/info")
def embeddings_info():
    if not os.path.exists(BASE):
        return {"topics": [], "dates": []}

    dates = sorted(os.listdir(BASE))
    topics = set()

    for d in dates:
        dpath = os.path.join(BASE, d)
        if not os.path.isdir(dpath):
            continue
        for f in os.listdir(dpath):
            if f.endswith(".npy"):
                topics.add(os.path.splitext(f)[0].replace("_", " "))

    return {"topics": list(topics), "dates": dates}
