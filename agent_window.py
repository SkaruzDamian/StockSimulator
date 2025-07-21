import tkinter as tk
from tkinter import ttk, messagebox
import threading
from agent_simulation import AgentSimulation, BasicStrategy, AggressiveStrategy, ConservativeStrategy
from utils import format_currency, format_percentage

class AgentWindow:
    def __init__(self, parent, trading_simulator):
        self.parent = parent
        self.trading_simulator = trading_simulator
        self.window = None
        self.agent_simulation = None
        
        self.strategies = {
            "Basic Strategy": BasicStrategy(),
            "Aggressive Strategy": AggressiveStrategy(),
            "Conservative Strategy": ConservativeStrategy()
        }
        
        self.progress_var = None
        self.progress_bar = None
        self.status_label = None
        self.stats_frame = None
        
        self.simulation_thread = None
        
    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Agent Simulation")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        self.create_widgets()
        self.update_display()
        
        self.update_progress()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Agent Simulation", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        config_frame = ttk.LabelFrame(main_frame, text="Konfiguracja", padding=15)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(config_frame, text="Strategia inwestycyjna:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.strategy_combo = ttk.Combobox(config_frame, values=list(self.strategies.keys()), 
                                          state="readonly", width=30)
        self.strategy_combo.set("Basic Strategy")
        self.strategy_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
    
        self.strategy_desc_label = ttk.Label(config_frame, text="", wraplength=500, foreground="gray")
        self.strategy_desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.strategy_combo.bind('<<ComboboxSelected>>', self.update_strategy_description)
        self.update_strategy_description()
       
        info_text = f"""
Parametry symulacji:
• Kapitał początkowy: {format_currency(self.trading_simulator.initial_capital)}
• Prowizja: {self.trading_simulator.commission*100:.2f}%
• Dni do przodu: {self.trading_simulator.days_ahead}
• Spółki: {', '.join(self.trading_simulator.tickers)}
• Okres: {self.trading_simulator.start_date.strftime('%Y-%m-%d')} - {self.trading_simulator.end_date.strftime('%Y-%m-%d')}
        """
        
        info_label = ttk.Label(config_frame, text=info_text.strip(), foreground="blue")
        info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        config_frame.columnconfigure(1, weight=1)
        
        control_frame = ttk.LabelFrame(main_frame, text="Kontrola", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        buttons_frame = ttk.Frame(control_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(buttons_frame, text="Rozpocznij symulację", 
                                      command=self.start_simulation, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(buttons_frame, text="Zatrzymaj", 
                                     command=self.stop_simulation, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Pokaż logi agenta", 
                  command=self.show_agent_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Zamknij", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
    
        progress_frame = ttk.LabelFrame(main_frame, text="Postęp symulacji", padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.status_label = ttk.Label(progress_frame, text="Symulacja nie została rozpoczęta")
        self.status_label.pack(pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_text = ttk.Label(progress_frame, text="0%")
        self.progress_text.pack()
        
        self.stats_frame = ttk.LabelFrame(main_frame, text="Statystyki na żywo", padding=15)
        self.stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_stats_display()
    
    def create_stats_display(self):
        left_frame = ttk.Frame(self.stats_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        ttk.Label(left_frame, text="Wyniki finansowe:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.portfolio_value_label = ttk.Label(left_frame, text="Wartość portfolio: $0.00")
        self.portfolio_value_label.pack(anchor=tk.W, pady=2)
        
        self.return_label = ttk.Label(left_frame, text="Zwrot: $0.00 (0.00%)")
        self.return_label.pack(anchor=tk.W, pady=2)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(left_frame, text="Aktywność:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.transactions_label = ttk.Label(left_frame, text="Transakcje: 0")
        self.transactions_label.pack(anchor=tk.W, pady=2)
        
        self.positions_label = ttk.Label(left_frame, text="Otwarte pozycje: 0")
        self.positions_label.pack(anchor=tk.W, pady=2)
        
        right_frame = ttk.Frame(self.stats_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="Skuteczność modelu:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.accuracy_label = ttk.Label(right_frame, text="Dokładność: 0.00%")
        self.accuracy_label.pack(anchor=tk.W, pady=2)
        
        ttk.Separator(right_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(right_frame, text="Status:", font=("Arial", 11, "bold")).pack(anchor=tk.W)
        
        self.agent_status_label = ttk.Label(right_frame, text="Gotowy do startu")
        self.agent_status_label.pack(anchor=tk.W, pady=2)
    
    def update_strategy_description(self, event=None):
        selected_strategy = self.strategy_combo.get()
        if selected_strategy in self.strategies:
            description = self.strategies[selected_strategy].description
            self.strategy_desc_label.config(text=description)
    
    def update_display(self):
        if self.agent_simulation:
            stats = self.agent_simulation.get_current_stats()
            
            self.portfolio_value_label.config(text=f"Wartość portfolio: {format_currency(stats['portfolio_value'])}")
            
            return_text = f"Zwrot: {format_currency(stats['return'])} ({format_percentage(stats['return_pct'])})"
            if stats['return'] > 0:
                self.return_label.config(text=return_text, foreground='green')
            elif stats['return'] < 0:
                self.return_label.config(text=return_text, foreground='red')
            else:
                self.return_label.config(text=return_text, foreground='black')
            
            self.transactions_label.config(text=f"Transakcje: {stats['transactions']}")
            self.positions_label.config(text=f"Otwarte pozycje: {stats['positions']}")
            
            self.accuracy_label.config(text=f"Dokładność: {stats['accuracy']:.2f}%")
            
            progress_info = self.agent_simulation.get_progress_info()
            self.agent_status_label.config(text=progress_info)
    
    def progress_callback(self, current_day, total_days, progress):
        def update_ui():
            self.progress_var.set(progress)
            self.progress_text.config(text=f"{progress:.1f}%")
            self.status_label.config(text=f"Dzień {current_day} z {total_days}")
            self.update_display()
        
        self.window.after(0, update_ui)
    
    def start_simulation(self):
        if self.simulation_thread and self.simulation_thread.is_alive():
            messagebox.showwarning("Uwaga", "Symulacja już trwa!")
            return
        
        selected_strategy_name = self.strategy_combo.get()
        selected_strategy = self.strategies[selected_strategy_name]
        
        self.agent_simulation = AgentSimulation(
            self.trading_simulator,
            selected_strategy,
            self.progress_callback
        )
        
        self.simulation_thread = threading.Thread(target=self.run_simulation_thread, daemon=True)
        self.simulation_thread.start()
        
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.strategy_combo.config(state="disabled")
        self.status_label.config(text="Rozpoczynanie symulacji...")
    
    def run_simulation_thread(self):
        try:
            success, message = self.agent_simulation.run_simulation()
            
            def update_ui_after_completion():
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.strategy_combo.config(state="readonly")
                
                if success:
                    self.status_label.config(text="Symulacja zakończona pomyślnie!")
                    self.progress_var.set(100)
                    self.progress_text.config(text="100%")
                    messagebox.showinfo("Sukces", f"{message}\n\nSprawdź folder 'agent_logs' dla szczegółowych wyników.")
                else:
                    self.status_label.config(text="Błąd podczas symulacji")
                    messagebox.showerror("Błąd", message)
                
                self.update_display()
            
            self.window.after(0, update_ui_after_completion)
            
        except Exception as e:
            def show_error():
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.strategy_combo.config(state="readonly")
                self.status_label.config(text="Błąd podczas symulacji")
                messagebox.showerror("Błąd", f"Nieoczekiwany błąd: {str(e)}")
            
            self.window.after(0, show_error)
    
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
        """Periodyczna aktualizacja postępu"""
        if self.window and self.window.winfo_exists():
            self.update_display()
            self.window.after(1000, self.update_progress)