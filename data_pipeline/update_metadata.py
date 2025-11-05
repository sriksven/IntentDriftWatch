"""
Update metadata logs after each data fetch.
"""
import json, os, datetime as dt, logging
from data_pipeline.utils.io_utils import ensure_dir, save_json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_metadata(topic: str, source: str, record_path: str):
    """Append record to metadata JSON."""
    meta_path = "data/metadata/data_collection_log.json"
    ensure_dir("data/metadata")
    record = {
        "topic": topic,
        "source": source,
        "file": record_path,
        "timestamp": str(dt.datetime.utcnow())
    }
    if os.path.exists(meta_path):
        with open(meta_path, "r+") as f:
            data = json.load(f)
            data.append(record)
            f.seek(0)
            json.dump(data, f, indent=2)
    else:
        save_json([record], meta_path)
    logger.info(f"Metadata updated for {topic} ({source})")
