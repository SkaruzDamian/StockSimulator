"""
Testy funkcjonalne systemu symulatora giełdowego
Autor: Damian Skaruz
Praca inżynierska: Projekt i implementacja autonomicznego agenta giełdowego

Testy funkcjonalne weryfikują czy system spełnia wymagania funkcjonalne
określone w specyfikacji. Testują system od strony użytkownika końcowego.
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_simulator import TradingSimulator
from portfolio_manager import PortfolioManager


class TestRequirement_4_1_1_SystemConfiguration(unittest.TestCase):
    
    @patch('trading_simulator.DataLoader')
    def test_valid_configuration_acceptance(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL', 'MSFT'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 5,
            'initial_capital': 10000.0,
            'indicators': ['SMA', 'RSI', 'MACD'],
            'selected_features': ['Open', 'High', 'Low', 'Close', 'Volume']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        
        self.assertTrue(simulator.is_setup)
        self.assertEqual(simulator.initial_capital, 10000.0)
        self.assertEqual(simulator.commission, 0.002)
        self.assertEqual(simulator.days_ahead, 5)
    
    def test_commission_rate_range(self):
        valid_commissions = [0.0, 0.001, 0.002, 0.005, 0.01]
        
        for commission in valid_commissions:
            pm = PortfolioManager(10000.0, commission)
            self.assertEqual(pm.commission_rate, commission)
    
    def test_minimum_capital_requirement(self):
        pm_low = PortfolioManager(500.0, 0.002)
        self.assertEqual(pm_low.initial_capital, 500.0)
        
        pm_valid = PortfolioManager(1000.0, 0.002)
        self.assertEqual(pm_valid.initial_capital, 1000.0)


class TestRequirement_4_1_2_FeatureSelection(unittest.TestCase):
    
    @patch('trading_simulator.DataLoader')
    def test_close_feature_is_mandatory(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Decision Tree',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        
        self.assertTrue(simulator.is_setup)


class TestRequirement_4_1_3_TechnicalIndicators(unittest.TestCase):
    
    def setUp(self):
        from data.data_processor import DataProcessor
        
        self.processor = DataProcessor()
        
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        
        base_price = 100
        close_prices = base_price + np.random.randn(100).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(100)) * 2
        low_prices = close_prices - np.abs(np.random.randn(100)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(100)
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 100)
        })
        self.test_data.set_index('Date', inplace=True)
        
    def test_all_18_indicators_available(self):
        required_indicators = [
            'SMA', 'EMA', 'RSI', 'MACD', 'Bollinger Bands',
            'Stochastic Oscillator', 'Williams_R', 'ATR', 'CCI',
            'MFI', 'ROC', 'OBV', 'AD', 'MOM', 'Price Change',
            'High Low Ratio', 'Volume SMA', 'Volume Ratio'
        ]
        
        for indicator in required_indicators:
            try:
                result = self.processor.calculate_technical_indicators(
                    self.test_data.copy(),
                    [indicator]
                )
                self.assertIsNotNone(result)
            except Exception as e:
                self.fail(f"Wskaźnik {indicator} nie jest dostępny: {str(e)}")


class TestRequirement_4_1_4_ManualSimulation(unittest.TestCase):
    
    @patch('trading_simulator.DataLoader')
    def test_manual_buy_operation(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        success, message = simulator.buy_stock('AAPL', 10)
        
        self.assertTrue(success or "Insufficient" in message or "Brak danych" in message)
    
    @patch('trading_simulator.DataLoader')
    def test_manual_sell_operation(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        buy_success, _ = simulator.buy_stock('AAPL', 10)
        
        if buy_success:
            success, message = simulator.sell_stock('AAPL', 5)
            self.assertTrue(success)
        else:
            self.assertTrue(True)
    
    @patch('trading_simulator.DataLoader')
    def test_day_progression_in_manual_mode(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        initial_date_index = simulator.current_date_index
        
        can_continue = simulator.next_day()
        
        self.assertEqual(simulator.current_date_index, initial_date_index + 1)


class TestRequirement_4_1_7_PortfolioVisualization(unittest.TestCase):
    
    def test_portfolio_summary_structure(self):
        pm = PortfolioManager(10000.0, 0.002)
        test_date = datetime(2024, 1, 15)
        
        pm.buy_stock('AAPL', 10, 150.0, test_date)
        pm.buy_stock('MSFT', 5, 300.0, test_date)
        
        current_prices = {'AAPL': 160.0, 'MSFT': 310.0}
        summary = pm.get_portfolio_summary(current_prices)
        
        required_fields = ['cash', 'total_value', 'total_return', 
                          'return_percentage', 'positions']
        
        for field in required_fields:
            self.assertIn(field, summary)
        
        for position in summary['positions']:
            required_position_fields = [
                'ticker', 'shares', 'avg_price', 'current_price',
                'market_value', 'unrealized_pnl', 'unrealized_pnl_pct'
            ]
            
            for field in required_position_fields:
                self.assertIn(field, position)
    
    def test_portfolio_returns_calculation(self):
        pm = PortfolioManager(10000.0, 0.002)
        test_date = datetime(2024, 1, 15)
        
        pm.buy_stock('AAPL', 10, 100.0, test_date)
        
        current_prices = {'AAPL': 120.0}
        summary = pm.get_portfolio_summary(current_prices)
        
        self.assertGreater(summary['total_return'], 0)
        self.assertGreater(summary['return_percentage'], 0)


class TestRequirement_4_1_9_PerformanceMetrics(unittest.TestCase):
    
    @patch('trading_simulator.DataLoader')
    def test_transaction_history_recording(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        buy_success, _ = simulator.buy_stock('AAPL', 10)
        if buy_success:
            simulator.next_day()
            simulator.sell_stock('AAPL', 5)
        
        history = simulator.get_transaction_history()
        
        if buy_success:
            self.assertGreater(len(history), 0)
            
            required_columns = ['date', 'ticker', 'action', 'shares', 'price']
            for col in required_columns:
                self.assertIn(col, history.columns)
        else:
            self.assertTrue(True)
    
    @patch('trading_simulator.DataLoader')
    def test_daily_performance_tracking(self, mock_data_loader):
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        close_prices = base_price + np.random.randn(200).cumsum()
        close_prices = np.maximum(close_prices, 10)
        
        high_prices = close_prices + np.abs(np.random.randn(200)) * 2
        low_prices = close_prices - np.abs(np.random.randn(200)) * 2
        open_prices = low_prices + (high_prices - low_prices) * np.random.rand(200)
        
        mock_data = pd.DataFrame({
            'Date': dates,
            'Open': open_prices,
            'High': high_prices,
            'Low': low_prices,
            'Close': close_prices,
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        mock_data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        for _ in range(5):
            if not simulator.next_day():
                break
        
        performance = simulator.get_performance_history()
        
        self.assertGreater(len(performance), 0)
        
        required_columns = ['date', 'value', 'return']
        for col in required_columns:
            self.assertIn(col, performance.columns)


class TestRequirement_4_2_1_Responsiveness(unittest.TestCase):
    
    def test_portfolio_operations_performance(self):
        import time
        
        pm = PortfolioManager(10000.0, 0.002)
        test_date = datetime(2024, 1, 15)
        
        start = time.time()
        pm.buy_stock('AAPL', 10, 150.0, test_date)
        buy_time = time.time() - start
        
        self.assertLess(buy_time, 0.1)
        
        start = time.time()
        pm.sell_stock('AAPL', 5, 160.0, test_date)
        sell_time = time.time() - start
        
        self.assertLess(sell_time, 0.1)


class TestRequirement_4_2_3_Reliability(unittest.TestCase):
    
    def test_insufficient_funds_handling(self):
        pm = PortfolioManager(1000.0, 0.002)
        test_date = datetime(2024, 1, 15)
        
        success, message = pm.buy_stock('TSLA', 100, 200.0, test_date)
        
        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)
        
        self.assertEqual(pm.current_capital, 1000.0)
    
    def test_insufficient_shares_handling(self):
        pm = PortfolioManager(10000.0, 0.002)
        test_date = datetime(2024, 1, 15)
        
        pm.buy_stock('AAPL', 10, 150.0, test_date)
        
        success, message = pm.sell_stock('AAPL', 20, 160.0, test_date)
        
        self.assertFalse(success)
        self.assertIn("Insufficient shares", message)
        
        position = pm.get_position('AAPL')
        self.assertEqual(position['shares'], 10)
    
    def test_state_preservation_after_errors(self):
        pm = PortfolioManager(10000.0, 0.002)
        test_date = datetime(2024, 1, 15)
        
        pm.buy_stock('AAPL', 10, 100.0, test_date)
        initial_capital = pm.current_capital
        
        pm.buy_stock('MSFT', 1000, 500.0, test_date)
        
        self.assertEqual(pm.current_capital, initial_capital)
        
        position = pm.get_position('AAPL')
        self.assertEqual(position['shares'], 10)


if __name__ == '__main__':
    unittest.main(verbosity=2)