"""
Preprocessing utilities with strict feature alignment
CRITICAL: Ensures no feature name or order mismatch
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import config

class FeatureAligner:
    """
    Ensures features are always aligned correctly between training and prediction
    """
    
    def __init__(self, feature_columns=None):
        """
        Initialize with feature columns in exact order
        
        Args:
            feature_columns: List of feature names in exact order
        """
        self.feature_columns = feature_columns if feature_columns else config.ALL_FEATURES_ORDERED
    
    def align_features(self, df, loan_type=None):
        """
        Align DataFrame columns to match training feature order exactly
        
        Args:
            df: Input DataFrame
            loan_type: Loan type (if single prediction)
        
        Returns:
            Aligned DataFrame with exact feature columns in exact order
        """
        # Create a DataFrame with all expected columns initialized to 0
        aligned_df = pd.DataFrame(0, index=df.index, columns=self.feature_columns)
        
        # Fill in values for columns that exist in input
        for col in df.columns:
            if col in self.feature_columns:
                aligned_df[col] = df[col]
        
        # Ensure correct data types
        # Ensure numeric types for ALL columns (LightGBM requirement)
        for col in self.feature_columns:
            aligned_df[col] = pd.to_numeric(aligned_df[col], errors='coerce').fillna(0)        
        return aligned_df[self.feature_columns]  # Return in exact order
    
    def save(self, filepath):
        """Save feature columns order"""
        joblib.dump(self.feature_columns, filepath)
    
    @staticmethod
    def load(filepath):
        """Load feature columns order"""
        feature_columns = joblib.load(filepath)
        return FeatureAligner(feature_columns)


class DataPreprocessor:
    """
    Handles all data preprocessing with feature alignment
    """
    
    def __init__(self):
        self.label_encoders = {}
        self.feature_aligner = FeatureAligner()
    
    def fit(self, df):
        """
        Fit encoders on training data
        
        Args:
            df: Training DataFrame
        
        Returns:
            Preprocessed DataFrame
        """
        df_processed = df.copy()
        
        # Encode categorical features
        for col in config.CATEGORICAL_FEATURES:
            if col in df_processed.columns:
                le = LabelEncoder()
                # Handle missing values
                df_processed[col] = df_processed[col].fillna('Unknown')
                df_processed[col] = df_processed[col].astype(str)
                
                # Fit and transform
                df_processed[col] = le.fit_transform(df_processed[col])
                self.label_encoders[col] = le
        
        # Handle numerical features
        for col in config.NUMERICAL_FEATURES:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)
        
        # Align features to ensure correct order
        df_processed = self.feature_aligner.align_features(df_processed)
        
        return df_processed
    
    def transform(self, df):
        """
        Transform new data using fitted encoders
        
        Args:
            df: DataFrame to transform
        
        Returns:
            Preprocessed DataFrame with aligned features
        """
        df_processed = df.copy()
        
        # Encode categorical features
        for col in config.CATEGORICAL_FEATURES:
            if col in df_processed.columns and col in self.label_encoders:
                le = self.label_encoders[col]
                
                # Handle missing values
                df_processed[col] = df_processed[col].fillna('Unknown')
                df_processed[col] = df_processed[col].astype(str)
                
                # Transform, handling unseen labels
                df_processed[col] = df_processed[col].apply(
                    lambda x: le.transform([x])[0] if x in le.classes_ else -1
                )
        
        # Handle numerical features
        for col in config.NUMERICAL_FEATURES:
            if col in df_processed.columns:
                df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce').fillna(0)
        
        # Align features to ensure correct order - CRITICAL STEP
        df_processed = self.feature_aligner.align_features(df_processed)
        
        return df_processed
    
    def save(self, filepath):
        """Save preprocessor"""
        joblib.dump({
            'label_encoders': self.label_encoders,
            'feature_columns': self.feature_aligner.feature_columns
        }, filepath)
    
    @staticmethod
    def load(filepath):
        """Load preprocessor"""
        data = joblib.load(filepath)
        preprocessor = DataPreprocessor()
        preprocessor.label_encoders = data['label_encoders']
        preprocessor.feature_aligner = FeatureAligner(data['feature_columns'])
        return preprocessor


def prepare_single_prediction(form_data, loan_type, preprocessor):
    """
    Prepare a single loan application for prediction
    Ensures no feature mismatch
    
    Args:
        form_data: Dictionary of form data
        loan_type: Type of loan
        preprocessor: Fitted DataPreprocessor
    
    Returns:
        Preprocessed DataFrame ready for prediction
    """
    # Create a dictionary with all features initialized
    feature_dict = {col: 0 for col in config.ALL_FEATURES_ORDERED}
    
    # Fill in common features
    for key, value in form_data.items():
        if key in config.ALL_FEATURES_ORDERED:
            feature_dict[key] = value
    
    # Set loan type
    feature_dict['loan_type'] = loan_type
    
    # Handle loan-type specific features
    # For features not relevant to this loan type, they remain 0
    if loan_type == 'Home':
        for field in config.LOAN_TYPE_FEATURES['Home']:
            if field in form_data:
                feature_dict[field] = form_data[field]
    
    elif loan_type == 'Gold':
        for field in config.LOAN_TYPE_FEATURES['Gold']:
            if field in form_data:
                feature_dict[field] = form_data[field]
    
    elif loan_type == 'Business':
        for field in config.LOAN_TYPE_FEATURES['Business']:
            if field in form_data:
                feature_dict[field] = form_data[field]
    
    elif loan_type == 'Educational':
        for field in config.LOAN_TYPE_FEATURES['Educational']:
            if field in form_data:
                feature_dict[field] = form_data[field]
    
    # Create DataFrame
    df = pd.DataFrame([feature_dict])
    
    # Preprocess
    df_processed = preprocessor.transform(df)
    
    return df_processed


def get_feature_names_from_model(model):
    """
    Get feature names from trained model
    
    Args:
        model: Trained model
    
    Returns:
        List of feature names
    """
    if hasattr(model, 'feature_name_'):
        return model.feature_name_
    elif hasattr(model, 'feature_names_'):
        return model.feature_names_
    else:
        return config.ALL_FEATURES_ORDERED
