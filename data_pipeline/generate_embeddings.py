"""
Module: feature_engineering.py
Purpose: Generate sentence embeddings from CLEANED topic data using SentenceTransformer.
"""

import os
import json
import datetime as dt
import logging
from glob import glob
from sentence_transformers import SentenceTransformer
import numpy as np
from data_pipeline.utils.io_utils import ensure_dir, save_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load light embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embeddings_for_topic(topic: str):
    """Generate embeddings from cleaned text for a given topic."""
    pattern = os.path.join("data_pipeline/data/processed/cleaned", f"{topic.replace(' ', '_')}_cleaned.json")
    if not os.path.exists(pattern):
        logger.warning(f"No cleaned data found for {topic}")
        return None

    with open(pattern, "r") as f:
        data = json.load(f)

    texts = data.get("texts", [])
    if not texts:
        logger.warning(f"No texts to embed for {topic}")
        return None

    logger.info(f"🔹 Generating embeddings for '{topic}' ({len(texts)} texts)...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    ensure_dir("data_pipeline/data/processed/embeddings")

    npy_path = os.path.join("data_pipeline/data/processed/embeddings", f"{topic.replace(' ', '_')}_embeddings.npy")
    np.save(npy_path, embeddings)

    meta = {
        "topic": topic,
        "timestamp": str(dt.datetime.utcnow()),
        "num_texts": len(texts),
        "embedding_shape": embeddings.shape
    }
    meta_path = os.path.join("data_pipeline/data/processed/embeddings", f"{topic.replace(' ', '_')}_meta.json")
    save_json(meta, meta_path)

    logger.info(f"Saved embeddings for '{topic}' → {npy_path}")
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
