"""
Module: evidently_reports.py
Purpose: Generate visual drift dashboards for semantic and concept drift using Evidently 0.7.x
"""

import os
import numpy as np
import pandas as pd
import datetime as dt
import logging
from data_pipeline.utils.io_utils import ensure_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Evidently - handle different versions gracefully
try:
    from evidently.reports import Report
    from evidently.test_suite import TestSuite
    EVIDENTLY_AVAILABLE = True
except ImportError:
    try:
        from evidently.report import Report
        EVIDENTLY_AVAILABLE = True
    except ImportError:
        EVIDENTLY_AVAILABLE = False
        logger.warning("⚠️ Evidently not properly installed. Visual reports will be skipped.")

if EVIDENTLY_AVAILABLE:
    try:
        from evidently.metric_preset import DataDriftPreset, ClassificationPreset
    except ImportError:
        try:
            from evidently.metrics import DataDriftTable, ClassificationQualityMetric
            DataDriftPreset = None
            ClassificationPreset = None
        except ImportError:
            EVIDENTLY_AVAILABLE = False


# ---------- Semantic Drift Report ----------
def generate_semantic_drift_report(topic, old_emb_path, new_emb_path, old_date, new_date):
    """Generate semantic drift visualization comparing embeddings between two dates."""
    
    if not EVIDENTLY_AVAILABLE:
        logger.info(f"⏭️  Skipping Evidently report for {topic} (Evidently not available)")
        return None
    
    try:
        ensure_dir("drift_reports/visual")
        old_emb = np.load(old_emb_path)
        new_emb = np.load(new_emb_path)

        n = min(len(old_emb), len(new_emb))
        if n == 0:
            logger.warning(f"No samples available for semantic drift visualization: {topic}")
            return None

        old_emb, new_emb = old_emb[:n], new_emb[:n]

        # Convert to DataFrames
        df_ref = pd.DataFrame(old_emb, columns=[f"feature_{i}" for i in range(old_emb.shape[1])])
        df_cur = pd.DataFrame(new_emb, columns=[f"feature_{i}" for i in range(new_emb.shape[1])])

        # Create report based on what's available
        if DataDriftPreset is not None:
            report = Report(metrics=[DataDriftPreset()])
        else:
            from evidently.metrics import DataDriftTable
            report = Report(metrics=[DataDriftTable()])
        
        report.run(reference_data=df_ref, current_data=df_cur)

        output_path = os.path.join(
            "drift_reports/visual",
            f"{topic.replace(' ', '_')}_semantic_drift_{new_date}.html"
        )
        report.save_html(output_path)
        logger.info(f"📊 Evidently semantic drift report saved → {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Evidently semantic drift report for {topic}: {e}")
        import traceback
        traceback.print_exc()
        return None


# ---------- Concept Drift Report ----------
def generate_concept_drift_report(topic, y_train, y_pred_train, y_test, y_pred_test, new_date):
    """Generate concept drift (classification performance) visualization."""
    
    if not EVIDENTLY_AVAILABLE:
        logger.info(f"⏭️  Skipping Evidently report for {topic} (Evidently not available)")
        return None
    
    try:
        ensure_dir("drift_reports/visual")

        n_train = len(y_train)
        n_test = len(y_test)

        # Create DataFrames with target and prediction columns
        df_ref = pd.DataFrame({
            "target": y_train.astype(str),
            "prediction": y_pred_train.astype(str)
        })
        df_cur = pd.DataFrame({
            "target": y_test.astype(str),
            "prediction": y_pred_test.astype(str)
        })

        # Create report based on what's available
        if ClassificationPreset is not None:
            report = Report(metrics=[ClassificationPreset()])
        else:
            from evidently.metrics import ClassificationQualityMetric
            report = Report(metrics=[ClassificationQualityMetric()])
        
        report.run(reference_data=df_ref, current_data=df_cur)

        output_path = os.path.join(
            "drift_reports/visual",
            f"{topic.replace(' ', '_')}_concept_drift_{new_date}.html"
        )
        report.save_html(output_path)
        logger.info(f"📈 Evidently concept drift report saved → {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Evidently concept drift report for {topic}: {e}")
        import traceback
        traceback.print_exc()
        return None