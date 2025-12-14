
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
    """
    Find sentences containing specific keywords.
    Returns a dict { keyword: [snippet1, snippet2] }
    """
    snippets = {k: [] for k in keywords}
    
    # Pre-compile regex for keywords for faster search
    # (Using simple split for now, robust enough for prototype)
    
    for text in texts:
        # Stop if we found enough for all keywords (optimization)
        if all(len(snippets[k]) >= max_snippets for k in keywords):
            break
            
        sentences = re.split(r'[.!?]+', text)
        
        for sent in sentences:
            sent = sent.strip()
            if not sent: continue
            
            sent_lower = " " + sent.lower() + " "
            
            for k in keywords:
                if len(snippets[k]) >= max_snippets:
                    continue
                
                # Check for word boundary roughly
                if f" {k} " in sent_lower:
                    snippets[k].append(sent)

    return snippets

@router.get("/drift_details")
def get_drift_details(
    topic: str = Query(..., description="Topic name"),
    old_date: str = Query(..., description="Old date YYYY-MM-DD"),
    new_date: str = Query(..., description="New date YYYY-MM-DD")
):
    """
    Analyze word usage changes between two dates for a topic.
    Returns distinct context snippets for the top changing words.
    """
    logger.info(f"Analyzing drift details for {topic}: {old_date} -> {new_date}")
    
    texts_old = load_texts(topic, old_date)
    texts_new = load_texts(topic, new_date)
    
    if not texts_old and not texts_new:
        return {"word_context": [], "warning": "No text data found for these dates."}

    rising, falling = get_top_diff_words(texts_old, texts_new)
    
    # Select top 3 rising and top 3 falling
    top_rising = rising[:3]
    top_falling = falling[:3]
    
    # We want to see:
    # 1. Rising words: usage in NEW vs usage in OLD (if any)
    # 2. Falling words: usage in OLD vs usage in NEW (if any)
    
    target_words = []
    
    # Adding rising words
    for item in top_rising:
        target_words.append({"word": item['word'], "type": "rising", "score": item['score']})
        
    # Adding falling words
    for item in top_falling:
        target_words.append({"word": item['word'], "type": "falling", "score": item['score']})
        
    unique_keywords = list(set([t['word'] for t in target_words]))
    
    # Find snippets in BOTH datasets for comparison
    snippets_old = find_snippets(texts_old, unique_keywords, max_snippets=2)
    snippets_new = find_snippets(texts_new, unique_keywords, max_snippets=2)
    
    word_context = []
    
    for item in target_words:
        w = item['word']
        word_context.append({
            "word": w,
            "type": item['type'],
            "score": item['score'],
            "context_old": snippets_old.get(w, []),
            "context_new": snippets_new.get(w, [])
        })

    return {
        "topic": topic,
        "period": f"{old_date} -> {new_date}",
        "word_context": word_context
    }
