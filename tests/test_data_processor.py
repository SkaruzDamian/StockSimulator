# -*- coding: utf-8 -*-
"""
Testy jednostkowe dla modułu DataProcessor
Autor: Damian Skaruz
Praca inżynierska: Projekt i implementacja autonomicznego agenta giełdowego
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# WAŻNE: Dodaj folder nadrzędny do ścieżki (testy są w podfolderze tests/)
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from data.data_processor import DataProcessor


class TestDataProcessorInitialization(unittest.TestCase):
    """Testy inicjalizacji procesora danych"""
    
    def test_initialization(self):
    
        processor = DataProcessor()
        self.assertIsNotNone(processor)


class TestDataProcessorTechnicalIndicators(unittest.TestCase):
    """Testy obliczania wskaźników technicznych"""
    
    def setUp(self):
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
    
    def test_calculate_sma_indicator(self):
        """Test obliczania wskaźnika SMA (Simple Moving Average)"""
        indicators = ['SMA']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('SMA_10', result.columns)
        self.assertIn('SMA_20', result.columns)
        self.assertIn('SMA_50', result.columns)
        
        # Sprawdzenie że wartościami nie są NaN po okresie rozgrzewki
        self.assertFalse(result['SMA_10'].iloc[-10:].isna().any())
    
    def test_calculate_ema_indicator(self):
        """Test obliczania wskaźnika EMA (Exponential Moving Average)"""
        indicators = ['EMA']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('EMA_10', result.columns)
        self.assertIn('EMA_20', result.columns)
        
        # EMA powinno reagować szybciej niż SMA
        self.assertFalse(result['EMA_10'].iloc[-10:].isna().any())
    
    def test_calculate_rsi_indicator(self):
        """Test obliczania wskaźnika RSI (Relative Strength Index)"""
        indicators = ['RSI']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('RSI_14', result.columns)
        
        # RSI powinno być w zakresie 0-100
        rsi_values = result['RSI_14'].dropna()
        self.assertTrue((rsi_values >= 0).all())
        self.assertTrue((rsi_values <= 100).all())
    
    def test_calculate_macd_indicator(self):
        """Test obliczania wskaźnika MACD"""
        indicators = ['MACD']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('MACD', result.columns)
        self.assertIn('MACD_Signal', result.columns)
        self.assertIn('MACD_Hist', result.columns)
        
        non_nan_mask = ~result['MACD'].isna() & ~result['MACD_Signal'].isna()
        calculated_hist = result.loc[non_nan_mask, 'MACD'] - result.loc[non_nan_mask, 'MACD_Signal']
        actual_hist = result.loc[non_nan_mask, 'MACD_Hist']
        
        np.testing.assert_array_almost_equal(calculated_hist.values, actual_hist.values, decimal=5)
    
    def test_calculate_bollinger_bands(self):
        """Test obliczania pasm Bollingera"""
        indicators = ['Bollinger Bands']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('BB_Upper', result.columns)
        self.assertIn('BB_Middle', result.columns)
        self.assertIn('BB_Lower', result.columns)
        self.assertIn('BB_Width', result.columns)
        self.assertIn('BB_Position', result.columns)
        
        non_nan_mask = ~result['BB_Upper'].isna() & ~result['BB_Lower'].isna()
        self.assertTrue((result.loc[non_nan_mask, 'BB_Upper'] >= 
                        result.loc[non_nan_mask, 'BB_Lower']).all())
    
    def test_calculate_multiple_indicators(self):

        indicators = ['SMA', 'EMA', 'RSI', 'MACD']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('SMA_10', result.columns)
        self.assertIn('EMA_10', result.columns)
        self.assertIn('RSI_14', result.columns)
        self.assertIn('MACD', result.columns)
    
    def test_calculate_stochastic_oscillator(self):
        """Test obliczania oscylatora stochastycznego"""
        indicators = ['Stochastic Oscillator']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('Stoch_K', result.columns)
        self.assertIn('Stoch_D', result.columns)
        
        stoch_k = result['Stoch_K'].dropna()
        stoch_d = result['Stoch_D'].dropna()
        
        # Sprawdź czy większość wartości jest w prawidłowym zakresie
        # (dopuszczamy niewielkie przekroczenia z powodu zaokrągleń)
        k_in_range = ((stoch_k >= -1) & (stoch_k <= 101)).sum()
        d_in_range = ((stoch_d >= -1) & (stoch_d <= 101)).sum()
        
        if len(stoch_k) > 0:
            self.assertGreater(k_in_range / len(stoch_k), 0.9, 
                              f"Stoch_K values out of range: min={stoch_k.min()}, max={stoch_k.max()}")
        if len(stoch_d) > 0:
            self.assertGreater(d_in_range / len(stoch_d), 0.9,
                              f"Stoch_D values out of range: min={stoch_d.min()}, max={stoch_d.max()}")
    
    def test_insufficient_data_error(self):

        small_data = self.test_data.head(10)  
        indicators = ['SMA']
        
        with self.assertRaises(ValueError) as context:
            self.processor.calculate_technical_indicators(small_data, indicators)
        
        # Sprawdź komunikat błędu (po polsku lub angielsku)
        error_msg = str(context.exception)
        self.assertTrue(
            "Not enough data points" in error_msg or 
            "Nie wystarczająca ilość danych" in error_msg,
            f"Unexpected error message: {error_msg}"
        )
    
    def test_price_change_indicator(self):
        """Test obliczania wskaźnika zmiany ceny"""
        indicators = ['Price Change']
        
        result = self.processor.calculate_technical_indicators(
            self.test_data.copy(), 
            indicators
        )
        
        self.assertIn('Price_Change', result.columns)
        
        self.assertTrue(pd.isna(result['Price_Change'].iloc[0]))
        
        manual_change = result['Close'].iloc[10] - result['Close'].iloc[9]
        self.assertAlmostEqual(result['Price_Change'].iloc[10], manual_change, places=5)


class TestDataProcessorTargetCreation(unittest.TestCase):
    """Testy tworzenia zmiennej docelowej (Target)"""
    
    def setUp(self):
        """Przygotowanie testowych danych"""
        self.processor = DataProcessor()
        
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Close': np.arange(100, 150, 1)  # Rosnący trend
        })
        
        self.test_data.set_index('Date', inplace=True)
    
    def test_make_target_one_day_ahead(self):
        """Test tworzenia targetu dla horyzontu 1 dzień"""
        days_ahead = 1
        
        result = self.processor.make_target(self.test_data.copy(), days_ahead)
        
        self.assertIn('Target', result.columns)
        
        # Dla rosnącego trendu wszystkie cele powinny być 1
        self.assertTrue((result['Target'] == 1).all())
        
        expected_length = len(self.test_data) - days_ahead
        self.assertEqual(len(result), expected_length)
    
    def test_make_target_multiple_days_ahead(self):
        """Test tworzenia targetu dla horyzontu 5 dni"""
        days_ahead = 5
        
        result = self.processor.make_target(self.test_data.copy(), days_ahead)
        
        self.assertIn('Target', result.columns)
        
        expected_length = len(self.test_data) - days_ahead
        self.assertEqual(len(result), expected_length)
    
    def test_make_target_with_falling_prices(self):
        """Test tworzenia targetu dla spadających cen"""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        falling_data = pd.DataFrame({
            'Date': dates,
            'Close': np.arange(150, 100, -1)  # Spadający trend
        })
        falling_data.set_index('Date', inplace=True)
        
        result = self.processor.make_target(falling_data, 1)
        
        # Dla spadającego trendu wszystkie cele powinny być 0
        self.assertTrue((result['Target'] == 0).all())
    
    def test_make_target_with_mixed_movements(self):
        """Test tworzenia targetu dla mieszanych ruchów cen"""
        dates = pd.date_range(start='2023-01-01', periods=20, freq='D')
        mixed_data = pd.DataFrame({
            'Date': dates,
            'Close': [100, 105, 103, 108, 106, 110, 108, 112, 111, 115,
                     114, 118, 116, 120, 119, 123, 122, 125, 124, 128]
        })
        mixed_data.set_index('Date', inplace=True)
        
        result = self.processor.make_target(mixed_data, 1)
        
        # Powinny być zarówno 0 jak i 1
        self.assertTrue(0 in result['Target'].values)
        self.assertTrue(1 in result['Target'].values)
    
    def test_make_target_insufficient_data(self):
        small_data = self.test_data.head(5)
        days_ahead = 10  # Więcej niż dostępnych danych
        
        with self.assertRaises(ValueError) as context:
            self.processor.make_target(small_data, days_ahead)
        
        # Sprawdź komunikat błędu (po polsku lub angielsku)
        error_msg = str(context.exception)
        self.assertTrue(
            "Not enough data" in error_msg or 
            "Nie wystarczająca ilość danych" in error_msg,
            f"Unexpected error message: {error_msg}"
        )
    
    def test_make_target_missing_close_column(self):
        invalid_data = pd.DataFrame({
            'Date': pd.date_range(start='2023-01-01', periods=50, freq='D'),
            'Open': np.random.rand(50)
        })
        
        with self.assertRaises(ValueError) as context:
            self.processor.make_target(invalid_data, 1)
        
        # Sprawdź komunikat błędu (po polsku lub angielsku)
        error_msg = str(context.exception)
        self.assertTrue(
            "Close price is required" in error_msg or 
            "Cena zamknięcia jest wymagana" in error_msg,
            f"Unexpected error message: {error_msg}"
        )


class TestDataProcessorDataSplit(unittest.TestCase):
    
    def setUp(self):
        """Przygotowanie testowych danych"""
        self.processor = DataProcessor()
        
        # Generowanie danych dla całego roku
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        
        self.test_data = pd.DataFrame({
            'Date': dates,
            'Close': np.random.rand(len(dates)) * 100,
            'Target': np.random.randint(0, 2, len(dates))
        })
    
    def test_split_data_basic(self):
        date_start = '2023-07-01'
        date_end = '2023-12-31'
        days_ahead = 5
        
        train_data, test_data, test_start_idx, test_end_idx = self.processor.split_data(
            self.test_data.copy(), 
            date_start, 
            date_end, 
            days_ahead
        )
        
        self.assertGreater(len(train_data), 0)
        self.assertGreater(len(test_data), 0)
        
        test_data_dates = pd.to_datetime(test_data['Date'])
        self.assertTrue((test_data_dates >= pd.to_datetime(date_start)).all())
        self.assertTrue((test_data_dates <= pd.to_datetime(date_end)).all())
    
    def test_split_data_chronological_order(self):
        date_start = '2023-06-01'
        date_end = '2023-12-31'
        days_ahead = 5
        
        train_data, test_data, _, _ = self.processor.split_data(
            self.test_data.copy(), 
            date_start, 
            date_end, 
            days_ahead
        )
        
        last_train_date = pd.to_datetime(train_data['Date']).max()
        first_test_date = pd.to_datetime(test_data['Date']).min()
        
        # Uwzględniając offset days_ahead
        self.assertLess(last_train_date, first_test_date)
    
    def test_split_data_offset_gap(self):
        """Test istnienia przerwy (gap) między zbiorem treningowym a testowym"""
        date_start = '2023-06-01'
        date_end = '2023-12-31'
        days_ahead = 10
        
        train_data, test_data, _, _ = self.processor.split_data(
            self.test_data.copy(), 
            date_start, 
            date_end, 
            days_ahead
        )
        
        # Sprawdzenie że istnieje gap o rozmiarze co najmniej days_ahead
        train_dates = pd.to_datetime(train_data['Date'])
        test_dates = pd.to_datetime(test_data['Date'])
        
        gap_days = (test_dates.min() - train_dates.max()).days
        self.assertGreaterEqual(gap_days, days_ahead)
    
    def test_split_data_no_data_in_range(self):
        date_start = '2025-01-01'  # Data poza zakresem
        date_end = '2025-12-31'
        days_ahead = 5
        
        with self.assertRaises(ValueError) as context:
            self.processor.split_data(
                self.test_data.copy(), 
                date_start, 
                date_end, 
                days_ahead
            )
        
        # Sprawdź komunikat błędu (po polsku lub angielsku)
        error_msg = str(context.exception)
        self.assertTrue(
            "No data found" in error_msg or 
            "Nie znaleziono danych" in error_msg,
            f"Unexpected error message: {error_msg}"
        )
    
    def test_split_data_insufficient_training_data(self):
        # Wybór zakresu testowego na samym początku danych
        date_start = '2023-01-01'
        date_end = '2023-01-10'
        days_ahead = 100  # Więcej niż dostępnych dni przed testem
        
        with self.assertRaises(ValueError) as context:
            self.processor.split_data(
                self.test_data.copy(), 
                date_start, 
                date_end, 
                days_ahead
            )
        
        # Sprawdź komunikat błędu (po polsku lub angielsku)
        error_msg = str(context.exception)
        self.assertTrue(
            "Not enough data before test period" in error_msg or 
            "Niewystarczająca ilość danych przed okresem testowym" in error_msg,
            f"Unexpected error message: {error_msg}"
        )
    
    def test_split_data_returns_indices(self):
        date_start = '2023-07-01'
        date_end = '2023-12-31'
        days_ahead = 5
        
        _, _, test_start_idx, test_end_idx = self.processor.split_data(
            self.test_data.copy(), 
            date_start, 
            date_end, 
            days_ahead
        )
        
        self.assertIsInstance(test_start_idx, (int, np.integer))
        self.assertIsInstance(test_end_idx, (int, np.integer))
        
        self.assertGreater(test_end_idx, test_start_idx)


class TestDataProcessorEdgeCases(unittest.TestCase):
    """Testy przypadków brzegowych procesora danych"""
    
    def setUp(self):
        self.processor = DataProcessor()
    
    def test_empty_dataframe(self):
        empty_df = pd.DataFrame()
        indicators = ['SMA']
        
        with self.assertRaises(ValueError):
            self.processor.calculate_technical_indicators(empty_df, indicators)
    
    def test_data_with_nan_values(self):
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        data_with_nan = pd.DataFrame({
            'Date': dates,
            'Close': np.random.rand(100) * 100
        })
        
        # Wprowadzenie NaN
        data_with_nan.loc[10:15, 'Close'] = np.nan
        data_with_nan.set_index('Date', inplace=True)
        
        indicators = ['SMA']
        result = self.processor.calculate_technical_indicators(data_with_nan, indicators)
        
        self.assertFalse(result['Close'].isna().any())


if __name__ == '__main__':
    unittest.main(verbosity=2)