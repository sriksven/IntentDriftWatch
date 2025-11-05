"""
Module: wiki_scraper.py
Purpose: Fetch Wikipedia article text for a topic and store locally.
"""

import wikipediaapi
import datetime as dt
import logging
import os
from data_pipeline.utils.io_utils import save_json, ensure_dir
from data_pipeline.utils.text_cleaning import clean_text
from data_pipeline.update_metadata import update_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_wiki_page(topic: str):
    """Fetch and store Wikipedia article text for a topic."""
    wiki = wikipediaapi.Wikipedia(
        language='en',
        user_agent='IntentDriftWatch/0.1 (https://github.com/sriksven/IntentDriftWatch)'
    )

    page = wiki.page(topic)

    if not page.exists():
        logger.warning(f"No Wikipedia page found for topic '{topic}'.")
        return None

    text = clean_text(page.text[:20000])  # limit text length to 20k chars
    data = {
        "topic": topic,
        "source": "wikipedia",
        "collected_at": str(dt.datetime.utcnow()),
        "texts": [text]
    }

    ensure_dir("data/raw/wiki")
    filename = f"{topic.replace(' ', '_')}_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
    path = os.path.join("data/raw/wiki", filename)
    save_json(data, path)
    update_metadata(topic, "wikipedia", path)

    logger.info(f"✅ Saved Wikipedia article for '{topic}' → {path}")
    return path


if __name__ == "__main__":
    topics = [
    "Artificial Intelligence", "Climate Change", "Space Exploration", "Cryptocurrency",
    "Electric Vehicles", "Elections"
    ]
    for t in topics:
        try:
            fetch_wiki_page(t)
        except Exception as e:
            logger.error(f"❌ Failed for {t}: {e}")
