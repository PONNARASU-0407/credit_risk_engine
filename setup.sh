#!/bin/bash

# Enterprise Credit Risk Engine - Setup Script
# For Linux and macOS

echo "======================================================================"
echo "ENTERPRISE CREDIT RISK ENGINE - AUTOMATED SETUP"
echo "======================================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if dataset exists
echo ""
if [ -f "data/enterprise_credit_risk_dataset_10000.csv" ]; then
    echo "✓ Dataset found"
    
    # Train models
    echo ""
    echo "Training machine learning models..."
    echo "This may take a few minutes..."
    python train_models.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "======================================================================"
        echo "✓ SETUP COMPLETED SUCCESSFULLY!"
        echo "======================================================================"
        echo ""
        echo "To start the application:"
        echo "  1. Activate virtual environment: source venv/bin/activate"
        echo "  2. Run the app: python app.py"
        echo "  3. Open browser: http://localhost:5000"
        echo ""
        echo "Default Credentials:"
        echo "  Admin  - Username: admin, Password: admin123"
        echo "  User   - Username: demo, Password: demo123"
        echo ""
        echo "======================================================================"
    else
        echo ""
        echo "✗ Model training failed. Please check the error messages above."
        exit 1
    fi
else
    echo "✗ Dataset not found at data/enterprise_credit_risk_dataset_10000.csv"
    echo "Please place the dataset in the data/ directory and run this script again."
    exit 1
fi
