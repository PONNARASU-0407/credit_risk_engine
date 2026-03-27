"""
Utility functions for calculations
"""
import numpy as np
import pandas as pd

def calculate_emi(principal, annual_interest_rate, tenure_months):
    """
    Calculate EMI using the standard formula:
    EMI = P × r × (1+r)^n / ((1+r)^n - 1)
    
    Args:
        principal: Loan amount
        annual_interest_rate: Annual interest rate in percentage
        tenure_months: Loan tenure in months
    
    Returns:
        EMI amount (float)
    """
    if principal <= 0 or tenure_months <= 0:
        return 0
    
    # Convert annual rate to monthly rate
    monthly_rate = (annual_interest_rate / 100) / 12
    
    if monthly_rate == 0:
        # If interest rate is 0, EMI is simply principal divided by tenure
        return principal / tenure_months
    
    # EMI formula
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1
    
    emi = numerator / denominator
    
    return round(emi, 2)


def calculate_emi_income_ratio(emi, monthly_income):
    """
    Calculate EMI to Income ratio
    
    Args:
        emi: EMI amount
        monthly_income: Monthly income
    
    Returns:
        EMI to income ratio (float)
    """
    if monthly_income <= 0:
        return 0
    
    ratio = emi / monthly_income
    return round(ratio, 4)


def generate_application_id():
    """
    Generate unique application ID
    
    Returns:
        Application ID string
    """
    import uuid
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"APP{timestamp}{unique_id}"


def validate_loan_application(data, loan_type):
    """
    Validate loan application data
    
    Args:
        data: Dictionary of application data
        loan_type: Type of loan
    
    Returns:
        Tuple (is_valid, error_message)
    """
    errors = []
    
    # Validate common fields
    if data.get('age', 0) < 18:
        errors.append("Age must be at least 18")
    
    # Monthly income validation
    # Educational loan can have 0 income
    if loan_type != 'Educational':
        if data.get('monthly_income', 0) <= 0:
            errors.append("Monthly income must be positive")
    else:
        # For educational loan, income cannot be negative
        if data.get('monthly_income', 0) < 0:
            errors.append("Monthly income cannot be negative")
    
    if data.get('requested_loan_amount', 0) <= 0:
        errors.append("Loan amount must be positive")
    
    if data.get('loan_tenure_months', 0) <= 0:
        errors.append("Loan tenure must be positive")
    
    # Validate loan-type specific fields
    if loan_type == 'Home':
        if data.get('property_value', 0) <= 0:
            errors.append("Property value must be positive")
        if data.get('down_payment', 0) < 0:
            errors.append("Down payment cannot be negative")
    
    elif loan_type == 'Gold':
        if data.get('gold_weight', 0) <= 0:
            errors.append("Gold weight must be positive")
        if data.get('gold_purity', 0) < 10 or data.get('gold_purity', 0) > 24:
            errors.append("Gold purity must be between 10 and 24 karats")
    
    elif loan_type == 'Business':
        if data.get('business_turnover', 0) <= 0:
            errors.append("Business turnover must be positive")
        if data.get('years_in_business', 0) < 0:
            errors.append("Years in business cannot be negative")
    
    elif loan_type == 'Educational':
        if data.get('course_fee', 0) <= 0:
            errors.append("Course fee must be positive")
        if data.get('coapplicant_income', 0) < 0:
            errors.append("Co-applicant income cannot be negative")
    
    if errors:
        return False, "; ".join(errors)
    
    return True, ""

