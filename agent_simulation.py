import pandas as pd
import numpy as np
import os
import shutil
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from portfolio_manager import PortfolioManager
from transaction_logger import TransactionLogger
from utils import format_currency, format_percentage, calculate_returns

class InvestmentStrategy(ABC):
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    @abstractmethod
    def should_buy(self, ticker, prediction, current_price, portfolio_data, market_data):
        pass
    
    @abstractmethod
    def calculate_position_size(self, ticker, available_capital, num_tickers, current_price):
        pass
    
    @abstractmethod
    def should_sell(self, ticker, position, current_price, buy_date, current_date, days_ahead):
        pass

class BasicStrategy(InvestmentStrategy):
    
    def __init__(self):
        super().__init__("Basic Strategy", "Kupuj przy prediction=1, sprzedawaj po określonym czasie")
    
    def should_buy(self, ticker, prediction, current_price, portfolio_data, market_data):
        return prediction == 1
    
    def calculate_position_size(self, ticker, available_capital, num_tickers, current_price):
        max_per_stock = available_capital / num_tickers
        shares = int(max_per_stock / current_price)
        return max(shares, 0)
    
    def should_sell(self, ticker, position, current_price, buy_date, current_date, days_ahead):
        days_held = (current_date - buy_date).days
        return days_held >= days_ahead

class AggressiveStrategy(InvestmentStrategy):
    
    def __init__(self):
        super().__init__("Aggressive Strategy", "Większe pozycje, koncentracja na najlepszych sygnałach")
    
    def should_buy(self, ticker, prediction, current_price, portfolio_data, market_data):
        return prediction == 1
    
    def calculate_position_size(self, ticker, available_capital, num_tickers, current_price):
        max_per_stock = (available_capital * 0.8) / num_tickers
        shares = int(max_per_stock / current_price)
        return max(shares, 0)
    
    def should_sell(self, ticker, position, current_price, buy_date, current_date, days_ahead):
        days_held = (current_date - buy_date).days
        profit_loss = (current_price - position['avg_price']) / position['avg_price']
        return days_held >= days_ahead or profit_loss < -0.05

class ConservativeStrategy(InvestmentStrategy):
    
    def __init__(self):
        super().__init__("Conservative Strategy", "Mniejsze pozycje, dłuższe trzymanie, stop-loss")
    
    def should_buy(self, ticker, prediction, current_price, portfolio_data, market_data):
        return prediction == 1
    
    def calculate_position_size(self, ticker, available_capital, num_tickers, current_price):
        max_per_stock = (available_capital * 0.5) / num_tickers
        shares = int(max_per_stock / current_price)
        return max(shares, 0)
    
    def should_sell(self, ticker, position, current_price, buy_date, current_date, days_ahead):
        days_held = (current_date - buy_date).days
        profit_loss = (current_price - position['avg_price']) / position['avg_price']
        
        return (days_held >= days_ahead * 1.5 or 
                profit_loss > 0.10 or 
                profit_loss < -0.03)

