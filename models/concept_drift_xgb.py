"""
Module: concept_drift_xgb.py
Purpose: Detect concept drift (supervised model degradation)
         using XGBoost trained on old embeddings and tested on new ones.
"""

import os, json, datetime as dt, logging
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, f1_score
from data_pipeline.utils.io_utils import ensure_dir, save_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- Helpers ----------
def load_embeddings(path):
    """Load embeddings and assign placeholder labels for now."""
    X = np.load(path)
    y = np.random.randint(0, 2, size=X.shape[0])  # synthetic labels
    return X, y


# ---------- Drift Computation ----------
def compute_concept_drift(topic, old_emb_path, new_emb_path, old_date, new_date):
    X_train, y_train = load_embeddings(old_emb_path)
    X_test, y_test = load_embeddings(new_emb_path)

    # Align sample sizes between snapshots (safety fix)
    n = min(len(X_train), len(X_test))
    if n == 0:
        logger.warning(f"No overlapping samples to compare for topic: {topic}")
        return None

    X_train, y_train = X_train[:n], y_train[:n]
    X_test, y_test = X_test[:n], y_test[:n]

    # XGBoost setup (new API — eval_metric inside constructor)
    model = xgb.XGBClassifier(
        max_depth=3,
        n_estimators=50,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric="logloss"  # ✅ moved here
    )

    model.fit(X_train, y_train)

    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)

    acc_train = accuracy_score(y_train, y_pred_train)
    acc_test = accuracy_score(y_test, y_pred_test)
    f1_train = f1_score(y_train, y_pred_train)
    f1_test = f1_score(y_test, y_pred_test)

    accuracy_drop = round(acc_train - acc_test, 4)

    result = {
        "topic": topic,
        "timestamp": str(dt.datetime.utcnow()),
        "old_date": old_date,
        "new_date": new_date,
        "train_acc": acc_train,
        "test_acc": acc_test,
        "train_f1": f1_train,
        "test_f1": f1_test,
        "accuracy_drop": accuracy_drop,
        "status": "Concept Drift Detected" if accuracy_drop > 0.15 else "Stable"
    }

    ensure_dir("drift_reports/concept")
    path = os.path.join("drift_reports/concept", f"{topic.replace(' ', '_')}_concept_drift_{new_date}.json")
    save_json(result, path)

    logger.info(f"✅ Concept drift for '{topic}' saved → {path}")
    logger.info(f"   Accuracy Drop: {accuracy_drop:.4f} | Status: {result['status']}")
    return result


# ---------- Runner ----------
def run_concept_drift(base_dir="data_pipeline/data/processed/embeddings"):
    if not os.path.exists(base_dir):
        logger.error(f"Embedding directory not found: {base_dir}")
        return

    date_dirs = sorted(d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)))
    if len(date_dirs) < 2:
        logger.warning("Not enough snapshots for concept drift.")
        return

    for i in range(1, len(date_dirs)):
        old_date, new_date = date_dirs[i - 1], date_dirs[i]
        old_dir, new_dir = os.path.join(base_dir, old_date), os.path.join(base_dir, new_date)

        old_files = {os.path.splitext(f)[0]: os.path.join(old_dir, f) for f in os.listdir(old_dir) if f.endswith(".npy")}
        new_files = {os.path.splitext(f)[0]: os.path.join(new_dir, f) for f in os.listdir(new_dir) if f.endswith(".npy")}
        common_topics = set(old_files) & set(new_files)

        logger.info(f"🔹 Evaluating concept drift: {old_date} → {new_date}")
        for topic_file in common_topics:
            topic_name = topic_file.replace("_", " ")
            compute_concept_drift(topic_name, old_files[topic_file], new_files[topic_file], old_date, new_date)

    logger.info("✅ All concept drift computations completed.")


if __name__ == "__main__":
    run_concept_drift()
