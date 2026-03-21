"""
Testy jednostkowe dla modułu PortfolioManager
Autor: Damian Skaruz
Praca inżynierska: Projekt i implementacja autonomicznego agenta giełdowego
"""

import unittest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from portfolio_manager import PortfolioManager


class TestPortfolioManagerInitialization(unittest.TestCase):
    """Testy weryfikujące poprawność inicjalizacji menedżera portfela"""
    
    def test_initialization_with_valid_parameters(self):
        """Test inicjalizacji z poprawnymi parametrami"""
        initial_capital = 10000.0
        commission_rate = 0.002
        
        pm = PortfolioManager(initial_capital, commission_rate)
        
        self.assertEqual(pm.initial_capital, initial_capital)
        self.assertEqual(pm.current_capital, initial_capital)
        self.assertEqual(pm.commission_rate, commission_rate)
        self.assertEqual(len(pm.positions), 0)
        self.assertEqual(len(pm.transaction_history), 0)
        self.assertEqual(len(pm.daily_portfolio_value), 0)
    
    def test_initialization_with_zero_capital(self):
        """Test inicjalizacji z zerowym kapitałem początkowym"""
        pm = PortfolioManager(0, 0.002)
        self.assertEqual(pm.current_capital, 0)
    
    def test_initialization_with_high_commission(self):
        """Test inicjalizacji z wysoką prowizją"""
        pm = PortfolioManager(10000.0, 0.05)  # 5% prowizji
        self.assertEqual(pm.commission_rate, 0.05)


class TestPortfolioManagerBuyOperations(unittest.TestCase):
    """Testy operacji zakupu akcji"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.pm = PortfolioManager(10000.0, 0.002)
        self.test_date = datetime(2024, 1, 15)
    
    def test_buy_stock_single_transaction(self):
        """Test zakupu akcji w pojedynczej transakcji"""
        ticker = "AAPL"
        shares = 10
        price = 150.0
        
        success, message = self.pm.buy_stock(ticker, shares, price, self.test_date)
        
        self.assertTrue(success)
        self.assertIn("Bought", message)
        
        position = self.pm.get_position(ticker)
        self.assertEqual(position['shares'], shares)
        self.assertEqual(position['avg_price'], price)
        
        expected_cost = shares * price
        expected_commission = expected_cost * 0.002
        expected_total = expected_cost + expected_commission
        expected_remaining_capital = 10000.0 - expected_total
        
        self.assertAlmostEqual(self.pm.current_capital, expected_remaining_capital, places=2)
    
    def test_buy_stock_multiple_transactions_same_ticker(self):
        """Test wielokrotnego zakupu tego samego tickera (averaging)"""
        ticker = "AAPL"
        
        # Pierwsza transakcja
        self.pm.buy_stock(ticker, 10, 100.0, self.test_date)
        
        # Druga transakcja - wyższa cena
        self.pm.buy_stock(ticker, 10, 150.0, self.test_date)
        
        position = self.pm.get_position(ticker)
        self.assertEqual(position['shares'], 20)
        
        # Średnia cena powinna być (10*100 + 10*150) / 20 = 125
        expected_avg_price = (10 * 100.0 + 10 * 150.0) / 20
        self.assertAlmostEqual(position['avg_price'], expected_avg_price, places=2)
    
    def test_buy_stock_insufficient_funds(self):
        """Test próby zakupu akcji przy niewystarczających środkach"""
        ticker = "TSLA"
        shares = 100
        price = 200.0  # Koszt: 20000 + prowizja > 10000
        
        success, message = self.pm.buy_stock(ticker, shares, price, self.test_date)
        
        self.assertFalse(success)
        self.assertIn("Insufficient funds", message)
        
        position = self.pm.get_position(ticker)
        self.assertEqual(position['shares'], 0)
        self.assertEqual(self.pm.current_capital, 10000.0)
    
    def test_can_buy_method(self):
        """Test metody sprawdzającej możliwość zakupu"""
        ticker = "AAPL"
        
        # Zakup możliwy
        self.assertTrue(self.pm.can_buy(ticker, 10, 100.0))
        
        # Zakup niemożliwy
        self.assertFalse(self.pm.can_buy(ticker, 100, 200.0))
    
    def test_buy_stock_commission_calculation(self):
        """Test poprawności obliczania prowizji przy zakupie"""
        ticker = "AAPL"
        shares = 10
        price = 100.0
        
        initial_capital = self.pm.current_capital
        self.pm.buy_stock(ticker, shares, price, self.test_date)
        
        cost = shares * price
        expected_commission = cost * 0.002
        expected_total_cost = cost + expected_commission
        
        actual_spent = initial_capital - self.pm.current_capital
        self.assertAlmostEqual(actual_spent, expected_total_cost, places=2)


class TestPortfolioManagerSellOperations(unittest.TestCase):
    """Testy operacji sprzedaży akcji"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.pm = PortfolioManager(10000.0, 0.002)
        self.test_date = datetime(2024, 1, 15)
        
        # Zakup akcji do testów sprzedaży
        self.pm.buy_stock("AAPL", 20, 100.0, self.test_date)
    
    def test_sell_stock_partial_position(self):
        """Test częściowej sprzedaży pozycji"""
        ticker = "AAPL"
        shares_to_sell = 10
        sell_price = 120.0
        
        initial_capital = self.pm.current_capital
        success, message = self.pm.sell_stock(ticker, shares_to_sell, sell_price, self.test_date)
        
        self.assertTrue(success)
        self.assertIn("Sold", message)
        
        position = self.pm.get_position(ticker)
        self.assertEqual(position['shares'], 10)  # Pozostało 10 akcji
        
        revenue = shares_to_sell * sell_price
        commission = revenue * 0.002
        net_revenue = revenue - commission
        
        expected_capital = initial_capital + net_revenue
        self.assertAlmostEqual(self.pm.current_capital, expected_capital, places=2)
    
    def test_sell_stock_complete_position(self):
        """Test całkowitej sprzedaży pozycji"""
        ticker = "AAPL"
        shares_to_sell = 20
        sell_price = 110.0
        
        success, message = self.pm.sell_stock(ticker, shares_to_sell, sell_price, self.test_date)
        
        self.assertTrue(success)
        
        # Pozycja powinna być całkowicie zamknięta
        position = self.pm.get_position(ticker)
        self.assertEqual(position['shares'], 0)
        self.assertNotIn(ticker, self.pm.positions)
    
    def test_sell_stock_insufficient_shares(self):
        """Test próby sprzedaży większej liczby akcji niż posiadane"""
        ticker = "AAPL"
        shares_to_sell = 50  # Mamy tylko 20
        
        success, message = self.pm.sell_stock(ticker, shares_to_sell, 100.0, self.test_date)
        
        self.assertFalse(success)
        self.assertIn("Insufficient shares", message)
        
        # Pozycja nie powinna się zmienić
        position = self.pm.get_position(ticker)
        self.assertEqual(position['shares'], 20)
    
    def test_can_sell_method(self):
        """Test metody sprawdzającej możliwość sprzedaży"""
        ticker = "AAPL"
        
        # Sprzedaż możliwa
        self.assertTrue(self.pm.can_sell(ticker, 10))
        self.assertTrue(self.pm.can_sell(ticker, 20))
        
        # Sprzedaż niemożliwa
        self.assertFalse(self.pm.can_sell(ticker, 50))
    
    def test_sell_stock_commission_calculation(self):
        """Test poprawności obliczania prowizji przy sprzedaży"""
        ticker = "AAPL"
        shares = 10
        price = 120.0
        
        initial_capital = self.pm.current_capital
        self.pm.sell_stock(ticker, shares, price, self.test_date)
        
        revenue = shares * price
        expected_commission = revenue * 0.002
        expected_net_revenue = revenue - expected_commission
        
        actual_gained = self.pm.current_capital - initial_capital
        self.assertAlmostEqual(actual_gained, expected_net_revenue, places=2)


