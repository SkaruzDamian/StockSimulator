import tkinter as tk
from tkinter import ttk, messagebox
import threading
from agent_simulation import AgentSimulation, BasicStrategy, AggressiveStrategy, ConservativeStrategy
from agent_results_window import AgentResultsWindow
from strategy_comparison import StrategyComparison
from strategy_comparison_window import StrategyComparisonWindow
from utils import format_currency, format_percentage

class AgentWindow:
    def __init__(self, parent, trading_simulator):
        self.parent = parent
        self.trading_simulator = trading_simulator
        self.window = None
        self.agent_simulation = None
        self.comparison = None
        
        self.strategies = {
            "Basic Strategy": BasicStrategy(),
            "Aggressive Strategy": AggressiveStrategy(),
            "Conservative Strategy": ConservativeStrategy()
        }
        
        self.progress_var = None
        self.progress_bar = None
        self.status_label = None
        self.simulation_thread = None
        
    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Agent Simulation")
        self.window.geometry("800x500")
        self.window.resizable(True, True)
        self.create_widgets()
        self.update_progress()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Agent Simulation", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        config_frame = ttk.LabelFrame(main_frame, text="Konfiguracja", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(config_frame, text="Strategia inwestycyjna:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.strategy_combo = ttk.Combobox(config_frame, values=list(self.strategies.keys()), state="readonly", width=30)
        self.strategy_combo.set("Basic Strategy")
        self.strategy_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        self.strategy_desc_label = ttk.Label(config_frame, text="", wraplength=500, foreground="gray")
        self.strategy_desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.strategy_combo.bind('<<ComboboxSelected>>', self.update_strategy_description)
        self.update_strategy_description()
        
        info_text = f"""
    Parametry symulacji:
    - KapitaÅ‚ poczÄ…tkowy: {format_currency(self.trading_simulator.initial_capital)}
    - Prowizja: {self.trading_simulator.commission*100:.2f}%
    - Dni do przodu: {self.trading_simulator.days_ahead}
    - SpÃ³Å‚ki: {', '.join(self.trading_simulator.tickers)}
    - Okres: {self.trading_simulator.start_date.strftime('%Y-%m-%d')} - {self.trading_simulator.end_date.strftime('%Y-%m-%d')}
        """
        
        info_label = ttk.Label(config_frame, text=info_text.strip(), foreground="blue")
        info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        config_frame.columnconfigure(1, weight=1)
        
        control_frame = ttk.LabelFrame(main_frame, text="Kontrola", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(buttons_frame, text="Rozpocznij symulacjÄ™", command=self.start_simulation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.compare_button = ttk.Button(buttons_frame, text="PorÃ³wnaj wszystkie strategie", command=self.start_comparison, style="Accent.TButton")
        self.compare_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame, text="Zatrzymaj", command=self.stop_simulation, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="PokaÅ¼ logi agenta", command=self.show_agent_logs).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Zamknij", command=self.window.destroy).pack(side=tk.RIGHT)
    
    def update_strategy_description(self, event=None):
        selected_strategy = self.strategy_combo.get()
        if selected_strategy in self.strategies:
            description = self.strategies[selected_strategy].description
            self.strategy_desc_label.config(text=description)
    
    def progress_callback(self, current_day, total_days, progress):
        pass
    
    def start_simulation(self):
        if self.simulation_thread and self.simulation_thread.is_alive():
            messagebox.showwarning("Uwaga", "Symulacja już trwa!")
            return
        
        selected_strategy_name = self.strategy_combo.get()
        selected_strategy = self.strategies[selected_strategy_name]
        
        self.agent_simulation = AgentSimulation(self.trading_simulator, selected_strategy, self.progress_callback)
        self.simulation_thread = threading.Thread(target=self.run_simulation_thread, daemon=True)
        self.simulation_thread.start()
        
        self.start_button.config(state="disabled")
        self.compare_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.strategy_combo.config(state="disabled")
        self.status_label.config(text="Rozpoczynanie symulacji...")
    
    def run_simulation_thread(self):
        try:
            success, message = self.agent_simulation.run_simulation()
            
            def update_ui_after_completion():
                self.start_button.config(state="normal")
                self.compare_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.strategy_combo.config(state="readonly")
                
                if success:
                    result = messagebox.askyesno("Sukces", f"{message}\n\nCzy chcesz zobaczyć wykresy wyników?")
                    if result:
                        self.show_results_window()
                else:
                    messagebox.showerror("Błąd", message)
            
            self.window.after(0, update_ui_after_completion)
            
        except Exception as e:
            def show_error():
                self.start_button.config(state="normal")
                self.compare_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.strategy_combo.config(state="readonly")
                messagebox.showerror("Błąd", f"Nieoczekiwany błąd: {str(e)}")
            self.window.after(0, show_error)
        
    def start_comparison(self):
        if self.simulation_thread and self.simulation_thread.is_alive():
            messagebox.showwarning("Uwaga", "Symulacja już trwa!")
            return
        
        self.comparison = StrategyComparison(self.trading_simulator, self.progress_callback)
        self.simulation_thread = threading.Thread(target=self.run_comparison_thread, daemon=True)
        self.simulation_thread.start()
        
        self.start_button.config(state="disabled")
        self.compare_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.strategy_combo.config(state="disabled")
        self.status_label.config(text="Rozpoczynanie porównania strategii...")
    
    def run_comparison_thread(self):
        try:
            results = self.comparison.run_comparison()
            
            def update_ui_after_completion():
                self.start_button.config(state="normal")
                self.compare_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.strategy_combo.config(state="readonly")
                
                result = messagebox.askyesno("Sukces", "Porównanie strategii zakończone!\n\nCzy chcesz zobaczyć wyniki?")
                if result:
                    self.show_comparison_window(results)
            
            self.window.after(0, update_ui_after_completion)
            
        except Exception as e:
            def show_error():
                self.start_button.config(state="normal")
                self.compare_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.strategy_combo.config(state="readonly")
                messagebox.showerror("Błąd", f"Nieoczekiwany błąd: {str(e)}")
            self.window.after(0, show_error)
    
    def show_results_window(self):
        results_window = AgentResultsWindow(self.window, self.agent_simulation)
        results_window.show()
    
    def show_comparison_window(self, results):
        comparison_window = StrategyComparisonWindow(self.window, results)
        comparison_window.show()
    
    def stop_simulation(self):
        messagebox.showinfo("Info", "Symulacja zostanie zatrzymana po zakończeniu bieżącego dnia.")
    
    def show_agent_logs(self):
        log_info = """Logi agenta zostały zapisane w folderze 'agent_logs':

📁 agent_logs/
├── transactions_[timestamp].txt - Transakcje agenta
├── model_performance_[timestamp].txt - Skuteczność modelu
├── daily_portfolio_[timestamp].txt - Dzienny stan portfolio
└── simulation_summary_[timestamp].txt - Podsumowanie symulacji

Logi są automatycznie aktualizowane podczas symulacji.
Szczegółowe podsumowanie zostanie zapisane po zakończeniu."""
        messagebox.showinfo("Logi agenta", log_info)
    
    def update_progress(self):
        if self.window and self.window.winfo_exists():
            self.window.after(1000, self.update_progress)