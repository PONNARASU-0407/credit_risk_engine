# 🚀 Quick Start Guide

Get the Enterprise Credit Risk Engine up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- 2GB free disk space
- Internet connection (for downloading packages)

## Setup Methods

### Method 1: Automated Setup (Recommended)

#### On Linux/Mac:

```bash
chmod +x setup.sh
./setup.sh
```

#### On Windows:

```batch
setup.bat
```

The script will:
1. Create virtual environment
2. Install all dependencies
3. Train ML models
4. Display startup instructions

---

### Method 2: Manual Setup

#### Step 1: Create Virtual Environment

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```batch
python -m venv venv
venv\Scripts\activate
```

#### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 3: Train Models

```bash
python train_models.py
```

Wait for training to complete (~2-5 minutes).

#### Step 4: Start Application

```bash
python app.py
```

---

## Accessing the Application

Once the server starts, open your browser and navigate to:

**Homepage:** http://localhost:5000

## Login Credentials

### Admin Access
- **URL:** http://localhost:5000/admin_login
- **Username:** `admin`
- **Password:** `admin123`

### User Access
- **URL:** http://localhost:5000/user_login
- **Username:** `demo`
- **Password:** `demo123`

## Quick Test Workflow

### As a User:

1. **Login** with demo/demo123
2. **Click "Apply for Loan"**
3. **Select "Home Loan"** (easiest to test)
4. **Fill the form:**
   - Age: 30
   - Gender: Male
   - City Type: Urban
   - Employment Type: Salaried
   - Employment Years: 5
   - Business Vintage: 0
   - Education: Graduate
   - Annual Income: 1000000
   - Monthly Income: 83333 (auto-calculated)
   - Dependents: 2
   - Credit Score: 750
   - CIBIL Score: 750
   - Requested Amount: 5000000
   - Tenure: 240 months
   - Interest Rate: 8.5% (auto-filled)
   - **Home Loan Specifics:**
     - Property Value: 8000000
     - Location: Urban
     - Down Payment: 2000000
     - Type: Apartment
5. **Submit** and note the Application ID
6. **Logout**

### As an Admin:

1. **Login** with admin/admin123
2. **See the pending application** on dashboard
3. **Click "Predict"** button
4. **Review application details**
5. **Click "Run ML Predictions"**
6. **View comprehensive results** with SHAP explanations
7. **Note:** Results are automatically saved
8. **Logout**

### Check Results as User:

1. **Login** again as demo/demo123
2. **Click "Check Status"**
3. **Enter your Application ID**
4. **View detailed results**
5. **Download PDF report**

## Common Issues & Solutions

### "Models not found" Error

**Solution:** Run `python train_models.py`

### "Port already in use" Error

**Solution:** 
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5000   # Windows (find PID and kill it)
```

### Import Errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Virtual Environment Not Activating

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```batch
venv\Scripts\activate.bat
```

## Stopping the Application

Press `Ctrl + C` in the terminal where the app is running.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore different loan types
- Review SHAP explanations
- Try with different credit scores and amounts
- Customize the application in `config.py`

## Support Files Overview

```
credit_risk_engine/
├── app.py              ← Main application
├── train_models.py     ← Train ML models
├── config.py           ← Configuration
├── requirements.txt    ← Dependencies
├── data/               ← Data storage
├── models/             ← Trained models
├── templates/          ← HTML pages
├── static/             ← CSS & JS
└── utils/              ← Helper functions
```

## Default Folder Structure Check

Ensure these folders exist:
- ✓ `data/`
- ✓ `models/`
- ✓ `templates/`
- ✓ `static/css/`
- ✓ `static/js/`
- ✓ `utils/`
- ✓ `logs/`

They should be created automatically, but if missing, create them manually.

## Performance Expectations

### Training Time:
- ~2-5 minutes (depending on system)

### Prediction Time:
- < 1 second per application

### Memory Usage:
- ~500MB-1GB during operation

---

**You're all set! 🎉**

For detailed information, see [README.md](README.md)
