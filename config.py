AVAILABLE_MODELS = {
    'Decision Tree': 'DecisionTreeModel',
    'Random Forest': 'RandomForestModel', 
    'SVM': 'SVMModel',
    'KNN': 'KNNModel',
    'Logistic Regression': 'LogisticRegressionModel',
    'Ensemble': 'EnsembleModel'
}

AVAILABLE_INDICATORS = [
    'SMA',
    'EMA', 
    'RSI',
    'MACD',
    'Bollinger Bands',
    'Stochastic Oscillator',
    'Williams_R',
    'ATR',
    'CCI',
    'MFI',
    'ROC',
    'OBV',
    'AD',
    'MOM',
    'Price Change',
    'High Low Ratio',
    'Volume SMA',
    'Volume Ratio'
]

AVAILABLE_PRICE_FEATURES = [
    'Open',
    'High', 
    'Low',
    'Close',
    'Volume'
]

DEFAULT_SETTINGS = {
    'initial_capital': 10000.0,
    'commission': 0.002,
    'days_ahead': 1,
    'start_date': '2020-01-01',
    'end_date': '2023-12-31'
}

CHART_COLORS = {
    'price': '#1f77b4',
    'sma': '#ff7f0e', 
    'ema': '#2ca02c',
    'bollinger_upper': '#d62728',
    'bollinger_middle': '#9467bd',
    'bollinger_lower': '#d62728',
    'volume': '#8c564b',
    'rsi': '#e377c2',
    'macd': '#7f7f7f',
    'macd_signal': '#bcbd22',
    'background': '#f0f0f0'
}

WINDOW_SETTINGS = {
    'main_window_size': (800, 600),
    'simulation_window_size': (1200, 800),
    'chart_figure_size': (12, 8)
}

DATA_COLUMNS_TO_DROP = ['Date', 'Target']

AGENT_STRATEGIES_INFO = {
    'Basic Strategy': {
        'description': 'Kupuj przy prediction=1, sprzedawaj po określonym czasie',
        'risk_level': 'Średnie',
        'capital_allocation': 'Równy podział między spółki'
    },
    'Aggressive Strategy': {
        'description': 'Większe pozycje, stop-loss przy stracie >5%',
        'risk_level': 'Wysokie', 
        'capital_allocation': '80% kapitału, większe pozycje'
    },
    'Conservative Strategy': {
        'description': 'Mniejsze pozycje, take-profit >10%, stop-loss >3%',
        'risk_level': 'Niskie',
        'capital_allocation': '50% kapitału, bezpieczniejsze pozycje'
    }
}