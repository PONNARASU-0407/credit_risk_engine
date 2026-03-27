"""
CSV Handler for data storage operations
"""
import pandas as pd
import os
import config
from datetime import datetime

class CSVHandler:
    """
    Handles all CSV read/write operations
    """
    
    @staticmethod
    def initialize_csv_files():
        """Initialize CSV files if they don't exist"""

        # Initialize user applications CSV
        if not os.path.exists(config.USER_APPLICATIONS_PATH):
            columns = ['application_id', 'username', 'submission_date', 'loan_type', 'status'] + config.ALL_FEATURES_ORDERED
            df = pd.DataFrame(columns=columns)
            df.to_csv(config.USER_APPLICATIONS_PATH, index=False)

        # Initialize admin predictions CSV
        if not os.path.exists(config.ADMIN_PREDICTIONS_PATH):
            columns = [
                'application_id',
                'prediction_date',
                'approval_status',
                'probability_of_default',
                'safe_loan_amount',
                'emi_amount',
                'emi_income_ratio',
                'processed_by',
                'shap_summary'   # ✅ Added
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(config.ADMIN_PREDICTIONS_PATH, index=False)

    @staticmethod
    def save_user_application(application_data):
        """
        Save user application to CSV
        """
        try:

            if os.path.exists(config.USER_APPLICATIONS_PATH):
                df = pd.read_csv(config.USER_APPLICATIONS_PATH)
            else:
                columns = ['application_id', 'username', 'submission_date', 'loan_type', 'status'] + config.ALL_FEATURES_ORDERED
                df = pd.DataFrame(columns=columns)

            new_row = {
                'application_id': application_data['application_id'],
                'username': application_data['username'],
                'submission_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'loan_type': application_data['loan_type'],
                'status': 'Pending'
            }

            for col in config.ALL_FEATURES_ORDERED:
                new_row[col] = application_data.get(col, 0)

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(config.USER_APPLICATIONS_PATH, index=False)

            return True

        except Exception as e:
            print(f"Error saving application: {e}")
            return False

    @staticmethod
    def save_admin_prediction(prediction_data):
        """
        Save admin prediction to CSV
        """
        try:

            if os.path.exists(config.ADMIN_PREDICTIONS_PATH):
                df = pd.read_csv(config.ADMIN_PREDICTIONS_PATH)
            else:
                columns = [
                    'application_id',
                    'prediction_date',
                    'approval_status',
                    'probability_of_default',
                    'safe_loan_amount',
                    'emi_amount',
                    'emi_income_ratio',
                    'processed_by',
                    'shap_summary'  # ✅ Added
                ]
                df = pd.DataFrame(columns=columns)

            new_row = {
                'application_id': prediction_data['application_id'],
                'prediction_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'approval_status': prediction_data['approval_status'],
                'probability_of_default': prediction_data['probability_of_default'],
                'safe_loan_amount': prediction_data['safe_loan_amount'],
                'emi_amount': prediction_data['emi_amount'],
                'emi_income_ratio': prediction_data['emi_income_ratio'],
                'processed_by': prediction_data.get('processed_by', 'admin'),
                'shap_summary': prediction_data.get('shap_summary', '')  # ✅ Added
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(config.ADMIN_PREDICTIONS_PATH, index=False)

            CSVHandler.update_application_status(
                prediction_data['application_id'],
                prediction_data['approval_status']
            )

            return True

        except Exception as e:
            print(f"Error saving prediction: {e}")
            return False

    @staticmethod
    def get_pending_applications():
        try:
            if not os.path.exists(config.USER_APPLICATIONS_PATH):
                return pd.DataFrame()

            df = pd.read_csv(config.USER_APPLICATIONS_PATH)
            pending_df = df[df['status'] == 'Pending']
            return pending_df

        except Exception as e:
            print(f"Error getting pending applications: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_application_by_id(application_id):
        try:

            if not os.path.exists(config.USER_APPLICATIONS_PATH):
                return None

            df = pd.read_csv(config.USER_APPLICATIONS_PATH)

            df['application_id'] = df['application_id'].astype(str).str.strip()
            df['username'] = df['username'].astype(str).str.strip().str.lower()

            application_id = str(application_id).strip()

            app_df = df[df['application_id'] == application_id]

            if len(app_df) == 0:
                return None

            return app_df.iloc[0].to_dict()

        except Exception as e:
            print(f"Error getting application: {e}")
            return None

    @staticmethod
    def get_prediction_by_id(application_id):
        try:

            if not os.path.exists(config.ADMIN_PREDICTIONS_PATH):
                return None

            df = pd.read_csv(config.ADMIN_PREDICTIONS_PATH)

            pred_df = df[df['application_id'] == application_id]

            if len(pred_df) == 0:
                return None

            return pred_df.iloc[0].to_dict()

        except Exception as e:
            print(f"Error getting prediction: {e}")
            return None

    @staticmethod
    def update_application_status(application_id, status):

        try:

            if not os.path.exists(config.USER_APPLICATIONS_PATH):
                return False

            df = pd.read_csv(config.USER_APPLICATIONS_PATH)

            df.loc[df['application_id'] == application_id, 'status'] = status

            df.to_csv(config.USER_APPLICATIONS_PATH, index=False)

            return True

        except Exception as e:
            print(f"Error updating status: {e}")
            return False

    @staticmethod
    def get_all_applications_for_user(username):

        try:

            if not os.path.exists(config.USER_APPLICATIONS_PATH):
                return pd.DataFrame()

            df = pd.read_csv(config.USER_APPLICATIONS_PATH)

            user_df = df[df['username'] == username]

            return user_df.sort_values('submission_date', ascending=False)

        except Exception as e:
            print(f"Error getting user applications: {e}")
            return pd.DataFrame()