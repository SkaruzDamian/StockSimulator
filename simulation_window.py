import tkinter as tk
from tkinter import ttk, messagebox
from chart_widget import ChartWidget
from portfolio_widget import PortfolioWidget
from manual_results_window import ManualResultsWindow
from utils import format_currency, format_percentage

class SimulationWindow:
    def __init__(self, parent, simulator):
        self.parent = parent
        self.simulator = simulator
        self.window = None
        self.current_ticker = None
        self.chart_widget = None
        self.portfolio_widget = None
        self.daily_actions = {}
        
    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Trading Simulator")
        self.window.geometry("1400x900")
        self.window.state('zoomed')
        self.create_widgets()
        self.update_display()
        if self.simulator.tickers:
            self.current_ticker = self.simulator.tickers[0]
            self.ticker_combo.set(self.current_ticker)
            self.update_chart()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        date_frame = ttk.Frame(top_frame)
        date_frame.pack(side=tk.LEFT)
        ttk.Label(date_frame, text="DziÅ›:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        self.date_label = ttk.Label(date_frame, text="", font=("Arial", 12))
        self.date_label.pack(side=tk.LEFT, padx=(5, 20))
        
        progress_frame = ttk.Frame(top_frame)
        progress_frame.pack(side=tk.RIGHT)
        self.progress_label = ttk.Label(progress_frame, text="", font=("Arial", 10))
        self.progress_label.pack()
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(content_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
        
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(bottom_frame, text="Dni do przodu:").pack(side=tk.LEFT, padx=(0, 5))
        self.days_forward_entry = ttk.Entry(bottom_frame, width=10)
        self.days_forward_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.days_forward_entry.insert(0, "1")
        
        self.skip_days_button = ttk.Button(bottom_frame, text="Przeskocz dni", command=self.skip_days)
        self.skip_days_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.next_day_button = ttk.Button(bottom_frame, text="NastÄ™pny dzieÅ„", command=self.next_day, style="Accent.TButton")
        self.next_day_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(bottom_frame, text="Resetuj", command=self.reset_simulation).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(bottom_frame, text="WyÅ›wietl historiÄ™", command=self.show_history).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(bottom_frame, text="PokaÅ¼ wykresy", command=self.show_results).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(bottom_frame, text="PokaÅ¼ logi", command=self.show_logs_info).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(bottom_frame, text="Zamknij", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def create_left_panel(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        trading_frame = ttk.Frame(notebook)
        portfolio_frame = ttk.Frame(notebook)
        notebook.add(trading_frame, text="Trading")
        notebook.add(portfolio_frame, text="Portfolio")
        self.create_trading_tab(trading_frame)
        self.create_portfolio_tab(portfolio_frame)
    
    def create_trading_tab(self, parent):
        ttk.Label(parent, text="Select Ticker:", font=("Arial", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        self.ticker_combo = ttk.Combobox(parent, values=self.simulator.tickers, state="readonly", width=30)
        self.ticker_combo.pack(fill=tk.X, pady=(0, 15))
        self.ticker_combo.bind('<<ComboboxSelected>>', self.on_ticker_changed)
        
        predictions_frame = ttk.LabelFrame(parent, text="Prognozy", padding=10)
        predictions_frame.pack(fill=tk.X, pady=(0, 15))
        self.predictions_text = tk.Text(predictions_frame, height=8, width=40, font=("Arial", 10), state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(predictions_frame, orient=tk.VERTICAL, command=self.predictions_text.yview)
        self.predictions_text.configure(yscrollcommand=scrollbar.set)
        self.predictions_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        trading_frame = ttk.LabelFrame(parent, text="Akcje", padding=10)
        trading_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(trading_frame, text="Shares:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.shares_entry = ttk.Entry(trading_frame, width=15)
        self.shares_entry.grid(row=0, column=1, padx=(5, 0), pady=5)
        self.shares_entry.insert(0, "100")
        
        buttons_frame = ttk.Frame(trading_frame)
        buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        self.buy_button = ttk.Button(buttons_frame, text="Buy", command=self.buy_stock, style="Accent.TButton")
        self.buy_button.pack(side=tk.LEFT, padx=(0, 5))
        self.sell_button = ttk.Button(buttons_frame, text="Sell", command=self.sell_stock)
        self.sell_button.pack(side=tk.LEFT)
        
        current_price_frame = ttk.LabelFrame(parent, text="Cena", padding=10)
        current_price_frame.pack(fill=tk.X)
        self.price_label = ttk.Label(current_price_frame, text="", font=("Arial", 12, "bold"))
        self.price_label.pack()
        trading_frame.columnconfigure(1, weight=1)
    
    def create_portfolio_tab(self, parent):
        self.portfolio_widget = PortfolioWidget(parent)
        
    def create_right_panel(self, parent):
        self.chart_widget = ChartWidget(parent)
    
    def on_ticker_changed(self, event=None):
        self.current_ticker = self.ticker_combo.get()
        self.update_chart()
        self.update_current_price()
    
    def get_current_date_key(self):
        current_date = self.simulator.get_current_date()
        if current_date:
            return current_date.strftime("%Y-%m-%d")
        return None
    
    def can_buy(self):
        date_key = self.get_current_date_key()
        if date_key is None:
            return False
        
        if date_key not in self.daily_actions:
            return True
        
        actions = self.daily_actions[date_key]
        return 'SELL' not in actions
    
    def can_sell(self):
        date_key = self.get_current_date_key()
        if date_key is None:
            return False
        
        if date_key not in self.daily_actions:
            return True
        
        return True
    
    def record_action(self, action_type):
        date_key = self.get_current_date_key()
        if date_key:
            if date_key not in self.daily_actions:
                self.daily_actions[date_key] = []
            self.daily_actions[date_key].append(action_type)
    
    def update_button_states(self):
        if self.can_buy():
            self.buy_button.config(state='normal')
        else:
            self.buy_button.config(state='disabled')
        
        if self.can_sell():
            self.sell_button.config(state='normal')
        else:
            self.sell_button.config(state='disabled')
    
    def update_display(self):
        current_date = self.simulator.get_current_date()
        if current_date:
            self.date_label.config(text=current_date.strftime("%Y-%m-%d"))
        stats = self.simulator.get_simulation_stats()
        progress_text = f"DzieÅ„ {stats['current_day']} of {stats['total_days']} ({stats['progress_percentage']:.1f}%)"
        self.progress_label.config(text=progress_text)
        self.update_predictions()
        self.update_current_price()
        self.update_portfolio()
        self.update_button_states()
        if not self.simulator.can_go_next_day():
            self.next_day_button.config(state='disabled', text="Simulation Complete")
            self.skip_days_button.config(state='disabled')
    
    def update_predictions(self):
        predictions = self.simulator.current_predictions
        prices = self.simulator.current_prices
        self.predictions_text.config(state=tk.NORMAL)
        self.predictions_text.delete(1.0, tk.END)
        for ticker in self.simulator.tickers:
            prediction = predictions.get(ticker, 0)
            price = prices.get(ticker, 0)
            signal = "BUY" if prediction == 1 else "HOLD/SELL"
            self.predictions_text.insert(tk.END, f"{ticker}:\n")
            self.predictions_text.insert(tk.END, f"  Signal: {signal}\n")
            self.predictions_text.insert(tk.END, f"  Price: {format_currency(price)}\n")
            self.predictions_text.insert(tk.END, f"  Prediction: {prediction}\n\n")
        self.predictions_text.config(state=tk.DISABLED)
    
    def update_current_price(self):
        if self.current_ticker:
            price = self.simulator.current_prices.get(self.current_ticker, 0)
            self.price_label.config(text=format_currency(price))
    
    def update_portfolio(self):
        if self.portfolio_widget:
            portfolio_summary = self.simulator.get_portfolio_summary()
            self.portfolio_widget.update_display(portfolio_summary)
    
    def update_chart(self):
        if self.chart_widget and self.current_ticker:
            current_date = self.simulator.get_current_date()
            ticker_data = self.simulator.get_ticker_data_until_date(self.current_ticker, current_date)
            if ticker_data is not None and not ticker_data.empty:
                self.chart_widget.update_chart(self.current_ticker, ticker_data, current_date, self.simulator.indicators)
    
    def buy_stock(self):
        if not self.can_buy():
            messagebox.showerror("Error", "Nie można kupić akcji po sprzedaży w tym samym dniu")
            return
        
        if not self.current_ticker:
            messagebox.showwarning("Warning", "Please select a ticker")
            return
        try:
            shares = int(self.shares_entry.get())
            if shares <= 0:
                raise ValueError("Shares must be positive")
            success, message = self.simulator.buy_stock(self.current_ticker, shares)
            if success:
                self.record_action('BUY')
                self.update_button_states()
                messagebox.showinfo("Success", message)
                self.update_portfolio()
            else:
                messagebox.showerror("Error", message)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shares")
    
    def sell_stock(self):
        if not self.can_sell():
            messagebox.showerror("Error", "Brak możliwości sprzedaży")
            return
        
        if not self.current_ticker:
            messagebox.showwarning("Warning", "Please select a ticker")
            return
        try:
            shares = int(self.shares_entry.get())
            if shares <= 0:
                raise ValueError("Shares must be positive")
            success, message = self.simulator.sell_stock(self.current_ticker, shares)
            if success:
                self.record_action('SELL')
                self.update_button_states()
                messagebox.showinfo("Success", message)
                self.update_portfolio()
            else:
                messagebox.showerror("Error", message)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of shares")
    
    def skip_days(self):
        try:
            days_to_skip = int(self.days_forward_entry.get())
            if days_to_skip <= 0:
                raise ValueError("Number must be positive")
            skipped = 0
            for i in range(days_to_skip):
                if self.simulator.next_day():
                    skipped += 1
                else:
                    break
            self.update_display()
            self.update_chart()
            if skipped < days_to_skip:
                messagebox.showinfo("Info", f"Przeskoczono {skipped} dni. OsiÄ…gniÄ™to koniec symulacji.")
            else:
                messagebox.showinfo("Success", f"Przeskoczono {skipped} dni")
        except ValueError:
            messagebox.showerror("Error", "WprowadÅº poprawnÄ… liczbÄ™ dni")
    
    def next_day(self):
        if self.simulator.next_day():
            self.update_display()
            self.update_chart()
        else:
            messagebox.showinfo("Simulation Complete", "The simulation has reached the end date.")
    
    def reset_simulation(self):
        result = messagebox.askyesno("Reset Simulation", "Are you sure you want to reset the simulation?")
        if result:
            self.simulator.reset_simulation()
            self.daily_actions = {}
            self.update_display()
            self.update_chart()
            self.next_day_button.config(state='normal', text="Next Day")
            self.skip_days_button.config(state='normal')
    
    def show_results(self):
        results_window = ManualResultsWindow(self.window, self.simulator)
        results_window.show()
    
    def show_logs_info(self):
        messagebox.showinfo("Informacje o logach", "Logi w folderze 'logs'")
    
    def show_history(self):
        history_window = tk.Toplevel(self.window)
        history_window.title("Transaction History")
        history_window.geometry("800x600")
        notebook = ttk.Notebook(history_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        transactions_frame = ttk.Frame(notebook)
        performance_frame = ttk.Frame(notebook)
        notebook.add(transactions_frame, text="Transactions")
        notebook.add(performance_frame, text="Performance")
        self.create_transaction_history(transactions_frame)
        self.create_performance_history(performance_frame)
    
    def create_transaction_history(self, parent):
        tree = ttk.Treeview(parent, columns=('Date', 'Ticker', 'Action', 'Shares', 'Price', 'Total'), show='headings')
        tree.heading('Date', text='Date')
        tree.heading('Ticker', text='Ticker')
        tree.heading('Action', text='Action')
        tree.heading('Shares', text='Shares')
        tree.heading('Price', text='Price')
        tree.heading('Total', text='Total')
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        history = self.simulator.get_transaction_history()
        for _, row in history.iterrows():
            total = row.get('total_cost', row.get('net_revenue', 0))
            tree.insert('', tk.END, values=(row['date'].strftime("%Y-%m-%d"), row['ticker'], row['action'], row['shares'], format_currency(row['price']), format_currency(total)))
    
    def create_performance_history(self, parent):
        tree = ttk.Treeview(parent, columns=('Date', 'Portfolio Value', 'Return %'), show='headings')
        tree.heading('Date', text='Date')
        tree.heading('Portfolio Value', text='Portfolio Value')
        tree.heading('Return %', text='Return %')
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        performance = self.simulator.get_performance_history()
        for _, row in performance.iterrows():
            tree.insert('', tk.END, values=(row['date'].strftime("%Y-%m-%d"), format_currency(row['value']), format_percentage(row['return'])))