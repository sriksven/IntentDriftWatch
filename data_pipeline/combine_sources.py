"""
Module: combine_sources.py
Purpose: Merge Reddit, Wikipedia, and RSS data for each topic
(intentionally skipping X for now)
into a unified combined dataset under data/processed/combined/.
"""

import os
import json
import datetime as dt
import logging
from glob import glob
from data_pipeline.utils.io_utils import save_json, ensure_dir
from data_pipeline.update_metadata import update_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RAW_PATHS = {
    "reddit": "data/raw/reddit",
    "wiki": "data/raw/wiki",
    # "x": "data/raw/x",  # temporarily disabled
    "rss": "data/raw/news"
}

def load_texts_from_json(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("texts", [])
    except Exception as e:
        logger.error(f"Failed to read {path}: {e}")
        return []

def combine_topic_data(topic: str):
    """Merge all available source files for a topic into one combined dataset."""
    combined_texts = []
    found_sources = []

    for source, dir_path in RAW_PATHS.items():
        pattern = os.path.join(dir_path, f"{topic.replace(' ', '_')}_*.json")
        files = glob(pattern)
        if not files:
            continue
        latest_file = sorted(files)[-1]  # pick the latest by date
        texts = load_texts_from_json(latest_file)
        if texts:
            combined_texts.extend(texts)
            found_sources.append(source)

    if not combined_texts:
        logger.warning(f"No data found for topic '{topic}' in any source.")
        return None

    ensure_dir("data/processed/combined")
    combined_data = {
        "topic": topic,
        "sources": found_sources,
        "collected_at": str(dt.datetime.utcnow()),
        "total_texts": len(combined_texts),
        "texts": combined_texts
    }

    filename = f"{topic.replace(' ', '_')}_combined_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
    path = os.path.join("data/processed/combined", filename)
    save_json(combined_data, path)
    update_metadata(topic, "combined", path)

    logger.info(f"✅ Combined data for '{topic}' from {found_sources} → {path}")
    return path


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
        combine_topic_data(t)
