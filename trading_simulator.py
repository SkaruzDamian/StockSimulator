import pandas as pd
import numpy as np
from datetime import datetime
from data.data_loader import DataLoader
from data.data_processor import DataProcessor
from portfolio_manager import PortfolioManager
from transaction_logger import TransactionLogger
from utils import get_model_class, prepare_features_for_prediction, validate_data_completeness

class TradingSimulator:
    def __init__(self, tickers, start_date, end_date, model_type, commission, days_ahead, initial_capital, indicators, selected_features):
        self.tickers = tickers
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.model_type = model_type
        self.commission = commission
        self.days_ahead = days_ahead
        self.initial_capital = initial_capital
        self.indicators = indicators
        self.selected_features = selected_features 
        
        self.data_processor = DataProcessor()
        self.portfolio_manager = PortfolioManager(initial_capital, commission)
        self.logger = TransactionLogger()  
        
        self.ticker_data = {}
        self.ticker_models = {}
        self.train_test_data = {}
        self.current_date_index = 0
        self.trading_dates = []
        self.current_predictions = {}
        self.current_prices = {}
        self.previous_prices = {}  
        
        self.is_setup = False
        self.is_trained = False
    
    def setup(self):
        print("Rozpoczynam konfigurację symulatora...")
        
        successful_tickers = []
        
        for ticker in self.tickers:
            print(f"Przetwarzam dane dla {ticker}...")
            
            try:
                data_loader = DataLoader(ticker)
                ticker_data = data_loader.load_data()
                
                is_valid, message = validate_data_completeness(ticker_data)  
                if not is_valid:
                    print(f"Błąd danych dla {ticker}: {message}")
                    continue
                
                ticker_data = self.data_processor.calculate_technical_indicators(ticker_data, self.indicators, self.selected_features)
                ticker_data = self.data_processor.make_target(ticker_data, self.days_ahead)
                
                train_data, test_data, test_start_idx, test_end_idx = self.data_processor.split_data(
                    ticker_data, self.start_date, self.end_date, self.days_ahead
                )
                
                if test_data.empty:
                    print(f"Brak danych testowych dla {ticker}")
                    continue
                
                self.ticker_data[ticker] = ticker_data
                self.train_test_data[ticker] = {
                    'train': train_data,
                    'test': test_data,
                    'test_start_idx': test_start_idx,
                    'test_end_idx': test_end_idx
                }
                
                model_class = get_model_class(self.model_type)
                model = model_class.build_model()
                self.ticker_models[ticker] = model
                
                successful_tickers.append(ticker)
                print(f"Zakończono przetwarzanie {ticker}")
                
            except Exception as e:
                print(f"Błąd podczas przetwarzania {ticker}: {str(e)}")
                continue
        
        if not successful_tickers:
            raise ValueError("Nie udało się załadować danych dla żadnego tickera")
        
        self.tickers = successful_tickers
        self._setup_trading_dates()
        self.is_setup = True
        print("Konfiguracja symulatora zakończona!")
    
    def _setup_trading_dates(self):
        all_dates = set()
        for ticker in self.ticker_data:
            test_data = self.train_test_data[ticker]['test']
            if 'Date' in test_data.columns:
                dates = test_data['Date'].tolist()
            else:
                dates = test_data.index.tolist()
            all_dates.update(dates)
        
        self.trading_dates = sorted(list(all_dates))
        if isinstance(self.trading_dates[0], str):
            self.trading_dates = [pd.to_datetime(date) for date in self.trading_dates]
    
    def train_models(self):
        if not self.is_setup:
            raise ValueError("Symulator nie został skonfigurowany. Uruchom setup() najpierw.")
        
        print("Rozpoczynam trenowanie modeli...")
        
        for ticker, model in self.ticker_models.items():
            print(f"Trenowanie modelu dla {ticker}...")
            
            try:
                train_data = self.train_test_data[ticker]['train']
                
                X_train = prepare_features_for_prediction(train_data, self.selected_features)
                y_train = train_data['Target']
                
                model_class = get_model_class(self.model_type)
                trained_model = model_class.train_model(model, X_train, y_train)
                self.ticker_models[ticker] = trained_model
                
                print(f"Model dla {ticker} został wytrenowany!")
                
            except Exception as e:
                print(f"Błąd podczas trenowania modelu dla {ticker}: {str(e)}")
                del self.ticker_models[ticker]
        
        self.is_trained = True
        print("Trenowanie modeli zakończone!")
    
    def get_current_date(self):
        if self.current_date_index < len(self.trading_dates):
            return self.trading_dates[self.current_date_index]
        return None
    
    def get_predictions_for_current_date(self):
        if not self.is_trained:
            raise ValueError("Modele nie zostały wytrenowane")
        
        current_date = self.get_current_date()
        if current_date is None:
            return {}
        
        print(f"Getting predictions for date: {current_date}")
        
        predictions = {}
        prices = {}
        
        for ticker in self.ticker_models:
            try:
                test_data = self.train_test_data[ticker]['test']
                
                if 'Date' in test_data.columns:
                    current_row = test_data[test_data['Date'] == current_date]
                else:
                    current_row = test_data[test_data.index == current_date]
                
                if not current_row.empty:
                    X_current = prepare_features_for_prediction(current_row, self.selected_features)
                    
                    model_class = get_model_class(self.model_type)
                    prediction = model_class.predict(self.ticker_models[ticker], X_current)
                    
                    predictions[ticker] = prediction[0] if len(prediction) > 0 else 0
                    
                    prices[ticker] = current_row['Close'].iloc[0]  
                    
                    self.logger.log_prediction(current_date, ticker, predictions[ticker])
                    
                    print(f"{ticker}: prediction={predictions[ticker]}, price={prices[ticker]}")
                else:
                    print(f"No data for {ticker} on {current_date}")
                
            except Exception as e:
                print(f"Błąd predykcji dla {ticker}: {str(e)}")
                predictions[ticker] = 0
                prices[ticker] = 0
        
        self.current_predictions = predictions
        self.current_prices = prices
        
        portfolio_summary = self.get_portfolio_summary()
        self.logger.log_daily_portfolio(current_date, portfolio_summary, predictions)
        
        print(f"Final predictions: {predictions}")
        print(f"Final prices: {prices}")
        
        return predictions
    
    def get_current_prices(self):
        return self.current_prices
    
    def get_ticker_data_for_date(self, ticker, date):
        if ticker not in self.ticker_data:
            return None
        
        data = self.ticker_data[ticker]
        if 'Date' in data.columns:
            row = data[data['Date'] == date]
        else:
            row = data[data.index == date]
        
        return row.iloc[0] if not row.empty else None
    
    def buy_stock(self, ticker, shares):
        if ticker not in self.current_prices:
            return False, f"Brak danych cenowych dla {ticker}"
        
        current_date = self.get_current_date()
        ticker_row = self.get_ticker_data_for_date(ticker, current_date)
        
        if ticker_row is None or 'Open' not in ticker_row:
            price = self.current_prices[ticker]
        else:
            price = ticker_row['Open']
        
        total_cost = shares * price
        commission = total_cost * self.commission
        total_with_commission = total_cost + commission
        
        success, message = self.portfolio_manager.buy_stock(ticker, shares, price, current_date)
        
        self.logger.log_transaction(
            current_date, ticker, "BUY", shares, price, 
            commission, total_with_commission, success
        )
        
        return success, message
    
    def sell_stock(self, ticker, shares):
        if ticker not in self.current_prices:
            return False, f"Brak danych cenowych dla {ticker}"
        
        price = self.current_prices[ticker]  
        current_date = self.get_current_date()
        
        total_revenue = shares * price
        commission = total_revenue * self.commission
        net_revenue = total_revenue - commission
        
        success, message = self.portfolio_manager.sell_stock(ticker, shares, price, current_date)
        
        self.logger.log_transaction(
            current_date, ticker, "SELL", shares, price, 
            commission, net_revenue, success
        )
        
        return success, message
    
    def next_day(self):
        current_date = self.get_current_date()
        if current_date:
            self.portfolio_manager.record_daily_value(current_date, self.current_prices)
            
            if self.previous_prices:
                for ticker in self.current_prices:
                    if ticker in self.previous_prices:
                        price_change = self.current_prices[ticker] - self.previous_prices[ticker]
                        if self.current_date_index > 0:
                            prev_date = self.trading_dates[self.current_date_index - 1]
                            self.logger.update_actual_outcome(ticker, prev_date, price_change)
            
            self.previous_prices = self.current_prices.copy()
        
        self.current_date_index += 1
        
        if self.current_date_index < len(self.trading_dates):
            self.get_predictions_for_current_date()
            return True
        else:
            final_portfolio = self.get_portfolio_summary()
            self.logger.finalize_logs(final_portfolio)
        
        return False
    
    def can_go_next_day(self):
        return self.current_date_index < len(self.trading_dates) - 1
    
    def get_portfolio_summary(self):
        return self.portfolio_manager.get_portfolio_summary(self.current_prices)
    
    def get_transaction_history(self):
        return self.portfolio_manager.get_transaction_history()
    
    def get_performance_history(self):
        return self.portfolio_manager.get_performance_history()
    
    def reset_simulation(self):
        self.current_date_index = 0
        self.current_predictions = {}
        self.current_prices = {}
        self.previous_prices = {}
        self.portfolio_manager.reset_portfolio()
        
        self.logger = TransactionLogger()
        
        if self.is_trained:
            self.get_predictions_for_current_date()
    
    def get_simulation_progress(self):
        if not self.trading_dates:
            return 0
        
        return (self.current_date_index / len(self.trading_dates)) * 100
    
    def get_simulation_stats(self):
        return {
            'total_days': len(self.trading_dates),
            'current_day': self.current_date_index + 1,
            'remaining_days': len(self.trading_dates) - self.current_date_index - 1,
            'progress_percentage': self.get_simulation_progress()
        }
    
    def get_ticker_data_until_date(self, ticker, date):
        if ticker not in self.ticker_data:
            return None
        
        data = self.ticker_data[ticker].copy()
        
        if 'Date' in data.columns:
            data = data[data['Date'] <= pd.to_datetime(date)]
        else:
            data = data[data.index <= pd.to_datetime(date)]
        
        return data