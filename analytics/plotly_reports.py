"""
Module: plotly_reports.py
Purpose: Generate interactive HTML drift reports using Plotly
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from data_pipeline.utils.io_utils import ensure_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Semantic Drift Visualization ----------
def generate_semantic_drift_report(topic, old_emb_path, new_emb_path, old_date, new_date):
    """Generate interactive Plotly-based semantic drift visualization."""
    try:
        ensure_dir("drift_reports/visual")
        
        old_emb = np.load(old_emb_path)
        new_emb = np.load(new_emb_path)

        n = min(len(old_emb), len(new_emb))
        if n == 0:
            logger.warning(f"No samples available for semantic drift visualization: {topic}")
            return None

        old_emb, new_emb = old_emb[:n], new_emb[:n]

        # Compute statistics
        old_mean = old_emb.mean(axis=0)
        new_mean = new_emb.mean(axis=0)
        old_std = old_emb.std(axis=0)
        new_std = new_emb.std(axis=0)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Mean Embedding Values Comparison',
                'Standard Deviation Comparison',
                'Embedding Distribution (First 3 Dimensions)',
                'Feature Drift Magnitude'
            ),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'scatter3d'}, {'type': 'bar'}]]
        )

        # Plot 1: Mean comparison
        feature_indices = np.arange(len(old_mean))
        fig.add_trace(
            go.Scatter(x=feature_indices, y=old_mean, name=f'Old ({old_date})', 
                      mode='lines', line=dict(color='blue')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=feature_indices, y=new_mean, name=f'New ({new_date})', 
                      mode='lines', line=dict(color='red')),
            row=1, col=1
        )

        # Plot 2: Std deviation comparison
        fig.add_trace(
            go.Scatter(x=feature_indices, y=old_std, name=f'Old Std ({old_date})', 
                      mode='lines', line=dict(color='lightblue')),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=feature_indices, y=new_std, name=f'New Std ({new_date})', 
                      mode='lines', line=dict(color='lightcoral')),
            row=1, col=2
        )

        # Plot 3: 3D scatter (first 3 dimensions)
        sample_size = min(500, n)  # Limit samples for performance
        old_sample = old_emb[:sample_size]
        new_sample = new_emb[:sample_size]
        
        fig.add_trace(
            go.Scatter3d(
                x=old_sample[:, 0], y=old_sample[:, 1], z=old_sample[:, 2],
                mode='markers', name=f'Old ({old_date})',
                marker=dict(size=3, color='blue', opacity=0.5)
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter3d(
                x=new_sample[:, 0], y=new_sample[:, 1], z=new_sample[:, 2],
                mode='markers', name=f'New ({new_date})',
                marker=dict(size=3, color='red', opacity=0.5)
            ),
            row=2, col=1
        )

        # Plot 4: Feature drift magnitude
        drift_magnitude = np.abs(new_mean - old_mean)
        top_drifted = np.argsort(drift_magnitude)[-20:]  # Top 20 drifted features
        
        fig.add_trace(
            go.Bar(
                x=top_drifted, y=drift_magnitude[top_drifted],
                name='Drift Magnitude',
                marker=dict(color=drift_magnitude[top_drifted], colorscale='Reds')
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title_text=f"Semantic Drift Analysis: {topic}<br>{old_date} → {new_date}",
            showlegend=True,
            height=1000,
            template='plotly_white'
        )

        fig.update_xaxes(title_text="Feature Index", row=1, col=1)
        fig.update_yaxes(title_text="Mean Value", row=1, col=1)
        fig.update_xaxes(title_text="Feature Index", row=1, col=2)
        fig.update_yaxes(title_text="Std Deviation", row=1, col=2)
        fig.update_xaxes(title_text="Feature Index", row=2, col=2)
        fig.update_yaxes(title_text="Drift Magnitude", row=2, col=2)

        output_path = os.path.join(
            "drift_reports/visual",
            f"{topic.replace(' ', '_')}_semantic_drift_{new_date}.html"
        )
        fig.write_html(output_path)
        logger.info(f"📊 Plotly semantic drift report saved → {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"❌ Failed to generate Plotly semantic drift report for {topic}: {e}")
        import traceback
        traceback.print_exc()
        return None


# ---------- Concept Drift Visualization ----------
def generate_concept_drift_report(topic, y_train, y_pred_train, y_test, y_pred_test, new_date):
    """Generate interactive Plotly-based concept drift visualization."""
    try:
        ensure_dir("drift_reports/visual")

        from sklearn.metrics import confusion_matrix, classification_report

        # Calculate confusion matrices
        cm_train = confusion_matrix(y_train, y_pred_train)
        cm_test = confusion_matrix(y_test, y_pred_test)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Training Set Confusion Matrix',
                'Test Set Confusion Matrix',
                'Prediction Distribution',
                'Performance Metrics'
            ),
            specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )

        # Plot 1: Training confusion matrix
        fig.add_trace(
            go.Heatmap(
                z=cm_train,
                x=['Old (0)', 'New (1)'],
                y=['Old (0)', 'New (1)'],
                colorscale='Blues',
                text=cm_train,
                texttemplate='%{text}',
                showscale=True
            ),
            row=1, col=1
        )

        # Plot 2: Test confusion matrix
        fig.add_trace(
            go.Heatmap(
                z=cm_test,
                x=['Old (0)', 'New (1)'],
                y=['Old (0)', 'New (1)'],
                colorscale='Reds',
                text=cm_test,
                texttemplate='%{text}',
                showscale=True
            ),
            row=1, col=2
        )

        # Plot 3: Prediction distribution
        train_dist = pd.Series(y_pred_train).value_counts().sort_index()
        test_dist = pd.Series(y_pred_test).value_counts().sort_index()
        
        fig.add_trace(
            go.Bar(name='Train', x=['Old (0)', 'New (1)'], y=train_dist.values, 
                   marker_color='lightblue'),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(name='Test', x=['Old (0)', 'New (1)'], y=test_dist.values, 
                   marker_color='lightcoral'),
            row=2, col=1
        )

        # Plot 4: Performance metrics
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        train_f1 = f1_score(y_train, y_pred_train, average='weighted')
        test_f1 = f1_score(y_test, y_pred_test, average='weighted')
        
        metrics_names = ['Accuracy', 'F1-Score']
        train_metrics = [train_acc, train_f1]
        test_metrics = [test_acc, test_f1]
        
        fig.add_trace(
            go.Bar(name='Train', x=metrics_names, y=train_metrics, 
                   marker_color='blue', text=[f'{v:.3f}' for v in train_metrics],
                   textposition='auto'),
            row=2, col=2
        )
        fig.add_trace(
            go.Bar(name='Test', x=metrics_names, y=test_metrics, 
                   marker_color='red', text=[f'{v:.3f}' for v in test_metrics],
                   textposition='auto'),
            row=2, col=2
        )

        # Update layout
        drift_status = "Significant Drift" if test_acc > 0.75 else "Moderate Drift" if test_acc > 0.60 else "Stable"
        
        fig.update_layout(
            title_text=f"Concept Drift Analysis: {topic}<br>Status: {drift_status} (Test Acc: {test_acc:.3f})",
            showlegend=True,
            height=1000,
            template='plotly_white'
        )

        fig.update_xaxes(title_text="Predicted", row=1, col=1)
        fig.update_yaxes(title_text="Actual", row=1, col=1)
        fig.update_xaxes(title_text="Predicted", row=1, col=2)
        fig.update_yaxes(title_text="Actual", row=1, col=2)
        fig.update_yaxes(title_text="Count", row=2, col=1)
        fig.update_yaxes(title_text="Score", row=2, col=2)

        output_path = os.path.join(
            "drift_reports/visual",
            f"{topic.replace(' ', '_')}_concept_drift_{new_date}.html"
        )
        fig.write_html(output_path)
        logger.info(f"📈 Plotly concept drift report saved → {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"❌ Failed to generate Plotly concept drift report for {topic}: {e}")
        import traceback
        traceback.print_exc()
        return None