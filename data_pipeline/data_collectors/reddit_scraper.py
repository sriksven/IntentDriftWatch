"""
Fetch Reddit posts using official Reddit API (PRAW) — works without Pushshift.
"""

import praw
import datetime as dt
import logging, os
from data_pipeline.utils.io_utils import save_json, ensure_dir
from data_pipeline.utils.text_cleaning import clean_texts
from data_pipeline.update_metadata import update_metadata
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


def fetch_reddit_posts(topic: str, subreddit: str = "all", limit: int = 200):
    """Fetch recent Reddit submissions containing the topic."""
    ensure_dir("data/raw/reddit")

    posts = []
    for submission in reddit.subreddit(subreddit).search(topic, limit=limit, sort="new"):
        text = f"{submission.title} {submission.selftext}"
        posts.append(text.strip())

    cleaned = clean_texts(posts)

    data = {
        "topic": topic,
        "source": "reddit",
        "collected_at": str(dt.datetime.utcnow()),
        "texts": cleaned
    }

    filename = f"{topic}_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
    path = os.path.join("data/raw/reddit", filename)
    save_json(data, path)
    update_metadata(topic, "reddit", path)

    logger.info(f"✅ Collected {len(cleaned)} Reddit posts for '{topic}' → {path}")
    return path

if __name__ == "__main__":
    topics = [
    "Artificial Intelligence", "Climate Change", "Space Exploration", "Cryptocurrency",
    "Electric Vehicles", "Elections"
    ]

    for t in topics:
        fetch_reddit_posts(t, limit=100)
