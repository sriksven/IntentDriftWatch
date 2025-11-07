"""
Module: train_xgb.py
Purpose: Train and persist XGBoost classifier for intent/topic modeling.
"""

import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from api.utils.embeddings import Embedder
from data_pipeline.generate_embeddings import preprocess_texts
import joblib
import os, logging
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class XGBTrainer:
    def __init__(self, model_dir: str = "api/model_store/"):
        self.model_dir = model_dir
        self.embedder = Embedder()
        os.makedirs(self.model_dir, exist_ok=True)

    def train(self, texts: list[str], labels: list[int]) -> dict:
        if len(texts) != len(labels):
            raise ValueError("Texts and labels must have the same length.")

        logger.info("Preprocessing and embedding texts...")
        X_texts = preprocess_texts(texts)
        X = self.embedder.encode_texts(X_texts)
        y = np.array(labels)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.8,
            use_label_encoder=False,
            eval_metric="logloss"
        )

        logger.info("Training XGBoost model...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        logger.info(f"Model accuracy: {acc:.3f}")

        model.save_model(os.path.join(self.model_dir, "xgboost_model.json"))
        joblib.dump({"labels": list(set(labels))},
                    os.path.join(self.model_dir, "label_encoder.pkl"))

        return {"accuracy": round(acc, 4), "model_path": self.model_dir}
