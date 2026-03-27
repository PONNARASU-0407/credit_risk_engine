"""
SHAP-based explainability utilities
"""

import shap
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import base64
from io import BytesIO
import config


class SHAPExplainer:
    """
    Handles SHAP explanations for model predictions
    """

    def __init__(self, model, X_train_sample=None):

        self.model = model
        self.X_train_sample = X_train_sample

        try:
            self.explainer = shap.TreeExplainer(model)
        except Exception as e:
            print("TreeExplainer failed, using KernelExplainer:", e)

            if X_train_sample is not None:
                self.explainer = shap.KernelExplainer(model.predict, X_train_sample)
            else:
                self.explainer = None

    def explain_prediction(self, X, feature_names=None):

        if self.explainer is None:
            print("SHAP explainer not available")
            return None

        try:

            # Generate SHAP values
            shap_values = self.explainer.shap_values(X)

            # Handle binary classification
            if isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

            # Handle new SHAP Explanation object
            if hasattr(shap_values, "values"):
                shap_values = shap_values.values

            shap_values = np.array(shap_values)

            print("SHAP values generated successfully")

        except Exception as e:
            print("SHAP calculation error:", e)
            return None

        # Feature names
        if feature_names is None:
            if hasattr(X, 'columns'):
                feature_names = X.columns.tolist()
            else:
                feature_names = [f'Feature_{i}' for i in range(X.shape[1])]

        try:

            force_plot_html = self._create_force_plot(shap_values[0], X, feature_names)
            waterfall_plot = self._create_waterfall_plot(shap_values[0], X, feature_names)
            importance_plot = self._create_feature_importance_plot(shap_values[0], feature_names)

            top_features = self._get_top_features(shap_values[0], feature_names)

            base_value = 0
            if hasattr(self.explainer, 'expected_value'):
                base_value = self.explainer.expected_value
                if isinstance(base_value, list):
                    base_value = base_value[1] if len(base_value) > 1 else base_value[0]

            return {

                'shap_values': shap_values[0].tolist(),
                'feature_names': feature_names,
                'force_plot_html': force_plot_html,
                'waterfall_plot': waterfall_plot,
                'importance_plot': importance_plot,
                'top_features': top_features,
                'base_value': float(base_value)

            }

        except Exception as e:
            print("Error building SHAP explanation:", e)
            return None

    def _create_force_plot(self, shap_values, X, feature_names):

        try:

            if hasattr(self.explainer, 'expected_value'):

                base_value = self.explainer.expected_value

                if isinstance(base_value, list):
                    base_value = base_value[1] if len(base_value) > 1 else base_value[0]

                force_plot = shap.force_plot(

                    base_value,
                    shap_values,
                    X.iloc[0] if hasattr(X, 'iloc') else X[0],
                    feature_names=feature_names,
                    matplotlib=False

                )

                return shap.getjs() + force_plot.html()

            return None

        except Exception as e:

            print("Force plot error:", e)
            return None

    def _create_waterfall_plot(self, shap_values, X, feature_names):

        try:

            plt.figure(figsize=(10, 6))

            shap_df = pd.DataFrame({

                'Feature': feature_names,
                'SHAP Value': shap_values

            })

            shap_df = shap_df.reindex(shap_df['SHAP Value'].abs().sort_values(ascending=False).index)

            top_10 = shap_df.head(10)

            colors = ['green' if x > 0 else 'red' for x in top_10['SHAP Value']]

            plt.barh(top_10['Feature'], top_10['SHAP Value'], color=colors)

            plt.xlabel('SHAP Value (Impact on Prediction)')
            plt.title('Top 10 Feature Contributions')

            plt.tight_layout()

            buffer = BytesIO()

            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')

            buffer.seek(0)

            image_base64 = base64.b64encode(buffer.read()).decode()

            plt.close()

            return image_base64

        except Exception as e:

            print("Waterfall plot error:", e)
            return None

    def _create_feature_importance_plot(self, shap_values, feature_names):

        try:

            plt.figure(figsize=(10, 6))

            importance_df = pd.DataFrame({

                'Feature': feature_names,
                'Importance': np.abs(shap_values)

            })

            importance_df = importance_df.sort_values('Importance', ascending=False).head(10)

            plt.barh(

                importance_df['Feature'],
                importance_df['Importance'],
                color='steelblue'

            )

            plt.xlabel('Absolute SHAP Value (Feature Importance)')
            plt.title('Top 10 Most Important Features')

            plt.tight_layout()

            buffer = BytesIO()

            plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')

            buffer.seek(0)

            image_base64 = base64.b64encode(buffer.read()).decode()

            plt.close()

            return image_base64

        except Exception as e:

            print("Importance plot error:", e)
            return None

    def _get_top_features(self, shap_values, feature_names, top_n=10):

        feature_impact = []

        for feature, value in zip(feature_names, shap_values):

            feature_impact.append({

                'feature': feature,
                'shap_value': float(value),
                'impact': 'Positive' if value > 0 else 'Negative',
                'abs_value': abs(float(value))

            })

        feature_impact.sort(key=lambda x: x['abs_value'], reverse=True)

        return feature_impact[:top_n]


def create_shap_summary_for_display(shap_explanation):

    if not shap_explanation or 'top_features' not in shap_explanation:
        return None

    summary = {

        'top_positive': [],
        'top_negative': [],
        'summary_text': ''

    }

    for feature in shap_explanation['top_features']:

        feature_info = {

            'name': feature['feature'].replace('_', ' ').title(),
            'value': abs(feature['shap_value']),
            'impact': feature['impact']

        }

        if feature['shap_value'] > 0:
            summary['top_positive'].append(feature_info)
        else:
            summary['top_negative'].append(feature_info)

    if summary['top_positive']:

        pos_features = ', '.join([f['name'] for f in summary['top_positive'][:3]])

        summary['summary_text'] += f"Factors supporting approval: {pos_features}. "

    if summary['top_negative']:

        neg_features = ', '.join([f['name'] for f in summary['top_negative'][:3]])

        summary['summary_text'] += f"Factors against approval: {neg_features}."

    return summary