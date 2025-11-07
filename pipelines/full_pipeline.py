"""
Module: full_pipeline.py
Purpose: Run the complete IntentDriftWatch workflow end-to-end.
Author: Sriks
"""

import os
import time
import logging

# ---- Import your project modules ----
from data_pipeline.data_collectors.reddit_scraper import fetch_reddit_posts
from data_pipeline.data_collectors.wiki_scraper import fetch_wiki_page
from data_pipeline.data_collectors.rss_scraper import fetch_rss_articles
from data_pipeline.combine_sources import combine_topic_data
from data_pipeline.clean_combined_data import clean_combined_topic
from data_pipeline.generate_embeddings import generate_embeddings_for_topic
from analytics.drift_utils import compute_drift
from data_pipeline.utils.log_data_collection import log_collection_event

# ---- Logging setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# ---- Topics to track ----
TOPICS = [
    "Artificial Intelligence", "Climate Change", "Space Exploration",
    "Cryptocurrency", "Electric Vehicles", "Elections"
]


def run_full_pipeline():
    logger.info("🚀 Starting IntentDriftWatch full pipeline...")

    # PHASE 1: DATA COLLECTION
    logger.info("📥 Phase 1: Collecting data from Reddit, Wikipedia, and RSS")

    for topic in TOPICS:
        try:
            fetch_reddit_posts(topic, limit=100)
            fetch_wiki_page(topic)
            fetch_rss_articles(topic)
            log_collection_event(topic, "data_collection", "success")
            time.sleep(5)
        except Exception as e:
            log_collection_event(topic, "data_collection", f"failed: {e}")
            logger.error(f"❌ Failed to collect data for {topic}: {e}")

    # PHASE 2: DATA PREPARATION
    logger.info("🧹 Phase 2: Combining and cleaning data")

    for topic in TOPICS:
        try:
            combine_topic_data(topic)
            clean_combined_topic(topic)
        except Exception as e:
            logger.error(f"❌ Failed during processing for {topic}: {e}")

    # PHASE 3: EMBEDDING GENERATION
    logger.info("🧠 Phase 3: Generating embeddings")

    for topic in TOPICS:
        try:
            generate_embeddings_for_topic(topic)
        except Exception as e:
            logger.error(f"❌ Embedding failed for {topic}: {e}")

    # PHASE 4: DRIFT DETECTION
    logger.info("📈 Phase 4: Computing semantic drift")

    for topic in TOPICS:
        try:
            # Assuming you compare last two snapshots automatically
            emb_dir = "data_pipeline/data/processed/embeddings"
            all_embeds = sorted(
                [f for f in os.listdir(emb_dir) if topic.replace(' ', '_') in f and f.endswith('.npy')]
            )

            if len(all_embeds) >= 2:
                old_path = os.path.join(emb_dir, all_embeds[-2])
                new_path = os.path.join(emb_dir, all_embeds[-1])
                compute_drift(topic, old_path, new_path)
            else:
                logger.warning(f"Not enough snapshots for drift detection: {topic}")
        except Exception as e:
            logger.error(f"❌ Drift computation failed for {topic}: {e}")

    logger.info("✅ Pipeline complete! All phases executed successfully.")


if __name__ == "__main__":
    run_full_pipeline()
