"""
Module: drift_utils.py
Purpose: Detect semantic drift automatically across all available embedding snapshots.
"""

import os
import numpy as np
import datetime as dt
import logging
from scipy.spatial.distance import cosine
from scipy.stats import entropy
from data_pipeline.utils.io_utils import ensure_dir, save_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Metrics ----------
def jensen_shannon_divergence(p, q):
    """Compute Jensen–Shannon Divergence between two probability distributions."""
    p, q = np.asarray(p), np.asarray(q)
    p = p / (p.sum() + 1e-12)
    q = q / (q.sum() + 1e-12)
    m = 0.5 * (p + q)
    return 0.5 * (entropy(p, m) + entropy(q, m))


# ---------- Core Drift ----------
def compute_drift(topic: str, old_path: str, new_path: str, old_date: str, new_date: str):
    """Compute semantic drift metrics between two embedding snapshots."""
    old_emb = np.load(old_path)
    new_emb = np.load(new_path)

    old_mean = np.mean(old_emb, axis=0)
    new_mean = np.mean(new_emb, axis=0)

    cosine_drift = cosine(old_mean, new_mean)
    jsd = jensen_shannon_divergence(np.abs(old_emb.flatten()), np.abs(new_emb.flatten()))
    drift_score = round((cosine_drift + jsd) / 2, 4)

    result = {
        "topic": topic,
        "timestamp": str(dt.datetime.utcnow()),
        "old_date": old_date,
        "new_date": new_date,
        "cosine_drift": float(cosine_drift),
        "jsd_drift": float(jsd),
        "drift_score": float(drift_score),
        "old_snapshot": old_path,
        "new_snapshot": new_path,
        "status": "Drift Detected" if drift_score > 0.25 else "Stable"
    }

    ensure_dir("drift_reports")
    report_path = os.path.join(
        "drift_reports",
        f"{topic.replace(' ', '_')}_drift_{new_date}.json"
    )
    save_json(result, report_path)

    logger.info(f"✅ Drift report for '{topic}' saved → {report_path}")
    logger.info(f"   Drift Score: {drift_score:.4f} | Status: {result['status']}")
    return result


# ---------- Automatic Runner ----------
def run_all_drifts(base_emb_dir="data_pipeline/data/processed/embeddings"):
    """
    Detect drift for all topics across all consecutive embedding snapshots.
    Example:
        2025-11-05 → 2025-11-06
        2025-11-06 → 2025-11-07
        etc.
    """
    logger.info("📈 Running full multi-date drift detection...")

    if not os.path.exists(base_emb_dir):
        logger.error(f"Embedding directory not found: {base_emb_dir}")
        return

    # Get all date folders
    date_dirs = sorted(
        [d for d in os.listdir(base_emb_dir) if os.path.isdir(os.path.join(base_emb_dir, d))]
    )
    if len(date_dirs) < 2:
        logger.warning("Not enough embedding snapshots to compute drift (need at least 2 dates).")
        return

    # Iterate through all consecutive pairs
    for i in range(1, len(date_dirs)):
        old_date, new_date = date_dirs[i - 1], date_dirs[i]
        old_dir = os.path.join(base_emb_dir, old_date)
        new_dir = os.path.join(base_emb_dir, new_date)

        logger.info(f"🔹 Comparing embeddings: {old_date} → {new_date}")

        old_files = {
            os.path.splitext(f)[0]: os.path.join(old_dir, f)
            for f in os.listdir(old_dir)
            if f.endswith(".npy")
        }
        new_files = {
            os.path.splitext(f)[0]: os.path.join(new_dir, f)
            for f in os.listdir(new_dir)
            if f.endswith(".npy")
        }

        common_topics = set(old_files.keys()) & set(new_files.keys())
        if not common_topics:
            logger.warning(f"No common topics found between {old_date} and {new_date}.")
            continue

        for topic_file in common_topics:
            topic_name = topic_file.replace("_", " ")
            compute_drift(topic_name, old_files[topic_file], new_files[topic_file], old_date, new_date)

    logger.info("✅ Multi-date drift detection completed successfully.")


if __name__ == "__main__":
    run_all_drifts()
