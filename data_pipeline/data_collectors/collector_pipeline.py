"""
Module: collector_pipeline.py
Purpose: Unified entry point to collect data from all sources
(Reddit, Wikipedia, Twitter, RSS) for multiple topics.
"""

import logging
import time
from data_pipeline.data_collectors.reddit_scraper import fetch_reddit_posts
from data_pipeline.data_collectors.wiki_scraper import fetch_wiki_page
from data_pipeline.data_collectors.twitter_scraper import fetch_twitter_posts
from data_pipeline.data_collectors.rss_scraper import fetch_rss_articles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your topics here (or later load dynamically from metadata)
TOPICS = [
    "Artificial Intelligence",
    "Climate Change",
    "Space Exploration",
    "Cryptocurrency",
    "Electric Vehicles",
    "Elections"
]

def run_collector_pipeline(topics=TOPICS, sleep_gap=10):
    """
    Run all available data collectors (Reddit, Wiki, X, RSS)
    for each topic sequentially.
    """
    for topic in topics:
        logger.info(f"\n🚀 Starting data collection for: {topic}\n")

        # Reddit
        try:
            fetch_reddit_posts(topic, limit=100)
        except Exception as e:
            logger.error(f"❌ Reddit collection failed for {topic}: {e}")

        # Wikipedia
        try:
            fetch_wiki_page(topic)
        except Exception as e:
            logger.error(f"❌ Wikipedia collection failed for {topic}: {e}")

        # Twitter (X)
        # try:
            # fetch_twitter_posts(topic, limit=50)
            # logger.info("⏳ Waiting before next API call to avoid rate limit...")
            # time.sleep(sleep_gap)
        # except Exception as e:
            # logger.error(f"Twitter collection failed for {topic}: {e}")

        # RSS
        try:
            fetch_rss_articles(topic, limit=30)
        except Exception as e:
            logger.error(f"RSS collection failed for {topic}: {e}")

        logger.info(f"✅ Completed data collection for topic: {topic}\n")
        time.sleep(5)  # small gap between topics


if __name__ == "__main__":
    run_collector_pipeline()
