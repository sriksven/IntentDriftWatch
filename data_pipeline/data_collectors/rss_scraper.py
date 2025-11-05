import feedparser
import datetime as dt
import logging
import os
from urllib.parse import quote_plus
from data_pipeline.utils.io_utils import save_json, ensure_dir
from data_pipeline.utils.text_cleaning import clean_texts
from data_pipeline.update_metadata import update_metadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_rss_articles(topic: str, limit: int = 30):
    """Fetch latest Google News RSS articles for a given topic."""
    ensure_dir("data/raw/news")

    encoded_topic = quote_plus(topic)
    url = f"https://news.google.com/rss/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            logger.warning(f"No RSS entries found for {topic}.")
            return None

        articles = [entry.title + " " + entry.description for entry in feed.entries[:limit]]
        cleaned = clean_texts(articles)

        data = {
            "topic": topic,
            "source": "rss",
            "collected_at": str(dt.datetime.utcnow()),
            "texts": cleaned
        }

        filename = f"{topic.replace(' ', '_')}_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
        path = os.path.join("data/raw/news", filename)
        save_json(data, path)
        update_metadata(topic, "rss", path)

        logger.info(f"✅ Collected {len(cleaned)} RSS articles for '{topic}' → {path}")
        return path
    except Exception as e:
        logger.error(f"❌ Failed to fetch RSS for {topic}: {e}")
        return None


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
        try:
            fetch_rss_articles(t, limit=30)
        except Exception as e:
            logger.error(f"❌ Failed for {t}: {e}")
