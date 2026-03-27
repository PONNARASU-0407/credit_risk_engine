"""
Model Training Script with Feature Alignment
CRITICAL: Ensures no feature mismatch during training and prediction
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error, classification_report
import lightgbm as lgb
import joblib
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from utils.preprocessing import DataPreprocessor, FeatureAligner

def load_and_prepare_data():
    """
    Load and prepare data for training
    """
    print("Loading dataset...")
    df = pd.read_csv(config.DATASET_PATH)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Remove customer_id as it's not a feature
    if 'customer_id' in df.columns:
        df = df.drop('customer_id', axis=1)
    
    return df

import lightgbm as lgb
import numpy as np
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

def train_approval_model(X_train, y_train, X_test, y_test):
    """
    Train loan approval classification model
    """
    print("\n" + "="*50)
    print("Training Approval Classification Model...")
    print("="*50)
    
    # Convert target to binary (Approved=1, Rejected=0)
    y_train_binary = (y_train == 'Approved').astype(int)
    y_test_binary = (y_test == 'Approved').astype(int)
    
    # Train LightGBM model
    model = lgb.LGBMClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    model.fit(X_train, y_train_binary,
             eval_set=[(X_test, y_test_binary)],
             eval_metric='auc')
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Evaluation
    accuracy = accuracy_score(y_test_binary, y_pred)
    auc = roc_auc_score(y_test_binary, y_pred_proba)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print(f"AUC-ROC: {auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test_binary, y_pred, 
                                target_names=['Rejected', 'Approved']))
    
    return model


def train_default_probability_model(X_train, y_train, X_test, y_test):
    """
    Train probability of default regression model
    """
    print("\n" + "="*50)
    print("Training Probability of Default Model...")
    print("="*50)
    
    # Train LightGBM regressor
    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    model.fit(X_train, y_train,
             eval_set=[(X_test, y_test)],
             eval_metric='rmse')
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Evaluation
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    print(f"\nRMSE: {rmse:.4f}")
    print(f"Mean Absolute Error: {np.mean(np.abs(y_test - y_pred)):.4f}")
    
    return model

def train_safe_amount_model(X_train, y_train, X_test, y_test):
    """
    Train safe loan amount regression model
    """
    print("\n" + "="*50)
    print("Training Safe Loan Amount Model...")
    print("="*50)
    
    # Train LightGBM regressor
    model = lgb.LGBMRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    model.fit(X_train, y_train,
             eval_set=[(X_test, y_test)],
             eval_metric='rmse')
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Evaluation
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    print(f"\nRMSE: {rmse:.4f}")
    print(f"Mean Absolute Error: {np.mean(np.abs(y_test - y_pred)):.4f}")
    
    return model

def main():
    """
    Main training pipeline
    """
    print("="*70)
    print("ENTERPRISE CREDIT RISK ENGINE - MODEL TRAINING")
    print("="*70)
    
    # Create directories
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    
    # Load data
    df = load_and_prepare_data()
    
    # Separate features and targets
    print("\nPreparing features and targets...")
    
    # Get feature columns (all except targets)
    feature_cols = [col for col in df.columns if col not in 
                   [config.TARGET_APPROVAL, config.TARGET_DEFAULT, config.TARGET_SAFE_AMOUNT]]
    
    X = df[feature_cols].copy()
    y_approval = df[config.TARGET_APPROVAL].copy()
    y_default = df[config.TARGET_DEFAULT].copy()
    y_safe_amount = df[config.TARGET_SAFE_AMOUNT].copy()
    # Remove non-predictive ID columns
    if 'gst_number' in X.columns:
         X = X.drop(columns=['gst_number'])


   
    
    print(f"\nFeature columns ({len(feature_cols)}): {feature_cols}")
    print(f"\nTarget 1 - Approval: {y_approval.value_counts().to_dict()}")
    print(f"Target 2 - Default Probability: Mean={y_default.mean():.3f}, Std={y_default.std():.3f}")
    print(f"Target 3 - Safe Amount: Mean={y_safe_amount.mean():.0f}, Std={y_safe_amount.std():.0f}")
    
    # Initialize preprocessor
    print("\nInitializing preprocessor...")
    preprocessor = DataPreprocessor()
    
    # Fit and transform features
    print("Preprocessing features...")
    X_processed = preprocessor.fit(X)
    
    print(f"Processed features shape: {X_processed.shape}")
    print(f"Feature columns after preprocessing: {X_processed.columns.tolist()}")
    
    # Save preprocessor
    preprocessor.save(config.LABEL_ENCODERS_PATH)
    print(f"Saved preprocessor to: {config.LABEL_ENCODERS_PATH}")
    
    # Save feature columns order
    joblib.dump(X_processed.columns.tolist(), config.FEATURE_COLUMNS_PATH)
    print(f"Saved feature columns to: {config.FEATURE_COLUMNS_PATH}")
    
    # Split data
    print("\nSplitting data...")
    X_train, X_test, y_approval_train, y_approval_test = train_test_split(
        X_processed, y_approval, test_size=0.2, random_state=42, stratify=y_approval
    )
    
    _, _, y_default_train, y_default_test = train_test_split(
        X_processed, y_default, test_size=0.2, random_state=42, stratify=y_approval
    )
    
    _, _, y_safe_amount_train, y_safe_amount_test = train_test_split(
        X_processed, y_safe_amount, test_size=0.2, random_state=42, stratify=y_approval
    )
    
    print(f"Training set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Train models
    approval_model = train_approval_model(X_train, y_approval_train, X_test, y_approval_test)
    default_model = train_default_probability_model(X_train, y_default_train, X_test, y_default_test)
    safe_amount_model = train_safe_amount_model(X_train, y_safe_amount_train, X_test, y_safe_amount_test)
    
    # Save models
    print("\n" + "="*50)
    print("Saving models...")
    print("="*50)
    
    joblib.dump(approval_model, config.APPROVAL_MODEL_PATH)
    print(f"Saved approval model to: {config.APPROVAL_MODEL_PATH}")
    
    joblib.dump(default_model, config.DEFAULT_MODEL_PATH)
    print(f"Saved default model to: {config.DEFAULT_MODEL_PATH}")
    
    joblib.dump(safe_amount_model, config.SAFE_AMOUNT_MODEL_PATH)
    print(f"Saved safe amount model to: {config.SAFE_AMOUNT_MODEL_PATH}")
    
    # Verify feature alignment
    print("\n" + "="*50)
    print("FEATURE ALIGNMENT VERIFICATION")
    print("="*50)
    
    print(f"\nExpected feature order:")
    for i, col in enumerate(X_processed.columns.tolist()):
        print(f"  {i+1}. {col}")
    
    print("\nModel training complete!")
    print("="*70)

if __name__ == "__main__":
    main()
