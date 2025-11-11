"""
Module: concept_drift_xgb.py
Purpose: Detect concept drift by training XGBoost to distinguish between 
         old and new embeddings. High accuracy = significant distribution shift.
"""

import os
import json
import datetime as dt
import logging
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report
from data_pipeline.utils.io_utils import ensure_dir, save_json
from analytics.evidently_reports import generate_concept_drift_report
from analytics.plotly_reports import generate_semantic_drift_report, generate_concept_drift_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Drift Computation ----------
def compute_concept_drift(topic, old_emb_path, new_emb_path, old_date, new_date):
    """
    Concept drift detection using temporal binary classification.
    
    Approach:
    - Label old embeddings as 0, new embeddings as 1
    - Train classifier to distinguish between them
    - High test accuracy = significant drift (model can easily tell them apart)
    - Low test accuracy (~0.5) = stable (model cannot distinguish, similar distributions)
    """
    old_emb = np.load(old_emb_path)
    new_emb = np.load(new_emb_path)

    if len(old_emb) == 0 or len(new_emb) == 0:
        logger.warning(f"Empty embeddings for topic: {topic}")
        return None

    # Create binary classification dataset: 0 = old period, 1 = new period
    X = np.vstack([old_emb, new_emb])
    y = np.array([0] * len(old_emb) + [1] * len(new_emb))

    # Split into train/test while maintaining class balance
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Train XGBoost classifier
    model = xgb.XGBClassifier(
        max_depth=5,
        n_estimators=100,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42
    )

    model.fit(X_train, y_train)

    # Generate predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    # Calculate metrics
    acc_train = accuracy_score(y_train, y_pred_train)
    acc_test = accuracy_score(y_test, y_pred_test)
    f1_train = f1_score(y_train, y_pred_train, average='weighted')
    f1_test = f1_score(y_test, y_pred_test, average='weighted')
    
    accuracy_drop = round(acc_train - acc_test, 4)

    # Generate Evidently concept drift report
    try:
        html_path = generate_concept_drift_report(
            topic=topic,
            y_train=y_train,
            y_pred_train=y_pred_train,
            y_test=y_test,
            y_pred_test=y_pred_test,
            new_date=new_date
        )
        if html_path:
            logger.info(f"📊 Evidently report: {html_path}")
    except Exception as e:
        logger.warning(f"⚠️ Could not generate Evidently concept drift report for {topic}: {e}")

    # Interpret drift severity
    # High test accuracy = model can easily distinguish old from new = drift detected
    # Accuracy around 0.5 = model cannot distinguish = stable/no drift
    if acc_test >= 0.75:
        status = "Significant Drift"
    elif acc_test >= 0.60:
        status = "Moderate Drift"
    else:
        status = "Stable"

    result = {
        "topic": topic,
        "timestamp": str(dt.datetime.utcnow()),
        "old_date": old_date,
        "new_date": new_date,
        "old_samples": int(len(old_emb)),
        "new_samples": int(len(new_emb)),
        "train_acc": float(acc_train),
        "test_acc": float(acc_test),
        "train_f1": float(f1_train),
        "test_f1": float(f1_test),
        "accuracy_drop": float(accuracy_drop),
        "status": status,
        "interpretation": f"Model can distinguish old/new with {acc_test:.1%} accuracy"
    }

    ensure_dir("drift_reports/concept")
    path = os.path.join(
        "drift_reports/concept",
        f"{topic.replace(' ', '_')}_concept_drift_{new_date}.json"
    )
    save_json(result, path)

    logger.info(f"✅ Concept drift for '{topic}' saved → {path}")
    logger.info(f"   Test Accuracy: {acc_test:.4f} | Test F1: {f1_test:.4f}")
    logger.info(f"   Status: {status}")
    
    return result


# ---------- Runner ----------
def run_concept_drift(base_dir="data_pipeline/data/processed/embeddings"):
    """
    Detect concept drift for all topics across consecutive embedding snapshots.
    """
    logger.info("📊 Running concept drift detection...")

    if not os.path.exists(base_dir):
        logger.error(f"Embedding directory not found: {base_dir}")
        return

    date_dirs = sorted(
        d for d in os.listdir(base_dir) 
        if os.path.isdir(os.path.join(base_dir, d))
    )
    
    if len(date_dirs) < 2:
        logger.warning("Not enough snapshots for concept drift (need at least 2 dates).")
        return

    for i in range(1, len(date_dirs)):
        old_date, new_date = date_dirs[i - 1], date_dirs[i]
        old_dir = os.path.join(base_dir, old_date)
        new_dir = os.path.join(base_dir, new_date)

        logger.info(f"🔹 Evaluating concept drift: {old_date} → {new_date}")

        old_files = {
            os.path.splitext(f)[0]: os.path.join(old_dir, f) 
            for f in os.listdir(old_dir) if f.endswith(".npy")
        }
        new_files = {
            os.path.splitext(f)[0]: os.path.join(new_dir, f) 
            for f in os.listdir(new_dir) if f.endswith(".npy")
        }
        
        common_topics = set(old_files) & set(new_files)
        
        if not common_topics:
            logger.warning(f"No common topics found between {old_date} and {new_date}.")
            continue

        for topic_file in common_topics:
            topic_name = topic_file.replace("_", " ")
            try:
                compute_concept_drift(
                    topic=topic_name,
                    old_emb_path=old_files[topic_file],
                    new_emb_path=new_files[topic_file],
                    old_date=old_date,
                    new_date=new_date
                )
            except Exception as e:
                logger.error(f"❌ Failed to compute concept drift for {topic_name}: {e}")

    logger.info("✅ All concept drift computations completed.")


if __name__ == "__main__":
    run_concept_drift()