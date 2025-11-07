"""
Module: twitter_scraper.py
Purpose: Fetch recent tweets for given topics using Twitter v2 API via Tweepy.
"""

import tweepy
import datetime as dt
import logging
import os
from data_pipeline.utils.io_utils import save_json, ensure_dir
from data_pipeline.utils.text_cleaning import clean_texts
from data_pipeline.utils.log_data_collection import log_collection_event
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Twitter API
load_dotenv()
BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
client = tweepy.Client(bearer_token=os.getenv("X_BEARER_TOKEN"))

    
def fetch_twitter_posts(topic: str, limit: int = 100):
    """Fetch up to `limit` recent tweets for a topic."""
    ensure_dir("data_pipeline/data/raw/x")

    tweets = []
    try:
        query = f"{topic} lang:en -is:retweet"
        response = client.search_recent_tweets(
            query=query,
            max_results=min(limit, 100),
            tweet_fields=["created_at", "lang", "text"]
        )

        if response.data:
            tweets = [tweet.text for tweet in response.data]
    except Exception as e:
        logger.error(f"❌ Error fetching tweets for {topic}: {e}")
        return None

    cleaned = clean_texts(tweets)
    data = {
        "topic": topic,
        "source": "x",
        "collected_at": str(dt.datetime.utcnow()),
        "texts": cleaned
    }

    filename = f"{topic.replace(' ', '_')}_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
    path = os.path.join("data_pipeline/data/raw/x", filename)
    save_json(data, path)
    log_collection_event(topic, "x", path)

    logger.info(f"✅ Collected {len(cleaned)} tweets for '{topic}' → {path}")
    return path


if __name__ == "__main__":
    import time

    topics = [
    "Artificial Intelligence", "Climate Change", "Space Exploration", "Cryptocurrency",
    "Electric Vehicles", "Elections"
    ]   

    for t in topics:
        try:
            fetch_twitter_posts(t, limit=100)
            logger.info(f"⏳ Waiting 10 seconds before next topic...")
            time.sleep(10)  # wait to stay below rate limit
        except Exception as e:
            logger.error(f"❌ Failed for {t}: {e}")

