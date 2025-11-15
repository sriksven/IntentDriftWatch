"""
Module: full_pipeline.py
Purpose: Run the complete IntentDriftWatch workflow end-to-end with MLflow tracking.
Author: Krishna
"""

import os
import sys
import time
import json
import datetime as dt
import logging
from glob import glob
import mlflow

# =========================================
# LOGGING SETUP: portable cross-platform
# =========================================

# Repo root dynamically (works on macOS, Linux, GitHub Actions)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logs stored inside repo under monitoring/logs/
LOG_DIR = os.path.join(ROOT_DIR, "monitoring", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(
    LOG_DIR,
    f"pipeline_{dt.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging initialized. Saving to: {log_file}")

# =========================================
# MODULE IMPORTS
# =========================================
from data_pipeline.data_collectors.reddit_scraper import fetch_reddit_posts
from data_pipeline.data_collectors.wiki_scraper import fetch_wiki_page
from data_pipeline.data_collectors.rss_scraper import fetch_rss_articles
from data_pipeline.combine_sources import combine_topic_data
from data_pipeline.clean_combined_data import clean_combined_topic
from data_pipeline.generate_embeddings import generate_embeddings_for_topic
from analytics.semantic_drift import run_semantic_drift

# Try to import concept drift (module may vary by install)
try:
    from analytics.concept_drift_xgb import run_concept_drift
except ImportError:
    try:
        from models.concept_drift_xgb import run_concept_drift
    except ImportError:
        logger.warning("concept_drift_xgb module not found")
        run_concept_drift = None

from data_pipeline.utils.log_data_collection import log_collection_event


# =========================================
# CONFIG
# =========================================
TOPICS = [
    "Artificial Intelligence", "Climate Change", "Space Exploration",
    "Cryptocurrency", "Electric Vehicles", "Elections"
]


# =========================================
# MAIN PIPELINE FUNCTION
# =========================================
def run_full_pipeline():
    logger.info("Starting IntentDriftWatch full pipeline...")

    # -----------------------------
    # MLflow setup
    # -----------------------------
    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("IntentDriftWatch_Experiments")

    run_name = f"Run_{dt.datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}"
    with mlflow.start_run(run_name=run_name):
        mlflow.log_param("run_date", str(dt.datetime.utcnow()))
        mlflow.log_param("tracked_topics", TOPICS)

        # -----------------------------
        # PHASE 1: DATA COLLECTION
        # -----------------------------
        logger.info("Phase 1: Collecting data from Reddit, Wikipedia, and RSS")

        for topic in TOPICS:
            try:
                fetch_reddit_posts(topic, limit=100)
                fetch_wiki_page(topic)
                fetch_rss_articles(topic)
                log_collection_event(topic, "data_collection", "success")
                time.sleep(5)
            except Exception as e:
                log_collection_event(topic, "data_collection", f"failed: {e}")
                logger.error(f"Failed to collect data for {topic}: {e}")

        # -----------------------------
        # PHASE 2: DATA PREPARATION
        # -----------------------------
        logger.info("Phase 2: Combining and cleaning data")

        for topic in TOPICS:
            try:
                combine_topic_data(topic)
                clean_combined_topic(topic)
            except Exception as e:
                logger.error(f"Failed during processing for {topic}: {e}")

        # -----------------------------
        # PHASE 3: EMBEDDING GENERATION
        # -----------------------------
        logger.info("Phase 3: Generating embeddings")

        for topic in TOPICS:
            try:
                generate_embeddings_for_topic(topic)
            except Exception as e:
                logger.error(f"Embedding failed for {topic}: {e}")

        # -----------------------------
        # PHASE 4: SEMANTIC DRIFT
        # -----------------------------
        logger.info("Phase 4: Detecting semantic drift")
        try:
            run_semantic_drift("data_pipeline/data/processed/embeddings")
        except Exception as e:
            logger.error(f"Semantic drift computation failed: {e}")

        # Log semantic drift metrics
        semantic_reports = glob("drift_reports/semantic/*.json")
        for rpt in semantic_reports:
            try:
                with open(rpt) as f:
                    data = json.load(f)
                topic_key = data["topic"].replace(" ", "_")
                mlflow.log_metric(f"{topic_key}_cosine_drift", data["cosine_drift"])
                mlflow.log_metric(f"{topic_key}_jsd_drift", data["jsd_drift"])
                mlflow.log_metric(f"{topic_key}_drift_score", data["drift_score"])
            except Exception as e:
                logger.warning(f"Could not log semantic drift metric from {rpt}: {e}")

        if os.path.exists("drift_reports/semantic"):
            mlflow.log_artifacts("drift_reports/semantic", artifact_path="semantic_reports")

        # -----------------------------
        # PHASE 5: CONCEPT DRIFT
        # -----------------------------
        logger.info("Phase 5: Detecting concept drift")

        if run_concept_drift is not None:
            try:
                run_concept_drift("data_pipeline/data/processed/embeddings")
            except Exception as e:
                logger.error(f"Concept drift computation failed: {e}")

            concept_reports = glob("drift_reports/concept/*.json")
            for rpt in concept_reports:
                try:
                    with open(rpt) as f:
                        data = json.load(f)
                    topic_key = data["topic"].replace(" ", "_")
                    mlflow.log_metric(f"{topic_key}_train_acc", data["train_acc"])
                    mlflow.log_metric(f"{topic_key}_test_acc", data["test_acc"])
                    mlflow.log_metric(f"{topic_key}_accuracy_drop", data["accuracy_drop"])
                    mlflow.log_metric(f"{topic_key}_test_f1", data["test_f1"])
                except Exception as e:
                    logger.warning(f"Could not log concept drift metric from {rpt}: {e}")

            if os.path.exists("drift_reports/concept"):
                mlflow.log_artifacts("drift_reports/concept", artifact_path="concept_reports")
        else:
            logger.warning("Concept drift module not available, skipping Phase 5")

        # -----------------------------
        # Visual Drift Reports
        # -----------------------------
        if os.path.exists("drift_reports/visual"):
            mlflow.log_artifacts("drift_reports/visual", artifact_path="visual_reports")
            logger.info("Visual drift reports logged to MLflow")

        # -----------------------------
        # END OF RUN
        # -----------------------------
        logger.info("Pipeline complete! All phases executed successfully.")
        mlflow.end_run()


# =========================================
# ENTRY POINT
# =========================================
if __name__ == "__main__":
    run_full_pipeline()