class TestPortfolioManagerPortfolioValue(unittest.TestCase):
    """Testy obliczania wartości portfela"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.pm = PortfolioManager(10000.0, 0.002)
        self.test_date = datetime(2024, 1, 15)
        
        # Budowa portfela
        self.pm.buy_stock("AAPL", 10, 100.0, self.test_date)
        self.pm.buy_stock("MSFT", 5, 200.0, self.test_date)
    
    def test_get_portfolio_value_no_price_change(self):
        """Test wartości portfela bez zmian cen"""
        current_prices = {
            "AAPL": 100.0,
            "MSFT": 200.0
        }
        
        portfolio_value = self.pm.get_portfolio_value(current_prices)
        
        # Wartość pozycji: 10*100 + 5*200 = 2000
        # Plus pozostała gotówka
        expected_positions_value = 2000.0
        expected_total = self.pm.current_capital + expected_positions_value
        
        self.assertAlmostEqual(portfolio_value, expected_total, places=2)
    
    def test_get_portfolio_value_with_gains(self):
        """Test wartości portfela ze wzrostem cen"""
        current_prices = {
            "AAPL": 150.0,  # +50%
            "MSFT": 250.0   # +25%
        }
        
        portfolio_value = self.pm.get_portfolio_value(current_prices)
        
        expected_positions_value = 10 * 150.0 + 5 * 250.0  # 2750
        expected_total = self.pm.current_capital + expected_positions_value
        
        self.assertAlmostEqual(portfolio_value, expected_total, places=2)
    
    def test_get_portfolio_value_with_losses(self):
        """Test wartości portfela ze spadkiem cen"""
        current_prices = {
            "AAPL": 80.0,   # -20%
            "MSFT": 180.0   # -10%
        }
        
        portfolio_value = self.pm.get_portfolio_value(current_prices)
        
        expected_positions_value = 10 * 80.0 + 5 * 180.0  # 1700
        expected_total = self.pm.current_capital + expected_positions_value
        
        self.assertAlmostEqual(portfolio_value, expected_total, places=2)
    
    def test_get_portfolio_summary_structure(self):
        """Test struktury zwracanego podsumowania portfela"""
        current_prices = {
            "AAPL": 120.0,
            "MSFT": 220.0
        }
        
        summary = self.pm.get_portfolio_summary(current_prices)
        
        # Sprawdzenie struktury
        self.assertIn('cash', summary)
        self.assertIn('total_value', summary)
        self.assertIn('total_return', summary)
        self.assertIn('return_percentage', summary)
        self.assertIn('positions', summary)
        
        # Sprawdzenie pozycji
        self.assertEqual(len(summary['positions']), 2)
        
        for position in summary['positions']:
            self.assertIn('ticker', position)
            self.assertIn('shares', position)
            self.assertIn('avg_price', position)
            self.assertIn('current_price', position)
            self.assertIn('market_value', position)
            self.assertIn('unrealized_pnl', position)
            self.assertIn('unrealized_pnl_pct', position)


class TestPortfolioManagerTransactionHistory(unittest.TestCase):
    """Testy historii transakcji i wydajności"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.pm = PortfolioManager(10000.0, 0.002)
        self.test_date = datetime(2024, 1, 15)
    
    def test_transaction_history_recording(self):
        """Test zapisywania historii transakcji"""
        self.pm.buy_stock("AAPL", 10, 100.0, self.test_date)
        self.pm.sell_stock("AAPL", 5, 120.0, self.test_date)
        
        history = self.pm.get_transaction_history()
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history.iloc[0]['action'], 'BUY')
        self.assertEqual(history.iloc[1]['action'], 'SELL')
    
    def test_record_daily_value(self):
        """Test zapisywania dziennej wartości portfela"""
        self.pm.buy_stock("AAPL", 10, 100.0, self.test_date)
        
        current_prices = {"AAPL": 110.0}
        self.pm.record_daily_value(self.test_date, current_prices)
        
        performance = self.pm.get_performance_history()
        
        self.assertEqual(len(performance), 1)
        self.assertIn('date', performance.columns)
        self.assertIn('value', performance.columns)
        self.assertIn('return', performance.columns)
    
    def test_reset_portfolio(self):
        """Test resetowania portfela do stanu początkowego"""
        self.pm.buy_stock("AAPL", 10, 100.0, self.test_date)
        
        self.pm.reset_portfolio()
        
        self.assertEqual(self.pm.current_capital, self.pm.initial_capital)
        self.assertEqual(len(self.pm.positions), 0)
        self.assertEqual(len(self.pm.transaction_history), 0)
        self.assertEqual(len(self.pm.daily_portfolio_value), 0)


