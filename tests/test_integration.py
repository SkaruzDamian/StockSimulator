"""
Testy integracyjne dla systemu symulatora giełdowego
Autor: Damian Skaruz
Praca inżynierska: Projekt i implementacja autonomicznego agenta giełdowego
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from trading_simulator import TradingSimulator
from portfolio_manager import PortfolioManager
from data.data_processor import DataProcessor


class TestTradingSimulatorIntegration(unittest.TestCase):
    """Testy integracyjne symulatora tradingowego"""
    
    @classmethod
    def setUpClass(cls):
        """Przygotowanie wspólnych zasobów dla wszystkich testów"""
        cls.test_config = {
            'tickers': ['AAPL'],
            'start_date': '2023-06-01',
            'end_date': '2023-08-31',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA', 'RSI'],
            'selected_features': ['Open', 'High', 'Low', 'Close', 'Volume']
        }
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        # Utworzenie mock'a dla DataLoader
        self.mock_data = self._create_mock_market_data()
    
    def _create_mock_market_data(self):
        """Tworzenie syntetycznych danych rynkowych do testów"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        np.random.seed(42)
        base_price = 150.0
        price_changes = np.random.randn(len(dates)).cumsum() * 2
        
        data = pd.DataFrame({
            'Date': dates,
            'Open': base_price + price_changes + np.random.randn(len(dates)) * 0.5,
            'High': base_price + price_changes + np.random.randn(len(dates)) * 0.5 + 1,
            'Low': base_price + price_changes + np.random.randn(len(dates)) * 0.5 - 1,
            'Close': base_price + price_changes,
            'Volume': np.random.randint(50000000, 100000000, len(dates))
        })
        
        data.set_index('Date', inplace=True)
        return data
    
    @patch('trading_simulator.DataLoader')
    def test_simulator_complete_workflow(self, mock_data_loader):
        """Test kompletnego przepływu pracy symulatora"""
        # Konfiguracja mock'a
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        # Utworzenie symulatora
        simulator = TradingSimulator(**self.test_config)
        
        # Test setup
        simulator.setup()
        self.assertTrue(simulator.is_setup)
        self.assertGreater(len(simulator.ticker_data), 0)
        
        # Test trenowania modeli
        simulator.train_models()
        self.assertTrue(simulator.is_trained)
        self.assertGreater(len(simulator.ticker_models), 0)
        
        # Test generowania predykcji
        predictions = simulator.get_predictions_for_current_date()
        self.assertIsInstance(predictions, dict)
        self.assertIn('AAPL', predictions)
    
    @patch('trading_simulator.DataLoader')
    def test_simulator_manual_trading_flow(self, mock_data_loader):
        """Test przepływu manualnego tradingu"""
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        simulator = TradingSimulator(**self.test_config)
        simulator.setup()
        simulator.train_models()
        
        # Pobranie predykcji
        predictions = simulator.get_predictions_for_current_date()
        prices = simulator.get_current_prices()
        
        # Symulacja zakupu
        if predictions.get('AAPL') == 1:
            success, message = simulator.buy_stock('AAPL', 10)
            self.assertTrue(success or "Insufficient funds" in message)
        
        # Przejście do następnego dnia
        can_continue = simulator.next_day()
        
        if can_continue:
            # Symulacja sprzedaży
            success, message = simulator.sell_stock('AAPL', 5)
            # Może się nie powieść jeśli nie mamy akcji
            self.assertIsInstance(success, bool)
    
    @patch('trading_simulator.DataLoader')
    def test_simulator_portfolio_value_tracking(self, mock_data_loader):
        """Test śledzenia wartości portfela w czasie"""
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        simulator = TradingSimulator(**self.test_config)
        simulator.setup()
        simulator.train_models()
        
        initial_capital = simulator.initial_capital
        
        # Wykonanie kilku transakcji
        for _ in range(5):
            predictions = simulator.get_predictions_for_current_date()
            
            if predictions.get('AAPL') == 1:
                simulator.buy_stock('AAPL', 5)
            
            if not simulator.next_day():
                break
        
        # Sprawdzenie historii wydajności
        performance = simulator.get_performance_history()
        
        self.assertIsInstance(performance, pd.DataFrame)
        if len(performance) > 0:
            self.assertIn('date', performance.columns)
            self.assertIn('value', performance.columns)
            self.assertIn('return', performance.columns)
    
    @patch('trading_simulator.DataLoader')
    def test_simulator_transaction_logging(self, mock_data_loader):
        """Test logowania transakcji"""
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        simulator = TradingSimulator(**self.test_config)
        simulator.setup()
        simulator.train_models()
        
        # Wykonanie transakcji
        simulator.buy_stock('AAPL', 10)
        simulator.next_day()
        simulator.sell_stock('AAPL', 5)
        
        # Sprawdzenie historii transakcji
        history = simulator.get_transaction_history()
        
        self.assertIsInstance(history, pd.DataFrame)
        if len(history) > 0:
            # Sprawdzenie struktury historii
            expected_columns = ['date', 'ticker', 'action', 'shares', 'price']
            for col in expected_columns:
                self.assertIn(col, history.columns)
    
    @patch('trading_simulator.DataLoader')
    def test_simulator_reset_functionality(self, mock_data_loader):
        """Test funkcji resetowania symulacji"""
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.mock_data
        mock_data_loader.return_value = mock_loader_instance
        
        simulator = TradingSimulator(**self.test_config)
        simulator.setup()
        simulator.train_models()
        
        # Wykonanie kilku transakcji
        simulator.buy_stock('AAPL', 10)
        simulator.next_day()
        simulator.sell_stock('AAPL', 5)
        
        # Reset symulacji
        simulator.reset_simulation()
        
        # Sprawdzenie stanu po resecie
        self.assertEqual(simulator.current_date_index, 0)
        portfolio_summary = simulator.get_portfolio_summary()
        
        # Kapitał powinien wrócić do wartości początkowej
        self.assertAlmostEqual(
            portfolio_summary['cash'], 
            simulator.initial_capital, 
            places=2
        )
        
        # Portfel powinien być pusty
        self.assertEqual(len(portfolio_summary['positions']), 0)


