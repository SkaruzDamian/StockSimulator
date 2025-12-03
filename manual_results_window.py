import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from utils import format_currency, format_percentage

class ManualResultsWindow:
    def __init__(self, parent, simulator):
        self.parent = parent
        self.simulator = simulator
        self.window = None
        
    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Wyniki Symulacji Manualnej")
        self.window.geometry("1400x900")
        self.window.state('zoomed')
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Wyniki Symulacji Manualnej", font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        overview_frame = ttk.Frame(notebook)
        ticker_frame = ttk.Frame(notebook)
        
        notebook.add(overview_frame, text="Portfolio Ogólnie")
        notebook.add(ticker_frame, text="Portfolio per Ticker")
        
        self.create_overview_chart(overview_frame)
        self.create_ticker_charts(ticker_frame)
        
    def create_overview_chart(self, parent):
        performance_data = self.simulator.portfolio_manager.daily_portfolio_value
        
        if not performance_data or len(performance_data) == 0:
            ttk.Label(parent, text="Brak danych do wyświetlenia").pack()
            print(f"DEBUG: daily_portfolio_value jest puste: {performance_data}")
            return
        
        print(f"DEBUG: Znaleziono {len(performance_data)} rekordów w daily_portfolio_value")
        
        df = pd.DataFrame(performance_data)
        
        figure = Figure(figsize=(14, 8))
        ax = figure.add_subplot(111)
        
        dates = pd.to_datetime(df['date'])
        values = df['value']
        
        ax.plot(dates, values, linewidth=2, color='#1f77b4', label='Wartość Portfolio')
        ax.fill_between(dates, values, self.simulator.initial_capital, alpha=0.3, color='#1f77b4')
        ax.axhline(y=self.simulator.initial_capital, color='red', linestyle='--', linewidth=2, label='Kapitał początkowy')
        
        ax.set_title('Całkowita Wartość Portfolio w Czasie', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Wartość Portfolio ($)', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        figure.autofmt_xdate()
        
        canvas = FigureCanvasTkAgg(figure, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        
    def create_ticker_charts(self, parent):
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas = tk.Canvas(canvas_frame, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        inner_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')
        
        transactions = self.simulator.portfolio_manager.transaction_history
        
        if not transactions:
            ttk.Label(inner_frame, text="Brak transakcji").pack()
            return
        
        df_transactions = pd.DataFrame(transactions)
        tickers = df_transactions['ticker'].unique()
        
        for ticker in tickers:
            self.create_ticker_portfolio_value_chart(inner_frame, ticker, df_transactions)
        
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
    def create_ticker_portfolio_value_chart(self, parent, ticker, all_transactions):
        frame = ttk.LabelFrame(parent, text=f"{ticker} - Wartość Portfolio", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=10)
        
        ticker_transactions = all_transactions[all_transactions['ticker'] == ticker].copy()
        ticker_transactions = ticker_transactions.sort_values('date')
        
        dates = []
        portfolio_values = []
        shares_held = 0
        total_cost = 0
        
        for _, row in ticker_transactions.iterrows():
            date = pd.to_datetime(row['date'])
            action = row['action']
            shares = row['shares']
            price = row['price']
            
            if action == 'BUY':
                total_cost += shares * price
                shares_held += shares
            elif action == 'SELL':
                if shares_held > 0:
                    cost_per_share = total_cost / shares_held
                    total_cost -= shares * cost_per_share
                    shares_held -= shares
            
            portfolio_value = shares_held * price
            dates.append(date)
            portfolio_values.append(portfolio_value)
        
        if not dates:
            ttk.Label(frame, text="Brak danych dla tego tickera").pack()
            return
        
        figure = Figure(figsize=(12, 5))
        ax = figure.add_subplot(111)
        
        ax.plot(dates, portfolio_values, linewidth=2, color='#2ca02c', marker='o', markersize=4)
        ax.fill_between(dates, portfolio_values, 0, alpha=0.3, color='#2ca02c')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        ax.set_title(f'{ticker} - Wartość Pozycji w Portfolio', fontsize=14, fontweight='bold')
        ax.set_xlabel('Data', fontsize=11)
        ax.set_ylabel('Wartość Portfolio ($)', fontsize=11)
        ax.grid(True, alpha=0.3)
        figure.autofmt_xdate()
        
        canvas_widget = FigureCanvasTkAgg(figure, frame)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas_widget, frame)
        toolbar.update()