"""
Module: reddit_scraper.py
Purpose: Fetch Reddit posts using the official Reddit API (PRAW) — no Pushshift dependency.
"""

import praw
import datetime as dt
import logging
import os
from dotenv import load_dotenv
from data_pipeline.utils.io_utils import save_json, ensure_dir
from data_pipeline.utils.text_cleaning import clean_texts
from data_pipeline.utils.log_data_collection import log_collection_event

# ---------------- Logging ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Load environment variables ----------------
load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


# ---------------- Main Function ----------------
def fetch_reddit_posts(topic: str, subreddit: str = "all", limit: int = 200):
    """Fetch recent Reddit submissions containing the topic."""
    raw_dir = "data_pipeline/data/raw/reddit"
    ensure_dir(raw_dir)

    posts = []
    try:
        for submission in reddit.subreddit(subreddit).search(topic, limit=limit, sort="new"):
            text = f"{submission.title} {submission.selftext}"
            if text.strip():
                posts.append(text.strip())

        if not posts:
            logger.warning(f"No Reddit posts found for topic '{topic}'.")
            return None

        cleaned = clean_texts(posts)

        data = {
            "topic": topic,
            "source": "reddit",
            "collected_at": str(dt.datetime.utcnow()),
            "texts": cleaned
        }

        filename = f"{topic.replace(' ', '_')}_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
        path = os.path.join(raw_dir, filename)
        save_json(data, path)
        log_collection_event(topic, "reddit", path)

        logger.info(f"✅ Collected {len(cleaned)} Reddit posts for '{topic}' → {path}")
        return path

    except Exception as e:
        logger.error(f"❌ Error fetching Reddit posts for '{topic}': {e}")
        log_collection_event(topic, "reddit", f"failed: {e}")
        return None


# ---------------- CLI Runner ----------------
if __name__ == "__main__":
    topics = [
        "Artificial Intelligence", "Climate Change", "Space Exploration",
        "Cryptocurrency", "Electric Vehicles", "Elections"
    ]

    for t in topics:
        fetch_reddit_posts(t, limit=100)
