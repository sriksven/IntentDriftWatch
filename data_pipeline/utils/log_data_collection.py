"""
Module: log_data_collection.py
Purpose: Log data collection events (topic, source, file path, timestamp)
         to a central JSON log for monitoring and reproducibility.
"""

import os
import json
import datetime as dt
import logging
from data_pipeline.utils.io_utils import ensure_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LOG_PATH = "logging/logs/data_collection_log.json"

def log_collection_event(topic: str, source: str, path: str):
    """Append a new record to the data collection log."""
    ensure_dir(os.path.dirname(LOG_PATH))
    record = {
        "topic": topic,
        "source": source,
        "path": path,
        "timestamp": str(dt.datetime.utcnow())
    }

    # Load existing log if present
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []

    existing.append(record)

    with open(LOG_PATH, "w") as f:
        json.dump(existing, f, indent=2)

    logger.info(f"🧾 Logged data collection for '{topic}' ({source}) → {path}")
