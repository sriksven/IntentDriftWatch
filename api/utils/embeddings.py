"""
Module: embeddings.py
Purpose: Centralized embedding generator for IntentDriftWatch.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Embedder:
    """Wrapper around SentenceTransformer for consistent embedding generation."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def encode_texts(self, texts: list[str]) -> np.ndarray:
        """Convert list of texts into dense vector embeddings."""
        if not texts:
            return np.empty((0, 384))
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            return embeddings
        except Exception as e:
            logger.error(f"Error during embedding: {e}")
            raise
