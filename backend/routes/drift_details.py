
import os
import json
import logging
import re
from collections import Counter
from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any

from sklearn.feature_extraction.text import CountVectorizer

router = APIRouter()
logger = logging.getLogger(__name__)

DATA_DIR = "data_pipeline/data/processed/cleaned"

def load_texts(topic: str, date: str) -> List[str]:
    """Load cleaned texts for a specific topic and date."""
    safe_topic = topic.replace(" ", "_")
    filename = f"{safe_topic}_cleaned_{date}.json"
    path = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(path):
        logger.warning(f"File not found: {path}")
        return []
        
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("texts", [])
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return []

def get_top_diff_words(texts_old: List[str], texts_new: List[str], top_n=10):
    """
    Compare two text lists and return words that increased or decreased in frequency.
    """
    if not texts_old and not texts_new:
        return [], []

    # Use CountVectorizer to handle tokenization and stop words
    vec = CountVectorizer(stop_words='english', max_features=1000)
    
    # Fit on all data to get vocabulary
    all_texts = texts_old + texts_new
    if not all_texts:
        return [], []
        
    try:
        vec.fit(all_texts)
        feature_names = vec.get_feature_names_out()
        
        # Transform separately
        if texts_old:
            X_old = vec.transform(texts_old)
            # Average freq per document to normalize for widespread usage? 
            # Or just raw counts normalized by total word count?
            # Let's simple: sum counts / total words in corpus
            counts_old = X_old.sum(axis=0).A1
            total_old = counts_old.sum() if counts_old.sum() > 0 else 1
            freq_old = counts_old / total_old
        else:
            freq_old = [0] * len(feature_names)

        if texts_new:
            X_new = vec.transform(texts_new)
            counts_new = X_new.sum(axis=0).A1
            total_new = counts_new.sum() if counts_new.sum() > 0 else 1
            freq_new = counts_new / total_new
        else:
            freq_new = [0] * len(feature_names)

        # Calculate difference
        diffs = []
        for i, word in enumerate(feature_names):
            diff = freq_new[i] - freq_old[i]
            diffs.append((word, diff, freq_new[i], freq_old[i]))
            
        # Sort by diff
        # Rising: highest positive diff
        rising = sorted([d for d in diffs if d[1] > 0], key=lambda x: x[1], reverse=True)[:top_n]
        
        # Falling: lowest negative diff (highest absolute value)
        falling = sorted([d for d in diffs if d[1] < 0], key=lambda x: x[1])[:top_n]
        
        # Format for output
        rising_out = [{"word": w, "score": float(d), "new_freq": float(nf), "old_freq": float(of)} for w, d, nf, of in rising]
        falling_out = [{"word": w, "score": float(d), "new_freq": float(nf), "old_freq": float(of)} for w, d, nf, of in falling]
        
        return rising_out, falling_out
        
    except ValueError:
        # E.g. empty vocabulary
        return [], []

def find_snippets(texts: List[str], keywords: List[str], max_snippets=2):
    """Find sentences containing keywords."""
    snippets = []
    
    for text in texts:
        if len(snippets) >= max_snippets:
            break
            
        # Simple sentence split (can be improved)
        sentences = re.split(r'[.!?]+', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: 
                continue
                
            # Check if any keyword is in this sentence
            # Naive check: word in sentence string
            for kw in keywords:
                # Add word boundary check regex would be better but keeping simple for now
                if f" {kw} " in f" {sent.lower()} ":
                    snippets.append({"text": sent, "keyword": kw})
                    break
            
            if len(snippets) >= max_snippets:
                break
                
    return snippets

@router.get("/drift_details")
def get_drift_details(
    topic: str = Query(..., description="Topic name"),
    old_date: str = Query(..., description="Old date YYYY-MM-DD"),
    new_date: str = Query(..., description="New date YYYY-MM-DD")
):
    """
    Analyze word usage changes between two dates for a topic.
    """
    logger.info(f"Analyzing drift details for {topic}: {old_date} -> {new_date}")
    
    texts_old = load_texts(topic, old_date)
    texts_new = load_texts(topic, new_date)
    
    if not texts_old and not texts_new:
        return {"rising": [], "falling": [], "snippets": [], "warning": "No text data found for these dates."}

    rising, falling = get_top_diff_words(texts_old, texts_new)
    
    # Get snippets for top 3 rising words
    top_rising_keywords = [item['word'] for item in rising[:3]]
    snippets = find_snippets(texts_new, top_rising_keywords)
    
    return {
        "topic": topic,
        "period": f"{old_date} -> {new_date}",
        "rising": rising,
        "falling": falling,
        "snippets": snippets
    }
