"""
Module: feature_engineering.py
Purpose: Generate sentence embeddings from CLEANED topic data using SentenceTransformer.
"""

import os
import json
import datetime as dt
import logging
from glob import glob
import numpy as np
from sentence_transformers import SentenceTransformer
from data_pipeline.utils.io_utils import ensure_dir, save_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings_for_topic(topic: str):
    """Load the latest cleaned JSON for a topic and generate dated embeddings."""
    pattern = os.path.join(
        "data_pipeline/data/processed/cleaned",
        f"{topic.replace(' ', '_')}_cleaned_*.json"
    )
    files = sorted(glob(pattern))
    if not files:
        logger.warning(f"No cleaned data found for {topic}")
        return None

    latest_file = files[-1]  # pick newest by filename/date
    with open(latest_file, "r") as f:
        data = json.load(f)

    texts = data.get("texts", [])
    if not texts:
        logger.warning(f"No texts to embed for {topic}")
        return None

    logger.info(f"🔹 Generating embeddings for '{topic}' from {os.path.basename(latest_file)} ({len(texts)} texts)...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    # date tag derived from cleaned file name or current date
    date_tag = dt.datetime.utcnow().strftime("%Y-%m-%d")

    emb_dir = os.path.join("data_pipeline", "data", "processed", "embeddings", date_tag)
    ensure_dir(emb_dir)

    npy_path = os.path.join(emb_dir, f"{topic.replace(' ', '_')}.npy")
    np.save(npy_path, embeddings)

    meta = {
        "topic": topic,
        "source_cleaned_file": os.path.basename(latest_file),
        "timestamp": str(dt.datetime.utcnow()),
        "num_texts": len(texts),
        "embedding_shape": embeddings.shape
    }
    meta_path = os.path.join(emb_dir, f"{topic.replace(' ', '_')}_meta.json")
    save_json(meta, meta_path)

    logger.info(f"✅ Saved embeddings for '{topic}' → {npy_path}")
    return npy_path


if __name__ == "__main__":
    topics = [
        "Artificial Intelligence",
        "Climate Change",
        "Space Exploration",
        "Cryptocurrency",
        "Electric Vehicles",
        "Elections"
    ]
    for t in topics:
        generate_embeddings_for_topic(t)
