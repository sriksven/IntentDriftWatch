"""
Module: drift_utils.py
Purpose: Detect semantic drift automatically across all topics.
"""

import os
import json
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
def compute_drift(topic: str, old_path: str, new_path: str):
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
        "cosine_drift": float(cosine_drift),
        "jsd_drift": float(jsd),
        "drift_score": float(drift_score),
        "old_snapshot": os.path.basename(old_path),
        "new_snapshot": os.path.basename(new_path),
        "status": "Drift Detected" if drift_score > 0.25 else "Stable"
    }

    ensure_dir("drift_reports")
    report_path = os.path.join(
        "drift_reports",
        f"{topic.replace(' ', '_')}_drift_{dt.datetime.utcnow().strftime('%Y-%m-%d')}.json"
    )
    save_json(result, report_path)

    logger.info(f"✅ Drift report for '{topic}' saved → {report_path}")
    logger.info(f"   Drift Score: {drift_score:.4f} | Status: {result['status']}")
    return result


# ---------- Automatic Runner ----------
def run_all_drifts(emb_dir="data_pipeline/data/processed/embeddings"):
    """Detect drift for all topics with at least two embedding snapshots."""
    logger.info("📈 Running automatic drift detection for all topics...")
    if not os.path.exists(emb_dir):
        logger.error(f"Embedding directory not found: {emb_dir}")
        return

    # Map: topic -> list of its embedding files
    topic_files = {}
    for f in os.listdir(emb_dir):
        if f.endswith(".npy"):
            topic = f.split("_embeddings")[0].replace("_", " ")
            topic_files.setdefault(topic, []).append(f)

    # Compute drift for all topics
    for topic, files in topic_files.items():
        files = sorted(files)
        if len(files) < 2:
            logger.warning(f"Skipping '{topic}' (only one embedding snapshot).")
            continue

        old_path = os.path.join(emb_dir, files[-2])
        new_path = os.path.join(emb_dir, files[-1])
        logger.info(f"🔹 Computing drift for {topic} between {files[-2]} → {files[-1]}")
        compute_drift(topic, old_path, new_path)

    logger.info("✅ All drift computations completed.")


if __name__ == "__main__":
    run_all_drifts()