class AgentSimulation:
    def __init__(self, trading_simulator, strategy=None, progress_callback=None):
        self.trading_simulator = trading_simulator
        self.strategy = strategy or BasicStrategy()
        self.progress_callback = progress_callback
        
        self.clean_agent_logs()
        
        self.agent_portfolio = PortfolioManager(
            trading_simulator.initial_capital,
            trading_simulator.commission
        )
        
        self.agent_logger = TransactionLogger("agent_logs")
        
        self.positions_with_dates = {}
        
        self.stats = {
            'total_transactions': 0,
            'buy_transactions': 0,
            'sell_transactions': 0,
            'correct_predictions': 0,
            'total_predictions': 0,
            'profitable_trades': 0,
            'losing_trades': 0,
            'total_profit_loss': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.is_running = False
        self.is_completed = False
    
    def clean_agent_logs(self):
        try:
            agent_logs_dir = "agent_logs"
            if os.path.exists(agent_logs_dir):
                print(f"DEBUG: Usuwam stare pliki z {agent_logs_dir}")
                shutil.rmtree(agent_logs_dir)
                print(f"DEBUG: Folder {agent_logs_dir} został wyczyszczony")
            os.makedirs(agent_logs_dir, exist_ok=True)
            print(f"DEBUG: Utworzono czysty folder {agent_logs_dir}")
        except Exception as e:
            print(f"BŁĄD czyszczenia agent_logs: {e}")
    
    def run_simulation(self):
        if self.is_running:
            return False, "Symulacja już trwa"
        
        if not self.trading_simulator.is_trained:
            return False, "Model nie został wytrenowany"
        
        self.is_running = True
        self.is_completed = False
        self.stats['start_time'] = datetime.now()
        
        print(f"Rozpoczynam symulację agenta ze strategią: {self.strategy.name}")
        
        self.trading_simulator.reset_simulation()
        
        simulation_day = 0
        total_days = len(self.trading_simulator.trading_dates)
        
        try:
            while self.trading_simulator.can_go_next_day():
                current_date = self.trading_simulator.get_current_date()
                prices = self.trading_simulator.current_prices
                
                self._execute_daily_logic(current_date)
                
                self.agent_portfolio.record_daily_value(current_date, prices)
                
                self.trading_simulator.next_day()
                simulation_day += 1
                
                if self.progress_callback:
                    progress = (simulation_day / total_days) * 100
                    self.progress_callback(simulation_day, total_days, progress)
            
            self._final_cleanup()
            
            self.stats['end_time'] = datetime.now()
            self.is_completed = True
            self.is_running = False
            
            self._finalize_simulation()
            
            print(f"DEBUG: Końcowa liczba rekordów w daily_portfolio_value: {len(self.agent_portfolio.daily_portfolio_value)}")
            
            return True, "Symulacja agenta zakończona pomyślnie"
            
        except Exception as e:
            self.is_running = False
            return False, f"Błąd podczas symulacji: {str(e)}"
    
    def _execute_daily_logic(self, current_date):
        predictions = self.trading_simulator.current_predictions
        prices = self.trading_simulator.current_prices
        
        self._check_sell_signals(current_date, prices)
        self._check_buy_signals(current_date, predictions, prices)
        
        self.agent_portfolio.record_daily_value(current_date, prices)
        
        portfolio_summary = self.agent_portfolio.get_portfolio_summary(prices)
        self.agent_logger.log_daily_portfolio(current_date, portfolio_summary, predictions)
    def _check_sell_signals(self, current_date, prices):
        positions_to_sell = []
        
        for ticker in list(self.positions_with_dates.keys()):
            if ticker not in prices:
                continue
                
            position_info = self.positions_with_dates[ticker]
            current_price = prices[ticker]
            
            portfolio_position = self.agent_portfolio.get_position(ticker)
            if portfolio_position['shares'] == 0:
                del self.positions_with_dates[ticker]
                continue
            
            should_sell = self.strategy.should_sell(
                ticker, portfolio_position, current_price,
                position_info['buy_date'], current_date,
                self.trading_simulator.days_ahead
            )
            
            if should_sell:
                positions_to_sell.append((ticker, portfolio_position['shares'], current_price))
        
        for ticker, shares, price in positions_to_sell:
            self._execute_sell(ticker, shares, price, current_date)
    
    def _check_buy_signals(self, current_date, predictions, prices):
        available_cash = self.agent_portfolio.get_available_cash()
        num_tickers = len(self.trading_simulator.tickers)
        
        for ticker in self.trading_simulator.tickers:
            if ticker not in predictions or ticker not in prices:
                continue
            
            prediction = predictions[ticker]
            current_price = prices[ticker]
            
            current_position = self.agent_portfolio.get_position(ticker)
            if current_position['shares'] > 0:
                continue
            
            should_buy = self.strategy.should_buy(
                ticker, prediction, current_price,
                self.agent_portfolio.get_portfolio_summary(prices), {}
            )
            
            if should_buy:
                shares = self.strategy.calculate_position_size(
                    ticker, available_cash, num_tickers, current_price
                )
                
                if shares > 0:
                    self._execute_buy(ticker, shares, current_price, current_date, prediction)
    
    def _execute_buy(self, ticker, shares, price, date, prediction):
        ticker_row = self.trading_simulator.get_ticker_data_for_date(ticker, date)
        
        if ticker_row is not None and 'Open' in ticker_row:
            buy_price = ticker_row['Open']
        else:
            buy_price = price
        
        success, message = self.agent_portfolio.buy_stock(ticker, shares, buy_price, date)
        
        if success:
            self.positions_with_dates[ticker] = {
                'buy_date': date,
                'buy_price': buy_price,
                'prediction': prediction,
                'shares': shares
            }
            
            self.stats['total_transactions'] += 1
            self.stats['buy_transactions'] += 1
            self.stats['total_predictions'] += 1
            
            total_cost = shares * buy_price
            commission = total_cost * self.trading_simulator.commission
            self.agent_logger.log_transaction(
                date, ticker, "BUY", shares, buy_price, commission, total_cost + commission, True
            )
            
            self.agent_logger.log_prediction(date, ticker, prediction)
            
            print(f"Agent kupił {shares} akcji {ticker} po ${buy_price:.2f} (Open)")
    
    def _execute_sell(self, ticker, shares, price, date):
        sell_price = price
        
        success, message = self.agent_portfolio.sell_stock(ticker, shares, sell_price, date)
        
        if success and ticker in self.positions_with_dates:
            position_info = self.positions_with_dates[ticker]
            buy_price = position_info['buy_price']
            prediction = position_info['prediction']
            
            profit_loss = (sell_price - buy_price) * shares
            profit_loss_pct = ((sell_price - buy_price) / buy_price) * 100
            
            price_change = sell_price - buy_price
            actual_direction = 1 if price_change > 0 else 0
            
            if prediction == actual_direction:
                self.stats['correct_predictions'] += 1
            
            self.stats['total_transactions'] += 1
            self.stats['sell_transactions'] += 1
            self.stats['total_profit_loss'] += profit_loss
            
            if profit_loss > 0:
                self.stats['profitable_trades'] += 1
                if profit_loss > self.stats['best_trade']:
                    self.stats['best_trade'] = profit_loss
            else:
                self.stats['losing_trades'] += 1
                if profit_loss < self.stats['worst_trade']:
                    self.stats['worst_trade'] = profit_loss
            
            total_revenue = shares * sell_price
            commission = total_revenue * self.trading_simulator.commission
            self.agent_logger.log_transaction(
                date, ticker, "SELL", shares, sell_price, commission, total_revenue - commission, True
            )
            
            self.agent_logger.update_actual_outcome(ticker, position_info['buy_date'], price_change)
            
            print(f"Agent sprzedał {shares} akcji {ticker} po ${sell_price:.2f} (Close) (P&L: ${profit_loss:.2f})")
            
            del self.positions_with_dates[ticker]
    
    def _final_cleanup(self):
        if not self.trading_simulator.trading_dates:
            return
            
        last_date = self.trading_simulator.trading_dates[-1]
        
        final_prices = {}
        for ticker in list(self.positions_with_dates.keys()):
            ticker_data = self.trading_simulator.get_ticker_data_until_date(ticker, last_date)
            if ticker_data is not None and not ticker_data.empty and 'Close' in ticker_data.columns:
                final_prices[ticker] = ticker_data['Close'].iloc[-1]
            else:
                if ticker in self.trading_simulator.current_prices:
                    final_prices[ticker] = self.trading_simulator.current_prices[ticker]
        
        for ticker in list(self.positions_with_dates.keys()):
            if ticker in final_prices:
                position = self.agent_portfolio.get_position(ticker)
                if position['shares'] > 0:
                    print(f"Finalna sprzedaż: {ticker} po ${final_prices[ticker]:.2f}")
                    self._execute_sell(ticker, position['shares'], final_prices[ticker], last_date)
    
    def _finalize_simulation(self):
        final_portfolio = self.agent_portfolio.get_portfolio_summary(self.trading_simulator.current_prices)
        
        accuracy = 0
        if self.stats['total_predictions'] > 0:
            accuracy = (self.stats['correct_predictions'] / self.stats['total_predictions']) * 100
        
        self.stats['final_portfolio_value'] = final_portfolio['total_value']
        self.stats['total_return'] = final_portfolio['total_return']
        self.stats['return_percentage'] = final_portfolio['return_percentage']
        self.stats['accuracy'] = accuracy
        
        self.agent_logger.finalize_logs(final_portfolio)
        self._write_simulation_summary()
    
    def _write_simulation_summary(self):
        summary_file = f"agent_logs/simulation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("PODSUMOWANIE SYMULACJI AGENTA\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Strategia: {self.strategy.name}\n")
            f.write(f"Opis: {self.strategy.description}\n\n")
            
            f.write("WYNIKI FINANSOWE:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Kapitał początkowy: {format_currency(self.trading_simulator.initial_capital)}\n")
            f.write(f"Wartość końcowa: {format_currency(self.stats['final_portfolio_value'])}\n")
            f.write(f"Całkowity zwrot: {format_currency(self.stats['total_return'])}\n")
            f.write(f"Zwrot procentowy: {format_percentage(self.stats['return_percentage'])}\n\n")
            
            f.write("STATYSTYKI TRANSAKCJI:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Łączne transakcje: {self.stats['total_transactions']}\n")
            f.write(f"Transakcje kupna: {self.stats['buy_transactions']}\n")
            f.write(f"Transakcje sprzedaży: {self.stats['sell_transactions']}\n")
            f.write(f"Zyskowne transakcje: {self.stats['profitable_trades']}\n")
            f.write(f"Stratne transakcje: {self.stats['losing_trades']}\n")
            f.write(f"Najlepszy trade: {format_currency(self.stats['best_trade'])}\n")
            f.write(f"Najgorszy trade: {format_currency(self.stats['worst_trade'])}\n\n")
            
            f.write("SKUTECZNOŚĆ MODELU:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Dokładność przewidywań: {self.stats['accuracy']:.2f}%\n")
            f.write(f"Poprawne przewidywania: {self.stats['correct_predictions']}\n")
            f.write(f"Łączne przewidywania: {self.stats['total_predictions']}\n")
            f.write(f"Błędne przewidywania: {self.stats['total_predictions'] - self.stats['correct_predictions']}\n\n")
            
            duration = self.stats['end_time'] - self.stats['start_time']
            f.write("CZAS SYMULACJI:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Rozpoczęcie: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Zakończenie: {self.stats['end_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Czas trwania: {duration}\n")
            
            f.write("\n" + "=" * 80 + "\n")
    
    def get_progress_info(self):
        if not self.is_running and not self.is_completed:
            return "Symulacja nie została rozpoczęta"
        
        if self.is_completed:
            return f"Symulacja zakończona - Wynik: {format_currency(self.stats.get('total_return', 0))}"
        
        current_day = self.trading_simulator.current_date_index + 1
        total_days = len(self.trading_simulator.trading_dates)
        progress = (current_day / total_days) * 100
        
        return f"Dzień {current_day}/{total_days} ({progress:.1f}%) - Transakcje: {self.stats['total_transactions']}"
    
    def get_current_stats(self):
        if self.trading_simulator.current_prices:
            current_portfolio = self.agent_portfolio.get_portfolio_summary(self.trading_simulator.current_prices)
            
            return {
                'portfolio_value': current_portfolio['total_value'],
                'return': current_portfolio['total_return'],
                'return_pct': current_portfolio['return_percentage'],
                'transactions': self.stats['total_transactions'],
                'accuracy': (self.stats['correct_predictions'] / max(self.stats['total_predictions'], 1)) * 100,
                'positions': len(self.positions_with_dates)
            }
        
        return {
            'portfolio_value': self.trading_simulator.initial_capital,
            'return': 0,
            'return_pct': 0,
            'transactions': 0,
            'accuracy': 0,
            'positions': 0
        }