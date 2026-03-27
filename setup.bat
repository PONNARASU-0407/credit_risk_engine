@echo off
REM Enterprise Credit Risk Engine - Setup Script
REM For Windows

echo ======================================================================
echo ENTERPRISE CREDIT RISK ENGINE - AUTOMATED SETUP
echo ======================================================================
echo.

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Check if dataset exists
echo.
if exist "data\enterprise_credit_risk_dataset_10000.csv" (
    echo [OK] Dataset found
    
    REM Train models
    echo.
    echo Training machine learning models...
    echo This may take a few minutes...
    python train_models.py
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo ======================================================================
        echo [OK] SETUP COMPLETED SUCCESSFULLY!
        echo ======================================================================
        echo.
        echo To start the application:
        echo   1. Activate virtual environment: venv\Scripts\activate.bat
        echo   2. Run the app: python app.py
        echo   3. Open browser: http://localhost:5000
        echo.
        echo Default Credentials:
        echo   Admin  - Username: admin, Password: admin123
        echo   User   - Username: demo, Password: demo123
        echo.
        echo ======================================================================
    ) else (
        echo.
        echo [ERROR] Model training failed. Please check the error messages above.
        pause
        exit /b 1
    )
) else (
    echo [ERROR] Dataset not found at data\enterprise_credit_risk_dataset_10000.csv
    echo Please place the dataset in the data\ directory and run this script again.
    pause
    exit /b 1
)

pause
