"""
Configuration file for Credit Risk Engine
"""
import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

# Create directories if they don't exist
for directory in [DATA_DIR, MODEL_DIR, LOG_DIR, TEMPLATE_DIR, STATIC_DIR]:
    os.makedirs(directory, exist_ok=True)

# Data files
DATASET_PATH = os.path.join(DATA_DIR, 'loan_dataset.csv')
USER_APPLICATIONS_PATH = os.path.join(DATA_DIR, 'user_applications.csv')
ADMIN_PREDICTIONS_PATH = os.path.join(DATA_DIR, 'admin_predictions.csv')

# Model files
APPROVAL_MODEL_PATH = os.path.join(MODEL_DIR, 'approval_model.pkl')
DEFAULT_MODEL_PATH = os.path.join(MODEL_DIR, 'default_probability_model.pkl')
SAFE_AMOUNT_MODEL_PATH = os.path.join(MODEL_DIR, 'safe_amount_model.pkl')
LABEL_ENCODERS_PATH = os.path.join(MODEL_DIR, 'label_encoders.pkl')
FEATURE_COLUMNS_PATH = os.path.join(MODEL_DIR, 'feature_columns.pkl')

# Flask settings
SECRET_KEY = 'your-secret-key-change-in-production-2024'
SESSION_TYPE = 'filesystem'

# Admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# User credentials (for demo - in production use proper authentication)
USER_CREDENTIALS = {
    'user1': 'pass123',
    'user2': 'pass456',
    'demo': 'demo123'
}

# Loan types
LOAN_TYPES = ['Home', 'Educational', 'Gold', 'Business']

# Common features for all loan types (in exact order)
COMMON_FEATURES = [
    'age', 'gender', 'city_type', 'employment_type', 'employment_years',
    'business_vintage_years', 'education_level', 'annual_income', 
    'monthly_income', 'dependents', 'credit_score', 'cibil_score',
    'requested_loan_amount', 'loan_tenure_months', 'interest_rate',
    'emi_amount', 'emi_income_ratio'
]

# Loan type specific features
LOAN_TYPE_FEATURES = {
    'Home': ['property_value', 'property_location', 'down_payment', 'property_type'],
    'Gold': ['gold_weight', 'gold_purity', 'gold_market_value'],
    'Business': ['business_turnover', 'years_in_business', 'business_type', 'gst_number'],
    'Educational': ['course_fee', 'college', 'course_duration', 'coapplicant_income']
}

# All features in exact order for model training (excluding target columns and customer_id)
ALL_FEATURES_ORDERED = [
    'age', 'gender', 'city_type', 'employment_type', 'employment_years',
    'business_vintage_years', 'education_level', 'annual_income', 
    'monthly_income', 'dependents', 'credit_score', 'cibil_score',
    'loan_type', 'requested_loan_amount', 'loan_tenure_months',
    'property_value', 'property_location', 'down_payment', 'property_type',
    'gold_weight', 'gold_purity', 'gold_market_value',
    'course_fee', 'college', 'course_duration', 'coapplicant_income',
    'business_turnover', 'years_in_business', 'business_type', 'gst_number',
    'interest_rate', 'emi_amount', 'emi_income_ratio'
]

# Categorical features
CATEGORICAL_FEATURES = [
    'gender', 'city_type', 'employment_type', 'education_level', 
    'loan_type', 'property_location', 'property_type', 'business_type', 
    'gst_number', 'college'
]

# Numerical features
NUMERICAL_FEATURES = [
    'age', 'employment_years', 'business_vintage_years', 'annual_income',
    'monthly_income', 'dependents', 'credit_score', 'cibil_score',
    'requested_loan_amount', 'loan_tenure_months', 'property_value',
    'down_payment', 'gold_weight', 'gold_purity', 'gold_market_value',
    'course_fee', 'course_duration', 'coapplicant_income',
    'business_turnover', 'years_in_business', 'interest_rate',
    'emi_amount', 'emi_income_ratio'
]

# Target columns
TARGET_APPROVAL = 'loan_approval_status'
TARGET_DEFAULT = 'probability_of_default'
TARGET_SAFE_AMOUNT = 'safe_loan_amount'

