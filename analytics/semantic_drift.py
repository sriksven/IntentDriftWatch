"""
Module: semantic_drift.py
Purpose: Detect semantic drift automatically across all available embedding snapshots.
"""

import os
import numpy as np
import datetime as dt
import logging
from scipy.spatial.distance import cosine
from scipy.stats import entropy
from data_pipeline.utils.io_utils import ensure_dir, save_json
from analytics.evidently_reports import generate_semantic_drift_report
from analytics.plotly_reports import generate_semantic_drift_report, generate_concept_drift_report

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
def compute_semantic_drift(topic: str, old_path: str, new_path: str, old_date: str, new_date: str):
    """Compute semantic drift metrics between two embedding snapshots."""
    old_emb = np.load(old_path)
    new_emb = np.load(new_path)

    # Ensure both have same length
    n = min(len(old_emb), len(new_emb))
    if n == 0:
        logger.warning(f"No overlapping samples to compare for topic: {topic}")
        return None

    old_emb, new_emb = old_emb[:n], new_emb[:n]

    old_mean = np.mean(old_emb, axis=0)
    new_mean = np.mean(new_emb, axis=0)

    cosine_drift = cosine(old_mean, new_mean)
    jsd = jensen_shannon_divergence(np.abs(old_emb.flatten()), np.abs(new_emb.flatten()))
    drift_score = round((cosine_drift + jsd) / 2, 4)

    # Generate Evidently semantic drift report
    try:
        html_path = generate_semantic_drift_report(
            topic=topic,
            old_emb_path=old_path,
            new_emb_path=new_path,
            old_date=old_date,
            new_date=new_date
        )
        if html_path:
            logger.info(f"📊 Evidently report: {html_path}")
    except Exception as e:
        logger.warning(f"⚠️ Could not generate Evidently semantic drift report for {topic}: {e}")

    result = {
        "topic": topic,
        "timestamp": str(dt.datetime.utcnow()),
        "old_date": old_date,
        "new_date": new_date,
        "old_samples": int(len(old_emb)),
        "new_samples": int(len(new_emb)),
        "cosine_drift": float(cosine_drift),
        "jsd_drift": float(jsd),
        "drift_score": float(drift_score),
        "old_snapshot": old_path,
        "new_snapshot": new_path,
        "status": "Significant Drift" if drift_score > 0.25 else "Minor Drift" if drift_score > 0.15 else "Stable"
    }

    ensure_dir("drift_reports/semantic")
    report_path = os.path.join(
        "drift_reports/semantic",
        f"{topic.replace(' ', '_')}_semantic_drift_{new_date}.json"
    )
    save_json(result, report_path)

    logger.info(f"✅ Semantic drift for '{topic}' saved → {report_path}")
    logger.info(f"   Drift Score: {drift_score:.4f} | Status: {result['status']}")
    return result


# ---------- Automatic Runner ----------
def run_semantic_drift(base_emb_dir="data_pipeline/data/processed/embeddings"):
    """
    Detect semantic drift for all topics across all consecutive embedding snapshots.
    Example:
        2025-11-05 → 2025-11-06
        2025-11-06 → 2025-11-07
        etc.
    """
    logger.info("📈 Running semantic drift detection...")

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
            try:
                compute_semantic_drift(
                    topic=topic_name,
                    old_path=old_files[topic_file],
                    new_path=new_files[topic_file],
                    old_date=old_date,
                    new_date=new_date
                )
            except Exception as e:
                logger.error(f"❌ Failed to compute semantic drift for {topic_name}: {e}")

    logger.info("✅ Semantic drift detection completed successfully.")


if __name__ == "__main__":
    run_semantic_drift()