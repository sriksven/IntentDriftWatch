from fastapi import APIRouter
import os

router = APIRouter()

BASE = "data_pipeline/data/processed/embeddings"

@router.get("/embeddings/{topic}")
def topic_embeddings(topic: str):
    topic_file = topic.replace(" ", "_")

    out = []
    if not os.path.exists(BASE):
        return {"embeddings": []}

    for d in sorted(os.listdir(BASE)):
        dpath = os.path.join(BASE, d)
        emb_path = os.path.join(dpath, f"{topic_file}.npy")

        if os.path.exists(emb_path):
            out.append({
                "date": d,
                "path": emb_path,
            })

    return {"embeddings": out}
