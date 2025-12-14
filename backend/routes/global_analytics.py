from fastapi import APIRouter, Query
from pathlib import Path
import json
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any

# Import to reuse context shift logic
# We will call the function directly. Note: It expects arguments, not Request object if called directly.
from .drift_details import get_drift_details
from backend.utils.llm_helper import explain_graph_trend

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SUMMARY_DIR = BASE_DIR / "drift_reports" / "summaries"

def parse_date(d: str):
    return datetime.strptime(d, "%Y-%m-%d")

def get_summaries_in_range(time_range: str):
    """
    Load all drift summaries within the time range.
    range: '7d', '30d', '1y'
    """
    now = datetime.now()
    if time_range == "24h":
        delta = timedelta(days=1)
    elif time_range == "7d":
        delta = timedelta(days=7)
    elif time_range == "30d":
        delta = timedelta(days=30)
    elif time_range == "6m":
        delta = timedelta(days=180)
    elif time_range == "1y":
        delta = timedelta(days=365)
    else:
        delta = timedelta(days=7) # Default

    start_date = now - delta
    
    files = sorted(SUMMARY_DIR.glob("drift_summary_*.json"))
    results = []

    for f in files:
        # Extract date from filename drift_summary_YYYY-MM-DD.json
        try:
            date_str = f.stem.split("drift_summary_")[1]
            f_date = parse_date(date_str)
            if f_date >= start_date:
                with open(f) as data_f:
                    results.append(json.load(data_f))
        except Exception as e:
            logger.error(f"Error parsing summary {f}: {e}")
            continue
            
    return sorted(results, key=lambda x: x['date'])

@router.get("/analytics/global_trend")
def get_global_trend(
    time_range: str = Query("7d", description="Time range (24h, 7d, 30d, 1y)")
):
    """
    Returns aggregated drift metrics over time for the dashboard graph.
    """
    summaries = get_summaries_in_range(time_range)
    
    trend_data = []
    
    for s in summaries:
        date = s.get("date")
        rows = s.get("rows", [])
        
        if not rows:
            continue
            
        # Compute averages
        sem_scores = [r.get("semantic_score") for r in rows if isinstance(r.get("semantic_score"), (int, float))]
        conc_scores = [r.get("test_acc") for r in rows if isinstance(r.get("test_acc"), (int, float))]
        
        avg_sem = sum(sem_scores) / len(sem_scores) if sem_scores else 0
        avg_conc = sum(conc_scores) / len(conc_scores) if conc_scores else 0
        
        trend_data.append({
            "date": date,
            "avg_semantic_drift": round(avg_sem, 4),
            "avg_concept_accuracy": round(avg_conc, 4)
        })
    
    explanation = None
    if trend_data:
        try:
             explanation = explain_graph_trend(trend_data)
        except Exception as e:
             logger.error(f"Failed to explain trend: {e}")
             
    return {"trend": trend_data, "explanation": explanation}

@router.get("/analytics/top_shift")
def get_top_shift(
    time_range: str = Query("7d", description="Time range (24h, 7d, 30d, 1y)")
):
    """
    Identifies the topic with the most significant drift in the period 
    and returns its 'Context Shift' explanation.
    """
    summaries = get_summaries_in_range(time_range)
    if not summaries:
        return {"detail": "No data in range"}
        
    # We need start and end snapshots
    if len(summaries) < 2:
        # Fallback to just the latest snapshot comparison if only 1 exists
        # But we really need 2 to show a trend. If 1, we can't show meaningful shift over period.
        # Let's try to get the very last summary and compare with the one before it, even if outside range?
        # Or just return empty.
        latest = summaries[-1]
        # Just return the top drifter from the latest snapshot vs its previous day (handled by drift_details default logic usually?)
        # But drift_details takes explicit old_date and new_date.
        return {"detail": "Insufficient history for range"}

    start_summary = summaries[0]
    end_summary = summaries[-1]
    
    old_date = start_summary['date']
    new_date = end_summary['date']
    
    # Find topic with max semantic drift in the END summary (snapshot drift)
    # OR change in drift? Usually we want "which topic drifted the most recently" or "cumulatively"?
    # Let's take the topic with the highest 'semantic_score' in the latest snapshot.
    
    rows = end_summary.get("rows", [])
    if not rows:
         return {"detail": "No topics found"}
         
    # Sort by semantic score descending
    sorted_rows = sorted(rows, key=lambda x: x.get("semantic_score", 0), reverse=True)
    top_drifter = sorted_rows[0]
    topic_name = top_drifter['topic']
    
    # Now fetch detailed context shift for this topic between old_date and new_date
    # We call the imported function directly
    try:
        drift_explanation = get_drift_details(
            topic=topic_name,
            old_date=old_date,
            new_date=new_date
        )
        return drift_explanation
    except Exception as e:
        logger.error(f"Failed to generate explanation: {e}")
        return {"detail": str(e)}