class TestPortfolioManagerEdgeCases(unittest.TestCase):
    """Testy przypadków brzegowych"""
    
    def setUp(self):
        """Przygotowanie środowiska testowego"""
        self.pm = PortfolioManager(10000.0, 0.002)
        self.test_date = datetime(2024, 1, 15)
    
    def test_get_position_nonexistent_ticker(self):
        """Test pobierania pozycji dla nieistniejącego tickera"""
        position = self.pm.get_position("NONEXISTENT")
        
        self.assertEqual(position['shares'], 0)
        self.assertEqual(position['avg_price'], 0.0)
    
    def test_multiple_tickers_independence(self):
        """Test niezależności transakcji na różnych tickerach"""
        self.pm.buy_stock("AAPL", 10, 100.0, self.test_date)
        self.pm.buy_stock("MSFT", 5, 200.0, self.test_date)
        
        # Sprzedaż jednego nie powinna wpływać na drugi
        self.pm.sell_stock("AAPL", 5, 120.0, self.test_date)
        
        aapl_position = self.pm.get_position("AAPL")
        msft_position = self.pm.get_position("MSFT")
        
        self.assertEqual(aapl_position['shares'], 5)
        self.assertEqual(msft_position['shares'], 5)
    
    def test_transaction_with_zero_commission(self):
        """Test transakcji z zerową prowizją"""
        pm_no_commission = PortfolioManager(10000.0, 0.0)
        
        pm_no_commission.buy_stock("AAPL", 10, 100.0, self.test_date)
        
        # Przy braku prowizji, koszt powinien być dokładnie shares * price
        expected_capital = 10000.0 - (10 * 100.0)
        self.assertEqual(pm_no_commission.current_capital, expected_capital)


if __name__ == '__main__':
    # Konfiguracja testów
    unittest.main(verbosity=2)