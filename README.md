# 🏦 Enterprise Credit Risk Engine

A full-stack, production-ready credit risk assessment system powered by LightGBM machine learning models with SHAP explainability.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Training Models](#training-models)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## ✨ Features

### Core Functionality
- **Two-tier Authentication System**
  - User login for loan applications
  - Admin login for application processing
  
- **Multiple Loan Types**
  - Home Loan
  - Educational Loan  
  - Gold Loan
  - Business Loan

- **AI-Powered Predictions**
  - Loan Approval Classification (LightGBM)
  - Probability of Default Estimation
  - Safe Loan Amount Regression

- **Explainable AI (XAI)**
  - SHAP value analysis
  - Feature importance visualization
  - Interactive force plots

- **Professional Features**
  - Dynamic form fields based on loan type
  - EMI calculation and affordability assessment
  - PDF report generation
  - Application tracking system
  - CSV-based data storage

## 🔧 Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **LightGBM** - Gradient boosting models
- **SHAP** - Model explainability
- **Pandas** - Data manipulation
- **Scikit-learn** - Preprocessing
- **Joblib** - Model serialization

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern, responsive styling
- **JavaScript** - Interactivity
- **Vanilla JS** - No frameworks required

### Data Storage
- **CSV Files** - No database required
- **Pickle Files** - Model persistence

## 📁 Project Structure

```
credit_risk_engine/
│
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── train_models.py                 # Model training script
├── requirements.txt                # Python dependencies
│
├── data/                           # Data storage
│   ├── enterprise_credit_risk_dataset_10000.csv
│   ├── user_applications.csv       # User submissions
│   └── admin_predictions.csv       # Prediction results
│
├── models/                         # Trained models
│   ├── approval_model.pkl
│   ├── default_probability_model.pkl
│   ├── safe_amount_model.pkl
│   ├── label_encoders.pkl
│   └── feature_columns.pkl
│
├── utils/                          # Utility modules
│   ├── calculations.py             # EMI and other calculations
│   ├── preprocessing.py            # Feature alignment & preprocessing
│   ├── explainability.py           # SHAP explanations
│   ├── pdf_generator.py            # PDF report generation
│   └── csv_handler.py              # CSV operations
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Homepage
│   ├── user_login.html
│   ├── admin_login.html
│   ├── user_dashboard.html
│   ├── apply_loan.html             # Dynamic loan application form
│   ├── check_status.html
│   ├── admin_dashboard.html
│   ├── admin_predict.html
│   ├── prediction_result.html      # Results with SHAP
│   ├── 404.html
│   └── 500.html
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Comprehensive styling
│   └── js/
│       └── script.js               # Client-side scripts
│
└── logs/                           # Application logs
```

## 🚀 Installation

### Step 1: Prerequisites

Ensure you have Python 3.8 or higher installed:

```bash
python --version
```

### Step 2: Clone/Create Project

Create the project directory and navigate to it:

```bash
cd credit_risk_engine
```

### Step 3: Create Virtual Environment

#### On Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Verify Installation

```bash
python -c "import flask, pandas, lightgbm, shap; print('All packages installed successfully!')"
```

## ⚙️ Configuration

### Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

**User Logins:**
- Username: `demo` | Password: `demo123`
- Username: `user1` | Password: `pass123`
- Username: `user2` | Password: `pass456`

### Customization

Edit `config.py` to customize:
- Admin credentials
- User credentials
- Interest rates by loan type
- Feature columns
- File paths

## 🎓 Training Models

### Critical: Feature Alignment

This system uses **strict feature alignment** to prevent feature mismatch errors during prediction. The training script:

1. Loads data with all features
2. Creates a consistent feature order
3. Saves the feature order for inference
4. Ensures categorical encoding consistency

### Run Training

```bash
python train_models.py
```

**Expected Output:**
```
==================================================================
ENTERPRISE CREDIT RISK ENGINE - MODEL TRAINING
==================================================================

Loading dataset...
Dataset shape: (10000, 37)

Training Approval Classification Model...
Accuracy: 0.8542
AUC-ROC: 0.9213

Training Probability of Default Model...
RMSE: 0.1234

Training Safe Loan Amount Model...
RMSE: 1523421.32

Saving models...
Model training complete!
==================================================================
```

**What Gets Created:**
- `models/approval_model.pkl` - Classification model
- `models/default_probability_model.pkl` - Regression model
- `models/safe_amount_model.pkl` - Regression model
- `models/label_encoders.pkl` - Categorical encoders
- `models/feature_columns.pkl` - Feature order for alignment

## 🏃 Running the Application

### Start the Flask Server

```bash
python app.py
```

**Expected Output:**
```
==================================================================
ENTERPRISE CREDIT RISK ENGINE
==================================================================

Starting Flask application...
User Login: http://localhost:5000/user_login
Admin Login: http://localhost:5000/admin_login

Default Admin Credentials:
  Username: admin
  Password: admin123

Default User Credentials:
  Username: demo, Password: demo123
==================================================================

 * Running on http://0.0.0.0:5000
```

### Access the Application

Open your browser and navigate to:
- **Homepage:** http://localhost:5000
- **User Login:** http://localhost:5000/user_login
- **Admin Login:** http://localhost:5000/admin_login

## 📖 Usage Guide

### User Workflow

1. **Login**
   - Navigate to User Login
   - Enter credentials (e.g., demo/demo123)

2. **Apply for Loan**
   - Click "Apply for Loan"
   - Select loan type (triggers dynamic form fields)
   - Fill in all required fields:
     - Common fields (age, income, credit scores, etc.)
     - Loan-type specific fields (auto-populated based on selection)
   - Interest rate auto-fills based on loan type
   - EMI is calculated automatically
   - Submit application
   - Receive unique Application ID

3. **Check Status**
   - Click "Check Status"
   - Enter Application ID
   - View results once processed by admin

4. **Download PDF**
   - After approval/rejection, download comprehensive PDF report
   - Includes SHAP explanations

### Admin Workflow

1. **Login**
   - Navigate to Admin Login
   - Enter admin credentials

2. **View Dashboard**
   - See all pending applications
   - View applicant details at a glance

3. **Process Application**
   - Click "Predict" on any application
   - Review application details
   - Click "Run ML Predictions"
   - System runs all 3 models:
     * Approval Classification
     * Default Probability
     * Safe Loan Amount

4. **Review Results**
   - View comprehensive prediction results
   - SHAP explanations show feature impacts
   - Visualizations include:
     * Waterfall plot
     * Feature importance plot
     * Force plot (interactive)
   - Results automatically saved to user

## 🔍 Key Features Explained

### Dynamic Form Fields

The loan application form dynamically shows/hides fields based on loan type:

**Home Loan:**
- Property value
- Property location
- Down payment
- Property type

**Gold Loan:**
- Gold weight
- Gold purity
- Gold market value

**Business Loan:**
- Business turnover
- Years in business
- Business type
- GST number

**Educational Loan:**
- Course fee
- College tier
- Course duration
- Co-applicant income

### Feature Alignment System

**Problem Solved:** Prevents feature name/order mismatch between training and prediction.

**Solution:**
1. `ALL_FEATURES_ORDERED` defines exact feature order
2. `FeatureAligner` class ensures consistency
3. `prepare_single_prediction()` handles loan-type specific features
4. Missing loan-type features are filled with 0 (not relevant to that loan type)

**Example:**
```python
# Home loan applicant doesn't have gold fields
# System automatically handles this:
features = {
    'age': 30,
    'loan_type': 'Home',
    'property_value': 5000000,
    'gold_weight': 0,  # Auto-filled
    'gold_purity': 0,  # Auto-filled
    # ... etc
}
```

### EMI Calculation

Uses standard loan EMI formula:
```
EMI = P × r × (1+r)^n / ((1+r)^n - 1)

Where:
P = Principal loan amount
r = Monthly interest rate (annual rate / 12)
n = Loan tenure in months
```

**Important:** 
- For approved loans: EMI based on requested amount
- For rejected loans: EMI based on safe loan amount

### SHAP Explainability

SHAP (SHapley Additive exPlanations) provides:

1. **Feature Impact:** Shows which features pushed toward approval/rejection
2. **Magnitude:** How strong each feature's impact was
3. **Direction:** Positive (approval) or negative (rejection)

**Visualizations:**
- **Waterfall Plot:** Top 10 features with their contributions
- **Feature Importance:** Absolute impact ranking
- **Force Plot:** Interactive visualization of prediction

### PDF Reports

Generated reports include:
- Application details
- Prediction results
- SHAP explanations
- Visual plots
- Recommendations

## 🌐 Deployment

### Local Deployment

Already covered in "Running the Application" section.

### Production Deployment

#### Using Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

#### Using Waitress (Windows)

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

### Environment Variables

For production, set these environment variables:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
```

### Security Considerations

1. **Change default credentials** in `config.py`
2. **Use environment variables** for sensitive data
3. **Enable HTTPS** in production
4. **Add rate limiting** for API endpoints
5. **Implement proper session management**
6. **Add CSRF protection**

## 🐛 Troubleshooting

### Models Not Found Error

**Problem:** "Models not trained yet" message

**Solution:**
```bash
python train_models.py
```

### Feature Mismatch Error

**Problem:** Feature names don't match between training and prediction

**Solution:** This shouldn't happen with the implemented feature alignment system. If it does:
1. Delete all files in `models/` folder
2. Re-run `python train_models.py`
3. Restart the Flask app

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### SHAP Visualization Not Showing

**Problem:** SHAP plots don't render

**Solution:**
- Check matplotlib backend (already set to 'Agg')
- Verify SHAP package version: `pip install shap==0.44.0`

### CSV File Permission Error

**Problem:** Can't write to CSV files

**Solution:**
- Check file permissions
- Ensure `data/` directory is writable
- On Linux: `chmod 755 data/`

### Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python app.py --port 5001
```

## 📊 Model Performance

Based on the training dataset:

**Approval Classification:**
- Accuracy: ~85-90%
- AUC-ROC: ~90-95%

**Probability of Default:**
- RMSE: ~0.10-0.15

**Safe Loan Amount:**
- RMSE: ~1,000,000 - 2,000,000 (depends on loan amounts in data)

## 🤝 Support

For issues or questions:
1. Check this README
2. Review code comments
3. Check `logs/` directory for error logs

## 📝 License

This project is for educational and demonstration purposes.

## 🎯 Future Enhancements

- Database integration (PostgreSQL/MySQL)
- User registration system
- Email notifications
- Advanced analytics dashboard
- Multi-factor authentication
- API endpoints for integration
- Docker containerization
- Automated model retraining

---

**Built with ❤️ using Python, Flask, LightGBM, and SHAP**
"# credit_risk_engine" 
