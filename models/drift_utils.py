"""
Module: drift_utils.py
Purpose: Compute semantic drift between time-separated text corpora.
"""

from api.utils.embeddings import Embedder
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DriftDetector:
    def __init__(self, threshold: float = 0.25):
        self.embedder = Embedder()
        self.threshold = threshold

    def compute_drift(self, old_texts: list[str], new_texts: list[str]) -> dict:
        """Return drift score and status comparing two text sets."""
        if not old_texts or not new_texts:
            logger.warning("Empty text lists received for drift computation.")
            return {"drift_score": 0.0, "drift_detected": False}

        old_emb = self.embedder.encode_texts(old_texts)
        new_emb = self.embedder.encode_texts(new_texts)

        sim = float(np.mean(cosine_similarity(old_emb, new_emb)))
        drift_score = 1 - sim
        drift_detected = drift_score > self.threshold

        result = {
            "drift_score": round(drift_score, 4),
            "drift_detected": drift_detected
        }
        logger.info(f"Drift result: {result}")
        return result