# Form field configurations
FORM_FIELDS = {
    'common': {
        'age': {'type': 'number', 'label': 'Age', 'required': True, 'min': 18, 'max': 100},
        'gender': {'type': 'select', 'label': 'Gender', 'required': True, 'options': ['Male', 'Female']},
        'city_type': {'type': 'select', 'label': 'City Type', 'required': True, 'options': ['Metro', 'Urban', 'Semi-Urban', 'Rural']},
        'employment_type': {'type': 'select', 'label': 'Employment Type', 'required': True, 'options': ['Salaried', 'Self-Employed', 'Student']},
        'employment_years': {'type': 'number', 'label': 'Employment Years', 'required': True, 'min': 0, 'max': 50},
        'business_vintage_years': {'type': 'number', 'label': 'Business Vintage Years', 'required': True, 'min': 0, 'max': 50},
        'education_level': {'type': 'select', 'label': 'Education Level', 'required': True, 'options': ['Graduate', 'Post-Graduate', 'Professional']},
        'annual_income': {'type': 'number', 'label': 'Annual Income (₹)', 'required': True, 'min': 0},
        'monthly_income': {'type': 'number', 'label': 'Monthly Income (₹)', 'required': True, 'min': 0},
        'dependents': {'type': 'number', 'label': 'Number of Dependents', 'required': True, 'min': 0, 'max': 10},
        'credit_score': {'type': 'number', 'label': 'Credit Score', 'required': True, 'min': 300, 'max': 900},
        'cibil_score': {'type': 'number', 'label': 'CIBIL Score', 'required': True, 'min': 300, 'max': 900},
        'requested_loan_amount': {'type': 'number', 'label': 'Requested Loan Amount (₹)', 'required': True, 'min': 10000},
        'loan_tenure_months': {'type': 'number', 'label': 'Loan Tenure (Months)', 'required': True, 'min': 6, 'max': 360},
        'interest_rate': {'type': 'number', 'label': 'Interest Rate (%)', 'required': True, 'min': 1, 'max': 30, 'step': 0.01}
    },
    'Home': {
        'property_value': {'type': 'number', 'label': 'Property Value (₹)', 'required': True, 'min': 100000},
        'property_location': {'type': 'select', 'label': 'Property Location', 'required': True, 'options': ['Metro', 'Urban', 'Semi-Urban', 'Rural']},
        'down_payment': {'type': 'number', 'label': 'Down Payment (₹)', 'required': True, 'min': 0},
        'property_type': {'type': 'select', 'label': 'Property Type', 'required': True, 'options': ['Apartment', 'Villa', 'Independent House']}
    },
    'Gold': {
        'gold_weight': {'type': 'number', 'label': 'Gold Weight (grams)', 'required': True, 'min': 1},
        'gold_purity': {'type': 'number', 'label': 'Gold Purity (karats)', 'required': True, 'min': 10, 'max': 24},
        'gold_market_value': {'type': 'number', 'label': 'Gold Market Value (₹)', 'required': True, 'min': 1000}
    },
    'Business': {
        'business_turnover': {'type': 'number', 'label': 'Business Turnover (₹)', 'required': True, 'min': 0},
        'years_in_business': {'type': 'number', 'label': 'Years in Business', 'required': True, 'min': 0, 'max': 50},
        'business_type': {'type': 'select', 'label': 'Business Type', 'required': True, 'options': ['Manufacturing', 'Retail', 'IT Services', 'Trading', 'Services']},
        'gst_number': {'type': 'text', 'label': 'GST Number', 'required': True, 'pattern': 'GST[0-9]{6}'}
    },
    'Educational': {
        'course_fee': {'type': 'number', 'label': 'Course Fee (₹)', 'required': True, 'min': 10000},
        'college': {'type': 'select', 'label': 'College Tier', 'required': True, 'options': ['Tier1', 'Tier2', 'Tier3']},
        'course_duration': {'type': 'number', 'label': 'Course Duration (Months)', 'required': True, 'min': 6, 'max': 120},
        'coapplicant_income': {'type': 'number', 'label': 'Co-applicant Income (₹)', 'required': True, 'min': 0}
    }
}

# Interest rate defaults by loan type
DEFAULT_INTEREST_RATES = {
    'Home': 8.5,
    'Gold': 10.0,
    'Business': 12.0,
    'Educational': 9.0
}
