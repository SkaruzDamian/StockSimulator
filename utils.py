import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import importlib

def validate_date_format(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_date_range(start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    return start < end

def validate_tickers(tickers_string):
    if not tickers_string.strip():
        return False, "Ticker list cannot be empty"
    
    tickers = [ticker.strip().upper() for ticker in tickers_string.split(',')]
    for ticker in tickers:
        if not ticker.replace('.', '').replace('-', '').isalnum():
            return False, f"Invalid ticker format: {ticker}"
    
    return True, tickers

def validate_numeric_input(value, min_val=None, max_val=None):
    try:
        num_val = float(value)
        if min_val is not None and num_val < min_val:
            return False
        if max_val is not None and num_val > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False

def format_currency(amount):
    return f"${amount:,.2f}"

def format_percentage(value):
    return f"{value:.2f}%"

def calculate_returns(initial_value, final_value):
    if initial_value == 0:
        return 0
    return ((final_value - initial_value) / initial_value) * 100

def get_model_class(model_name):
    available_models = {
        'Decision Tree': 'DecisionTreeModel',
        'Random Forest': 'RandomForestModel', 
        'SVM': 'SVMModel',
        'KNN': 'KNNModel',
        'Logistic Regression': 'LogisticRegressionModel',
        'Ensemble': 'EnsembleModel'
    }
    
    if model_name not in available_models:
        raise ValueError(f"Model {model_name} not available")
    
    class_name = available_models[model_name]
    
    try:
        if class_name == 'DecisionTreeModel':
            from ml.models.decision_tree_model import DecisionTreeModel
            return DecisionTreeModel
        elif class_name == 'RandomForestModel':
            from ml.models.random_forest_model import RandomForestModel
            return RandomForestModel
        elif class_name == 'SVMModel':
            from ml.models.svm_model import SVMModel
            return SVMModel
        elif class_name == 'KNNModel':
            from ml.models.knn_model import KNNModel
            return KNNModel
        elif class_name == 'LogisticRegressionModel':
            from ml.models.logistic_regression_model import LogisticRegressionModel
            return LogisticRegressionModel
        elif class_name == 'EnsembleModel':
            from ml.models.ensemble_model import EnsembleModel
            return EnsembleModel
        else:
            raise ValueError(f"Unknown model class: {class_name}")
    except ImportError as e:
        raise ImportError(f"Could not import {class_name}: {str(e)}")

def prepare_features_for_prediction(data, drop_columns=None):
    if drop_columns is None:
        drop_columns = ['Target', 'Date']
    
    existing_drop_columns = [col for col in drop_columns if col in data.columns]
    features = data.drop(columns=existing_drop_columns)
    
    features = features.select_dtypes(include=[np.number])
    features = features.fillna(features.mean())
    
    return features

def validate_data_completeness(data, required_features=None):
    if required_features is None:
        required_features = ['Close'] 
    
    missing_columns = [col for col in required_features if col not in data.columns]
    if missing_columns:
        return False, f"Missing required columns: {missing_columns}"
    
    if data.empty:
        return False, "Data is empty"
    
    if data.isnull().all().any():
        return False, "Data contains completely null columns"
    
    return True, "Data is valid"

def safe_divide(numerator, denominator, default_value=0):
    if denominator == 0:
        return default_value
    return numerator / denominator

def normalize_ticker_name(ticker):
    return ticker.strip().upper().replace(' ', '')

def get_trading_days_between(start_date, end_date):
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    business_days = pd.bdate_range(start=start, end=end)
    return len(business_days)

def format_prediction_confidence(prediction_proba):
    if len(prediction_proba.shape) > 1 and prediction_proba.shape[1] > 1:
        confidence = np.max(prediction_proba, axis=1)
        return [f"{conf:.1%}" for conf in confidence]
    return ["N/A"]

def calculate_portfolio_metrics(transactions, current_prices, initial_capital):
    total_value = initial_capital
    total_invested = 0
    
    for ticker, data in transactions.items():
        shares = data.get('shares', 0)
        avg_price = data.get('avg_price', 0)
        current_price = current_prices.get(ticker, avg_price)
        
        position_value = shares * current_price
        invested_value = shares * avg_price
        
        total_value += position_value - invested_value
        total_invested += invested_value
    
    return {
        'total_value': total_value,
        'total_invested': total_invested,
        'total_return': total_value - initial_capital,
        'return_percentage': calculate_returns(initial_capital, total_value)
    }