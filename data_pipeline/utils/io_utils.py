"""
Module: io_utils.py
Purpose: Centralized file I/O utilities for saving and loading JSON data.
"""

import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_dir(path: str):
    """Ensure that a directory exists."""
    os.makedirs(path, exist_ok=True)

def save_json(data: dict, path: str):
    """Save Python dict to JSON file."""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved JSON: {path}")

def load_json(path: str) -> dict:
    """Load JSON data from file."""
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
