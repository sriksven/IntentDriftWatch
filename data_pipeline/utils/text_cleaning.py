"""
Module: text_cleaning.py
Purpose: Text normalization utilities shared across data pipeline scripts.
"""

import re

def clean_text(text: str) -> str:
    """Remove URLs, punctuation, and excessive spaces."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def clean_texts(texts: list[str]) -> list[str]:
    """Apply clean_text to a list of strings."""
    return [clean_text(t) for t in texts if t and isinstance(t, str)]
