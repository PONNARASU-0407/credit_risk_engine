"""
Enterprise Credit Risk Engine - Flask Application
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import pandas as pd
import numpy as np
import joblib
import os
import sys
from datetime import datetime
from io import BytesIO
import json


# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from utils.calculations import calculate_emi, calculate_emi_income_ratio, generate_application_id, validate_loan_application
from utils.preprocessing import DataPreprocessor, prepare_single_prediction
from utils.explainability import SHAPExplainer, create_shap_summary_for_display
from utils.pdf_generator import LoanApplicationPDF
from utils.csv_handler import CSVHandler

# Initialize Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['SESSION_TYPE'] = config.SESSION_TYPE

# Global variables for models
models_loaded = False
approval_model = None
default_model = None
safe_amount_model = None
preprocessor = None
feature_columns = None
# ================= SAFE CONVERSION =================

def safe_float(value, default=0.0):
    if value is None or str(value).strip() == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    if value is None or str(value).strip() == "":
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


def load_models():
    """Load all trained models"""
    global models_loaded, approval_model, default_model, safe_amount_model, preprocessor, feature_columns
    
    if models_loaded:
        return True
    
    try:
        # Check if models exist
        if not os.path.exists(config.APPROVAL_MODEL_PATH):
            print("Models not found. Please run train_models.py first.")
            return False
        
        # Load models
        approval_model = joblib.load(config.APPROVAL_MODEL_PATH)
        default_model = joblib.load(config.DEFAULT_MODEL_PATH)
        safe_amount_model = joblib.load(config.SAFE_AMOUNT_MODEL_PATH)
        
        # Load preprocessor
        preprocessor = DataPreprocessor.load(config.LABEL_ENCODERS_PATH)
        
        # Load feature columns
        feature_columns = joblib.load(config.FEATURE_COLUMNS_PATH)
        
        models_loaded = True
        print("All models loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def make_predictions(X_processed, loan_type,age, requested_amount, tenure, interest_rate, monthly_income,emi_amount):
    """
    Make predictions using all three models
    
    Returns:
        Dictionary with all prediction results
    """
    # Prediction 1: Approval Status
    approval_pred = approval_model.predict(X_processed)[0]
    approval_proba = approval_model.predict_proba(X_processed)[0]
    approval_status = 'Approved' if approval_pred == 1 else 'Rejected'
    
    # Prediction 2: Probability of Default
    default_prob = default_model.predict(X_processed)[0]
    default_prob = max(0, min(1, default_prob))  # Clip between 0 and 1
    
    # Prediction 3: Safe Loan Amount
    safe_amount = safe_amount_model.predict(X_processed)[0]
    safe_amount = max(0, safe_amount)  # Ensure non-negative
    
    # Calculate EMI based on approval status
    if approval_status == 'Approved':
        loan_amount_for_emi = requested_amount
    else:
        if (safe_amount > monthly_income * tenure) or (emi_amount > monthly_income):
            loan_amount_for_emi = monthly_income * tenure
        else:
            loan_amount_for_emi = safe_amount
    
    emi = calculate_emi(loan_amount_for_emi, interest_rate, tenure)
    emi_ratio = calculate_emi_income_ratio(emi, monthly_income)
    
    return {
        'approval_status': approval_status,
        'approval_probability': float(approval_proba[1]),
        'probability_of_default': float(default_prob),
        'safe_loan_amount': float(safe_amount),
        'emi_amount': float(emi),
        'emi_income_ratio': float(emi_ratio)
    }
def generate_shap_explanations(X_processed, model_type='approval'):
    """
    Generate SHAP explanations
    
    Args:
        X_processed: Preprocessed features
        model_type: 'approval', 'default', or 'safe_amount'
    
    Returns:
        SHAP explanation dictionary
    """
    try:
        # Select model
        if model_type == 'approval':
            model = approval_model
        elif model_type == 'default':
            model = default_model
        else:
            model = safe_amount_model
        
        # Create SHAP explainer
        explainer = SHAPExplainer(model)
        
        # Generate explanation
        shap_explanation = explainer.explain_prediction(X_processed, feature_columns)
        
        # Create summary
        shap_summary = create_shap_summary_for_display(shap_explanation)
        
        return shap_explanation, shap_summary
        
    except Exception as e:
        print(f"Error generating SHAP explanations: {e}")
        return None, None

# Initialize CSV files
CSVHandler.initialize_csv_files()

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials
        if username in config.USER_CREDENTIALS and config.USER_CREDENTIALS[username] == password:
            session['user_logged_in'] = True
            session['username'] = username
            session['user_type'] = 'user'
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('user_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check admin credentials
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['username'] = username
            session['user_type'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/user/dashboard')
def user_dashboard():
    """User dashboard"""
    if not session.get('user_logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('user_login'))
    
    username = session.get('username')
    
    # Get user's applications
    applications = CSVHandler.get_all_applications_for_user(username)
    
    return render_template('user_dashboard.html', 
                         username=username,
                         applications=applications.to_dict('records') if not applications.empty else [])

@app.route('/user/apply_loan', methods=['GET', 'POST'])
def apply_loan():
    """Loan application form"""
    if not session.get('user_logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('user_login'))
    
    if request.method == 'POST':
        try:
            # Get form data
            loan_type = request.form.get('loan_type')
            username = session.get('username')
            
            # Collect common fields
            form_data = {
    'age': safe_int(request.form.get('age')),
    'gender': request.form.get('gender', ''),
    'city_type': request.form.get('city_type', ''),
    'employment_type': request.form.get('employment_type', ''),
    'employment_years': safe_int(request.form.get('employment_years')),
    'business_vintage_years': safe_int(request.form.get('business_vintage_years')),
    'education_level': request.form.get('education_level', ''),
    'annual_income': safe_float(request.form.get('annual_income')),
    'monthly_income': safe_float(request.form.get('monthly_income')),
    'dependents': safe_int(request.form.get('dependents')),
    'credit_score': safe_int(request.form.get('credit_score')),
    'cibil_score': safe_int(request.form.get('cibil_score')),
    'requested_loan_amount': safe_float(request.form.get('requested_loan_amount')),
    'loan_tenure_months': safe_int(request.form.get('loan_tenure_months')),
    'interest_rate': safe_float(
        request.form.get('interest_rate'),
        config.DEFAULT_INTEREST_RATES.get(loan_type, 10.0)
    )
    }

            
            # Collect loan-type specific fields
            if loan_type == 'Home':
                form_data.update({
                    'property_value': safe_float(request.form.get('property_value', 0)),
                    'property_location': request.form.get('property_location', ''),
                    'down_payment': safe_float(request.form.get('down_payment', 0)),
                    'property_type': request.form.get('property_type', '')
                })
            elif loan_type == 'Gold':
                form_data.update({
                    'gold_weight': safe_float(request.form.get('gold_weight', 0)),
                    'gold_purity': safe_int(request.form.get('gold_purity', 0)),
                    'gold_market_value': safe_float(request.form.get('gold_market_value', 0))
                })
            elif loan_type == 'Business':
                form_data.update({
                    'business_turnover': safe_float(request.form.get('business_turnover', 0)),
                    'years_in_business': safe_int(request.form.get('years_in_business', 0)),
                    'business_type': request.form.get('business_type', ''),
                    'gst_number': request.form.get('gst_number', '')
                })
            elif loan_type == 'Educational':
                form_data.update({
                    'course_fee': safe_float(request.form.get('course_fee', 0)),
                    'college': request.form.get('college', ''),
                    'course_duration': safe_int(request.form.get('course_duration', 0)),
                    'coapplicant_income': safe_float(request.form.get('coapplicant_income', 0))
                })
            
            # Calculate EMI and EMI-to-income ratio
            emi = calculate_emi(
                form_data['requested_loan_amount'],
                form_data['interest_rate'],
                form_data['loan_tenure_months']
            )
            emi_ratio = calculate_emi_income_ratio(emi, form_data['monthly_income'])
            
            form_data['emi_amount'] = emi
            form_data['emi_income_ratio'] = emi_ratio
            
            # Validate application
            is_valid, error_msg = validate_loan_application(form_data, loan_type)
            if not is_valid:
                flash(f'Validation error: {error_msg}', 'error')
                return redirect(url_for('apply_loan'))
            
            # Generate application ID
            application_id = generate_application_id()
            
            # Prepare data for saving
            application_data = {
                'application_id': application_id,
                'username': username,
                'loan_type': loan_type
            }
            application_data.update(form_data)
            
            # Save to CSV
            success = CSVHandler.save_user_application(application_data)
            
            if success:
                flash(f'Application submitted successfully! Application ID: {application_id}', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Error submitting application. Please try again.', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            print(f"Application error: {e}")
    
    return render_template('apply_loan.html', 
                         loan_types=config.LOAN_TYPES,
                         form_fields=config.FORM_FIELDS,
                         default_rates=config.DEFAULT_INTEREST_RATES)
@app.route('/user/check_status', methods=['GET', 'POST'])
def check_status():
    """Check loan application status"""

    # Allow both user and admin
    if not session.get('user_logged_in') and not session.get('admin_logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('user_login'))

    result = None

    if request.method == 'POST':

        application_id = request.form.get('application_id').strip()

        # Get application data
        app_data = CSVHandler.get_application_by_id(application_id)

        if app_data is None:
            flash('Application ID not found', 'error')

        else:

            # If normal user → check ownership
            if session.get('user_type') == 'user':

                csv_user = str(app_data.get('username') or "").strip().lower()
                session_user = str(session.get('username') or "").strip().lower()

                if csv_user != session_user:
                    flash('This application does not belong to you', 'error')
                    return render_template('check_status.html', result=None)

            # Get prediction data
            pred_data = CSVHandler.get_prediction_by_id(application_id)

            if pred_data is None:
                result = {
                    'status': 'Pending',
                    'message': 'Application is still under review.'
                }

            else:

                import json

                # Load SHAP summary
                shap_summary = pred_data.get('shap_summary')

                # Load SHAP explanation (plots)
                shap_explanation = pred_data.get('shap_explanation')

                # Convert JSON strings back to dictionary
                try:
                    if isinstance(shap_summary, str):
                        shap_summary = json.loads(shap_summary)
                except:
                    shap_summary = None

                try:
                    if isinstance(shap_explanation, str):
                        shap_explanation = json.loads(shap_explanation)
                except:
                    shap_explanation = None

                result = {
    'status': pred_data.get('approval_status'),
    'application_id': application_id,

    'probability_of_default': float(pred_data.get('probability_of_default', 0)),
    'safe_loan_amount': float(pred_data.get('safe_loan_amount', 0)),
    'emi_amount': float(pred_data.get('emi_amount', 0)),
    'emi_income_ratio': float(pred_data.get('emi_income_ratio', 0)),

    'loan_type': app_data.get('loan_type'),
    'requested_amount': float(app_data.get('requested_loan_amount', 0)),
    'username': app_data.get('username'),

    'shap_summary': shap_summary
}

    return render_template('check_status.html', result=result)
@app.route('/user/download_pdf/<application_id>')
def download_pdf(application_id):
    """Download PDF report"""
    if not session.get('user_logged_in'):
        flash('Please login first', 'warning')
        return redirect(url_for('user_login'))
    
    # Get application and prediction data
    app_data = CSVHandler.get_application_by_id(application_id)
    pred_data = CSVHandler.get_prediction_by_id(application_id)
    
    if app_data is None or pred_data is None:
        flash('Data not found', 'error')
        return redirect(url_for('check_status'))
    
    if app_data.get('username') != session.get('username'):
        flash('Unauthorized access', 'error')
        return redirect(url_for('check_status'))
    
    # Generate PDF
    try:
        pdf_generator = LoanApplicationPDF()
        pdf_buffer = pdf_generator.generate_report(app_data, pred_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'loan_report_{application_id}.pdf'
        )
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('check_status'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))
    
    # Load models if not loaded
    if not load_models():
        flash('Models not trained yet. Please run train_models.py first.', 'error')
        return render_template('admin_dashboard.html', applications=[], models_loaded=False)
    
    # Get pending applications
    pending_apps = CSVHandler.get_pending_applications()
    
    return render_template('admin_dashboard.html', 
                         applications=pending_apps.to_dict('records') if not pending_apps.empty else [],
                         models_loaded=True)
@app.route('/admin/check_status', methods=['GET','POST'])
def admin_check_status():

    if not session.get('admin_logged_in'):
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))

    result = None

    if request.method == 'POST':

        application_id = request.form.get('application_id')

        app_data = CSVHandler.get_application_by_id(application_id)

        if app_data is None:
            flash('Application not found', 'error')

        else:
            pred_data = CSVHandler.get_prediction_by_id(application_id)

            if pred_data is None:
                result = {
                    'status': 'Pending',
                    'application_id': application_id
                }
            else:
                result = {
                    'status': pred_data.get('approval_status'),
                    'application_id': application_id,
                    'probability_of_default': pred_data.get('probability_of_default'),
                    'safe_loan_amount': pred_data.get('safe_loan_amount'),
                    'emi_amount': pred_data.get('emi_amount'),
                    'emi_income_ratio': pred_data.get('emi_income_ratio'),
                    'username': app_data.get('username')
                }

    return render_template('admin_check_status.html', result=result)

@app.route('/admin/predict/<application_id>', methods=['GET', 'POST'])
def admin_predict(application_id):
    """Admin prediction page"""

    if not session.get('admin_logged_in'):
        flash('Please login as admin', 'warning')
        return redirect(url_for('admin_login'))

    # Load models
    if not load_models():
        flash('Models not trained yet', 'error')
        return redirect(url_for('admin_dashboard'))

    # Get application data
    app_data = CSVHandler.get_application_by_id(application_id)

    if app_data is None:
        flash('Application not found', 'error')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        try:

            loan_type = app_data['loan_type']
            

            # Prepare form data
            form_data = {}
            for col in config.ALL_FEATURES_ORDERED:
                if col in app_data:
                    form_data[col] = app_data[col]

            # Prepare prediction input
            X_processed = prepare_single_prediction(
                form_data,
                loan_type,
                preprocessor
            )

            # Make prediction
            predictions = make_predictions(
                X_processed,
                loan_type,
                app_data['age'],
                app_data['requested_loan_amount'],
                app_data['loan_tenure_months'],
                app_data['interest_rate'],
                app_data['monthly_income'],
                app_data['emi_amount']
            )

            # Generate SHAP explanations
            shap_explanation, shap_summary = generate_shap_explanations(
                X_processed,
                'approval'
            )

            import json

            # Convert SHAP summary to JSON safely
            shap_summary_json = None

            if shap_summary:
                shap_summary_json = json.dumps({
                    "summary_text": shap_summary.get("summary_text", ""),
                    "top_positive": shap_summary.get("top_positive", []),
                    "top_negative": shap_summary.get("top_negative", [])
                })

            # Prediction data to store in CSV
            prediction_data = {
                'application_id': application_id,
                'approval_status': predictions['approval_status'],
                'probability_of_default': predictions['probability_of_default'],
                'safe_loan_amount': predictions['safe_loan_amount'],
                'emi_amount': predictions['emi_amount'],
                'emi_income_ratio': predictions['emi_income_ratio'],
                'processed_by': session.get('username'),
                'shap_summary': shap_summary_json
            }

            # Save prediction to CSV
            success = CSVHandler.save_admin_prediction(prediction_data)

            if success:
                flash('Prediction completed and sent to user!', 'success')

                return render_template(
                    'prediction_result.html',
                    application=app_data,
                    prediction=predictions,
                    shap_explanation=shap_explanation,
                    shap_summary=shap_summary,
                    application_id=application_id
                )

            else:
                flash('Error saving prediction', 'error')

        except Exception as e:

            flash(f'Prediction error: {str(e)}', 'error')

            print("Prediction Error:", e)

            import traceback
            traceback.print_exc()

    return render_template(
        'admin_predict.html',
        application=app_data,
        application_id=application_id
    )

@app.route('/api/loan_fields/<loan_type>')
def get_loan_fields(loan_type):
    """API endpoint to get loan type specific fields"""
    if loan_type not in config.LOAN_TYPES:
        return jsonify({'error': 'Invalid loan type'}), 400
    
    fields = config.FORM_FIELDS.get(loan_type, {})
    return jsonify({
        'loan_type': loan_type,
        'fields': fields,
        'default_interest_rate': config.DEFAULT_INTEREST_RATES.get(loan_type, 10.0)
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create necessary directories
    for directory in [config.DATA_DIR, config.MODEL_DIR, config.LOG_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # Initialize CSV files
    CSVHandler.initialize_csv_files()
    
    # Run app
    print("="*70)
    print("ENTERPRISE CREDIT RISK ENGINE")
    print("="*70)
    print("\nStarting Flask application...")
    print(f"User Login: http://localhost:5000/user_login")
    print(f"Admin Login: http://localhost:5000/admin_login")
    print("\nDefault Admin Credentials:")
    print(f"  Username: {config.ADMIN_USERNAME}")
    print(f"  Password: {config.ADMIN_PASSWORD}")
    print("\nDefault User Credentials:")
    for user, pwd in config.USER_CREDENTIALS.items():
        print(f"  Username: {user}, Password: {pwd}")
    print("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
