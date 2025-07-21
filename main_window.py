import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from config import AVAILABLE_MODELS, AVAILABLE_INDICATORS, DEFAULT_SETTINGS
from utils import validate_date_format, validate_date_range, validate_tickers, validate_numeric_input
from simulation_window import SimulationWindow
from agent_window import AgentWindow
from trading_simulator import TradingSimulator
import threading

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trading Simulator - Configuration")
        self.root.geometry("700x850")  
        self.root.resizable(False, False)
        
        self.simulator = None          
        self.create_widgets()
        self.load_defaults()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text="Trading Simulator Configuration", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        config_section = ttk.LabelFrame(main_frame, text="Podstawowa konfiguracja", padding=10)
        config_section.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(config_section, text="Tickers (comma separated):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tickers_entry = ttk.Entry(config_section, width=50)
        self.tickers_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_section, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.start_date_entry = ttk.Entry(config_section, width=50)
        self.start_date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_section, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.end_date_entry = ttk.Entry(config_section, width=50)
        self.end_date_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_section, text="Model Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.model_combo = ttk.Combobox(config_section, values=list(AVAILABLE_MODELS.keys()), 
                                       state="readonly", width=47)
        self.model_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_section, text="Commission Rate (0.001 = 0.1%):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.commission_entry = ttk.Entry(config_section, width=50)
        self.commission_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_section, text="Days Ahead:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.days_ahead_entry = ttk.Entry(config_section, width=50)
        self.days_ahead_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(config_section, text="Initial Capital:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.capital_entry = ttk.Entry(config_section, width=50)
        self.capital_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        config_section.columnconfigure(1, weight=1)
        
        features_section = ttk.LabelFrame(main_frame, text="Cechy cenowe (musisz wybrać przynajmniej jedną)", padding=10)
        features_section.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        features_frame = ttk.Frame(features_section)
        features_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.price_feature_vars = {}
        price_features = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        for i, feature in enumerate(price_features):
            var = tk.BooleanVar()
            self.price_feature_vars[feature] = var
            
            cb = ttk.Checkbutton(features_frame, text=feature, variable=var)
            cb.grid(row=0, column=i, sticky=tk.W, padx=10, pady=2)
           
            if feature == 'Close':
                var.set(True)
        
        indicators_section = ttk.LabelFrame(main_frame, text="Wskaźniki techniczne", padding=10)
        indicators_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        indicators_frame = ttk.Frame(indicators_section)
        indicators_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.indicator_vars = {}
        for i, indicator in enumerate(AVAILABLE_INDICATORS):
            var = tk.BooleanVar()
            self.indicator_vars[indicator] = var
            
            row = i // 3
            col = i % 3
            
            cb = ttk.Checkbutton(indicators_frame, text=indicator, variable=var)
            cb.grid(row=row, column=col, sticky=tk.W, padx=5, pady=2)
        
        main_buttons_frame = ttk.LabelFrame(main_frame, text="Tryby symulacji", padding=15)
        main_buttons_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        manual_frame = ttk.Frame(main_buttons_frame)
        manual_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.manual_button = ttk.Button(manual_frame, text="Symulacja manualna", 
                                       command=self.start_manual_simulation, 
                                       style="Accent.TButton")
        self.manual_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(manual_frame, text="Kontroluj każdą transakcję samodzielnie", 
                 foreground="gray").pack(side=tk.LEFT)

        ttk.Separator(main_buttons_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        agent_frame = ttk.Frame(main_buttons_frame)
        agent_frame.pack(fill=tk.X)
        
        self.agent_button = ttk.Button(agent_frame, text="Symulacja agenta", 
                                      command=self.start_agent_simulation,
                                      style="Accent.TButton")
        self.agent_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(agent_frame, text="Automatyczna symulacja z wyborem strategii", 
                 foreground="gray").pack(side=tk.LEFT)
        
        utility_buttons_frame = ttk.Frame(main_frame)
        utility_buttons_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(utility_buttons_frame, text="Reset to Defaults", 
                  command=self.load_defaults).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(utility_buttons_frame, text="Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        progress_section = ttk.LabelFrame(main_frame, text="Status", padding=10)
        progress_section.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        self.progress_var = tk.StringVar()
        self.progress_label = ttk.Label(progress_section, textvariable=self.progress_var)
        self.progress_label.pack(pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(progress_section, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)
        
        main_frame.columnconfigure(1, weight=1)
        
    def load_defaults(self):
        self.tickers_entry.delete(0, tk.END)
        self.tickers_entry.insert(0, "AAPL,GOOGL,MSFT")
        
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, DEFAULT_SETTINGS['start_date'])
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, DEFAULT_SETTINGS['end_date'])
        
        self.model_combo.set(list(AVAILABLE_MODELS.keys())[0])
        
        self.commission_entry.delete(0, tk.END)
        self.commission_entry.insert(0, str(DEFAULT_SETTINGS['commission']))
        
        self.days_ahead_entry.delete(0, tk.END)
        self.days_ahead_entry.insert(0, str(DEFAULT_SETTINGS['days_ahead']))
        
        self.capital_entry.delete(0, tk.END)
        self.capital_entry.insert(0, str(DEFAULT_SETTINGS['initial_capital']))
        
        for var in self.indicator_vars.values():
            var.set(False)
        
        for var in self.price_feature_vars.values():
            var.set(False)
            
        self.price_feature_vars['Close'].set(True)
        
        default_indicators = ['SMA', 'EMA', 'RSI', 'MACD']
        for indicator in default_indicators:
            if indicator in self.indicator_vars:
                self.indicator_vars[indicator].set(True)
    
    def validate_inputs(self):
        if not validate_date_format(self.start_date_entry.get()):
            messagebox.showerror("Error", "Invalid start date format. Use YYYY-MM-DD")
            return False
        
        if not validate_date_format(self.end_date_entry.get()):
            messagebox.showerror("Error", "Invalid end date format. Use YYYY-MM-DD")
            return False
        
        if not validate_date_range(self.start_date_entry.get(), self.end_date_entry.get()):
            messagebox.showerror("Error", "Start date must be before end date")
            return False
        
        is_valid, result = validate_tickers(self.tickers_entry.get())
        if not is_valid:
            messagebox.showerror("Error", result)
            return False
        
        if not validate_numeric_input(self.commission_entry.get(), 0, 1):
            messagebox.showerror("Error", "Commission rate must be a number between 0 and 1")
            return False
        
        if not validate_numeric_input(self.days_ahead_entry.get(), 1, 30):
            messagebox.showerror("Error", "Days ahead must be a number between 1 and 30")
            return False
        
        if not validate_numeric_input(self.capital_entry.get(), 1000):
            messagebox.showerror("Error", "Initial capital must be at least 1000")
            return False
        
        if not self.model_combo.get():
            messagebox.showerror("Error", "Please select a model type")
            return False
        
        selected_indicators = [indicator for indicator, var in self.indicator_vars.items() if var.get()]
        if not selected_indicators:
            messagebox.showerror("Error", "Please select at least one technical indicator")
            return False
        
        selected_features = [feature for feature, var in self.price_feature_vars.items() if var.get()]
        if not selected_features:
            messagebox.showerror("Error", "Musisz wybrać przynajmniej jedną cechę cenową")
            return False
        
        if 'Close' not in selected_features:
            messagebox.showerror("Error", "Cena zamknięcia (Close) jest wymagana")
            return False
        
        return True
    
    def get_configuration(self):
        is_valid, tickers = validate_tickers(self.tickers_entry.get())
        selected_indicators = [indicator for indicator, var in self.indicator_vars.items() if var.get()]
        selected_features = [feature for feature, var in self.price_feature_vars.items() if var.get()]
        
        return {
            'tickers': tickers,
            'start_date': self.start_date_entry.get(),
            'end_date': self.end_date_entry.get(),
            'model_type': self.model_combo.get(),
            'commission': float(self.commission_entry.get()),
            'days_ahead': int(self.days_ahead_entry.get()),
            'initial_capital': float(self.capital_entry.get()),
            'indicators': selected_indicators,
            'selected_features': selected_features
        }
    
    def setup_simulator(self, config):
        self.progress_var.set("Initializing simulator...")
        self.progress_bar.start()
        
        simulator = TradingSimulator(
            tickers=config['tickers'],
            start_date=config['start_date'],
            end_date=config['end_date'],
            model_type=config['model_type'],
            commission=config['commission'],
            days_ahead=config['days_ahead'],
            initial_capital=config['initial_capital'],
            indicators=config['indicators'],
            selected_features=config['selected_features']  
        )
        
        self.progress_var.set("Loading data...")
        simulator.setup()
        
        self.progress_var.set("Training models...")
        simulator.train_models()
        
        self.progress_var.set("Getting initial predictions...")
        simulator.get_predictions_for_current_date()
        
        return simulator
    
    def start_manual_simulation(self):
        if not self.validate_inputs():
            return
        
        config = self.get_configuration()
        
        self.manual_button.config(state='disabled')
        self.agent_button.config(state='disabled')
        
        def setup_manual_simulation():
            try:
                simulator = self.setup_simulator(config)
                self.simulator = simulator  
                
                def open_manual_window():
                    self.progress_bar.stop()
                    self.progress_var.set("Manual simulation ready!")
                    self.manual_button.config(state='normal')
                    self.agent_button.config(state='normal')
                    
                    simulation_window = SimulationWindow(self.root, simulator)
                    simulation_window.show()
                
                self.root.after(0, open_manual_window)
                
            except Exception as e:
                error_msg = str(e)
                def show_error():
                    self.progress_bar.stop()
                    self.progress_var.set("Error occurred")
                    self.manual_button.config(state='normal')
                    self.agent_button.config(state='normal')
                    messagebox.showerror("Setup Error", f"Failed to setup simulation:\n{error_msg}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=setup_manual_simulation, daemon=True).start()
    
    def start_agent_simulation(self):
        if not self.validate_inputs():
            return
        
        if self.simulator and self.simulator.is_trained:
            agent_window = AgentWindow(self.root, self.simulator)
            agent_window.show()
            return
        
        config = self.get_configuration()
        
        self.manual_button.config(state='disabled')
        self.agent_button.config(state='disabled')
        
        def setup_agent_simulation():
            try:
                simulator = self.setup_simulator(config)
                self.simulator = simulator  
                
                def open_agent_window():
                    self.progress_bar.stop()
                    self.progress_var.set("Agent simulation ready!")
                    self.manual_button.config(state='normal')
                    self.agent_button.config(state='normal')
                    
                    agent_window = AgentWindow(self.root, simulator)
                    agent_window.show()
                
                self.root.after(0, open_agent_window)
                
            except Exception as e:
                error_msg = str(e)
                def show_error():
                    self.progress_bar.stop()
                    self.progress_var.set("Error occurred")
                    self.manual_button.config(state='normal')
                    self.agent_button.config(state='normal')
                    messagebox.showerror("Setup Error", f"Failed to setup simulation:\n{error_msg}")
                
                self.root.after(0, show_error)
        
        threading.Thread(target=setup_agent_simulation, daemon=True).start()
    
    def run(self):
        self.root.mainloop()