class TestDataProcessorPortfolioIntegration(unittest.TestCase):
    """Testy integracji między procesorem danych a menedżerem portfela"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.processor = DataProcessor()
        self.portfolio = PortfolioManager(10000.0, 0.002)
        
        # Generowanie danych testowych
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        
        np.random.seed(42)
        base_price = 100
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Open': base_price + np.random.randn(200).cumsum(),
            'High': base_price + np.random.randn(200).cumsum() + 2,
            'Low': base_price + np.random.randn(200).cumsum() - 2,
            'Close': base_price + np.random.randn(200).cumsum(),
            'Volume': np.random.randint(1000000, 5000000, 200)
        })
        
        self.test_data.set_index('Date', inplace=True)
    
    def test_indicators_target_and_trading_integration(self):
        """Test integracji: wskaźniki -> target -> trading"""
        # Krok 1: Obliczenie wskaźników
        indicators = ['SMA', 'RSI', 'MACD']
        data_with_indicators = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertGreater(len(data_with_indicators.columns), len(self.test_data.columns))
        
        # Krok 2: Utworzenie targetu
        data_with_target = self.processor.make_target(data_with_indicators, days_ahead=1)
        
        self.assertIn('Target', data_with_target.columns)
        
        # Krok 3: Podział danych
        train_data, test_data, _, _ = self.processor.split_data(
            data_with_target,
            '2023-06-01',
            '2023-08-31',
            days_ahead=1
        )
        
        self.assertGreater(len(train_data), 0)
        self.assertGreater(len(test_data), 0)
        
        # Krok 4: Symulacja tradingu na podstawie targetu
        test_date = datetime(2023, 6, 1)
        
        for idx, row in test_data.head(10).iterrows():
            if row['Target'] == 1:  # Sygnał kupna
                if self.portfolio.can_buy('TEST', 10, row['Close']):
                    self.portfolio.buy_stock('TEST', 10, row['Close'], test_date)
            
            test_date += timedelta(days=1)
        
        # Weryfikacja że transakcje zostały wykonane
        history = self.portfolio.get_transaction_history()
        self.assertGreater(len(history), 0)
    
    def test_commission_impact_on_returns(self):
        """Test wpływu prowizji na ostateczne zwroty"""
        # Portfolio bez prowizji
        portfolio_no_commission = PortfolioManager(10000.0, 0.0)
        
        # Portfolio z prowizją
        portfolio_with_commission = PortfolioManager(10000.0, 0.002)
        
        # Identyczne transakcje
        test_date = datetime(2023, 6, 1)
        buy_price = 100.0
        sell_price = 110.0
        shares = 50
        
        # Bez prowizji
        portfolio_no_commission.buy_stock('TEST', shares, buy_price, test_date)
        portfolio_no_commission.sell_stock('TEST', shares, sell_price, test_date)
        
        # Z prowizją
        portfolio_with_commission.buy_stock('TEST', shares, buy_price, test_date)
        portfolio_with_commission.sell_stock('TEST', shares, sell_price, test_date)
        
        # Kapitał końcowy powinien być większy bez prowizji
        self.assertGreater(
            portfolio_no_commission.current_capital,
            portfolio_with_commission.current_capital
        )
        
        # Różnica powinna odpowiadać prowizjom
        buy_cost = shares * buy_price
        sell_revenue = shares * sell_price
        expected_commission = (buy_cost + sell_revenue) * 0.002
        
        actual_difference = (portfolio_no_commission.current_capital - 
                           portfolio_with_commission.current_capital)
        
        self.assertAlmostEqual(actual_difference, expected_commission, places=1)


class TestModelTrainingPredictionIntegration(unittest.TestCase):
    """Testy integracji trenowania modeli i generowania predykcji"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.processor = DataProcessor()
        
        # Generowanie danych z wyraźnym trendem dla testowania modeli
        dates = pd.date_range(start='2023-01-01', periods=300, freq='D')
        
        np.random.seed(42)
        trend = np.linspace(100, 150, 300)  # Wyraźny trend wzrostowy
        noise = np.random.randn(300) * 2
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Open': trend + noise,
            'High': trend + noise + 2,
            'Low': trend + noise - 2,
            'Close': trend + noise,
            'Volume': np.random.randint(1000000, 5000000, 300)
        })
        
        self.test_data.set_index('Date', inplace=True)
    
    @patch('trading_simulator.DataLoader')
    def test_model_prediction_consistency(self, mock_data_loader):
        """Test spójności predykcji modelu"""
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.test_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['TEST'],
            'start_date': '2023-09-01',
            'end_date': '2023-11-30',
            'model_type': 'Random Forest',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA', 'RSI'],
            'selected_features': ['Open', 'High', 'Low', 'Close', 'Volume']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        # Generowanie predykcji dla tego samego dnia wielokrotnie
        predictions_1 = simulator.get_predictions_for_current_date()
        
        # Reset do tego samego dnia
        simulator.current_date_index = 0
        predictions_2 = simulator.get_predictions_for_current_date()
        
        # Predykcje powinny być identyczne (determinizm)
        self.assertEqual(predictions_1, predictions_2)
    
    @patch('trading_simulator.DataLoader')
    def test_predictions_within_valid_range(self, mock_data_loader):
        """Test czy predykcje mieszczą się w poprawnym zakresie"""
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = self.test_data
        mock_data_loader.return_value = mock_loader_instance
        
        config = {
            'tickers': ['TEST'],
            'start_date': '2023-09-01',
            'end_date': '2023-11-30',
            'model_type': 'Decision Tree',
            'commission': 0.002,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA'],
            'selected_features': ['Close']
        }
        
        simulator = TradingSimulator(**config)
        simulator.setup()
        simulator.train_models()
        
        # Zbieranie predykcji dla kilku dni
        predictions_list = []
        
        for _ in range(10):
            predictions = simulator.get_predictions_for_current_date()
            if 'TEST' in predictions:
                predictions_list.append(predictions['TEST'])
            
            if not simulator.next_day():
                break
        
        # Predykcje binarne powinny być 0 lub 1
        for pred in predictions_list:
            self.assertIn(pred, [0, 1])


