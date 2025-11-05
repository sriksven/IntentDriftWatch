"""
Module: clean_combined_data.py
Purpose: Clean and normalize combined topic data before embedding.
"""

import os
import json
import logging
from glob import glob
from data_pipeline.utils.io_utils import ensure_dir, save_json
from data_pipeline.utils.text_cleaning import clean_texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_combined_topic(topic: str):
    """Load combined data, clean texts, and save to processed/cleaned."""
    pattern = os.path.join("data/processed/combined", f"{topic.replace(' ', '_')}_combined_*.json")
    files = sorted(glob(pattern))
    if not files:
        logger.warning(f"No combined data found for {topic}")
        return None

    latest_file = files[-1]
    with open(latest_file, "r") as f:
        data = json.load(f)

    texts = data.get("texts", [])
    if not texts:
        logger.warning(f"No texts to clean for {topic}")
        return None

    cleaned = clean_texts(texts)

    data["texts"] = cleaned
    data["num_cleaned_texts"] = len(cleaned)

    ensure_dir("data/processed/cleaned")
    output_path = os.path.join("data/processed/cleaned", f"{topic.replace(' ', '_')}_cleaned.json")
    save_json(data, output_path)

    logger.info(f"✅ Cleaned data for '{topic}' → {output_path}")
    return output_path


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
        clean_combined_topic(t)