class TestEndToEndSimulation(unittest.TestCase):
    """Testy end-to-end całego procesu symulacji"""
    
    @patch('trading_simulator.DataLoader')
    def test_complete_simulation_cycle(self, mock_data_loader):
        """Test kompletnego cyklu symulacji od początku do końca"""
        # Przygotowanie danych
        dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
        
        np.random.seed(42)
        base = 100
        data = pd.DataFrame({
            'Date': dates,
            'Open': base + np.random.randn(250).cumsum(),
            'High': base + np.random.randn(250).cumsum() + 1,
            'Low': base + np.random.randn(250).cumsum() - 1,
            'Close': base + np.random.randn(250).cumsum(),
            'Volume': np.random.randint(1000000, 5000000, 250)
        })
        data.set_index('Date', inplace=True)
        
        mock_loader_instance = Mock()
        mock_loader_instance.load_data.return_value = data
        mock_data_loader.return_value = mock_loader_instance
        
        # Konfiguracja
        config = {
            'tickers': ['AAPL'],
            'start_date': '2023-07-01',
            'end_date': '2023-09-30',
            'model_type': 'Random Forest',
            'commission': 0.001,
            'days_ahead': 1,
            'initial_capital': 10000.0,
            'indicators': ['SMA', 'EMA', 'RSI'],
            'selected_features': ['Open', 'High', 'Low', 'Close', 'Volume']
        }
        
        # Utworzenie i konfiguracja symulatora
        simulator = TradingSimulator(**config)
        simulator.setup()
        self.assertTrue(simulator.is_setup)
        
        # Trenowanie modeli
        simulator.train_models()
        self.assertTrue(simulator.is_trained)
        
        # Symulacja tradingu
        days_simulated = 0
        max_days = 20
        
        while simulator.can_go_next_day() and days_simulated < max_days:
            predictions = simulator.get_predictions_for_current_date()
            prices = simulator.get_current_prices()
            
            # Prosta strategia: kup jeśli predykcja = 1
            for ticker, prediction in predictions.items():
                if prediction == 1:
                    # Próba zakupu małej ilości akcji
                    simulator.buy_stock(ticker, 5)
            
            simulator.next_day()
            days_simulated += 1
        
        # Weryfikacja wyników
        portfolio_summary = simulator.get_portfolio_summary()
        
        # Portfolio summary powinno mieć wymaganą strukturę
        self.assertIn('cash', portfolio_summary)
        self.assertIn('total_value', portfolio_summary)
        self.assertIn('total_return', portfolio_summary)
        
        # Historia transakcji powinna istnieć
        history = simulator.get_transaction_history()
        self.assertIsInstance(history, pd.DataFrame)
        
        # Historia wydajności powinna być zapisana
        performance = simulator.get_performance_history()
        self.assertIsInstance(performance, pd.DataFrame)
        self.assertGreater(len(performance), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)