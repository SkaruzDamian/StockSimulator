import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
from utils import format_currency, format_percentage

class StrategyComparisonWindow:
    def __init__(self, parent, comparison_results):
        self.parent = parent
        self.comparison_results = comparison_results
        self.window = None
        
    def show(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Porównanie Strategii")
        self.window.geometry("1400x900")
        self.window.state('zoomed')
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Porównanie Strategii Inwestycyjnych", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        chart_frame = ttk.Frame(main_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.create_comparison_chart(chart_frame)
        
        summary_frame = ttk.LabelFrame(main_frame, text="Podsumowanie Wyników", padding=15)
        summary_frame.pack(fill=tk.X)
        
        self.create_summary_table(summary_frame)
        
    def create_comparison_chart(self, parent):
        figure = Figure(figsize=(14, 8))
        ax = figure.add_subplot(111)
        
        colors = {
            'Basic Strategy': '#1f77b4',
            'Aggressive Strategy': '#d62728',
            'Conservative Strategy': '#2ca02c'
        }
        
        initial_capital = None
        
        for strategy_name, result in self.comparison_results.items():
            if result is None:
                continue
                
            daily_values = result['daily_portfolio_value']
            if not daily_values:
                continue
            
            df = pd.DataFrame(daily_values)
            dates = pd.to_datetime(df['date'])
            values = df['value']
            
            if initial_capital is None:
                initial_capital = result['initial_capital']
            
            ax.plot(dates, values, linewidth=2, 
                   color=colors.get(strategy_name, '#000000'), 
                   label=strategy_name)
        
        if initial_capital is not None:
            ax.axhline(y=initial_capital, color='black', linestyle='--', 
                      linewidth=2, label='Kapitał początkowy', alpha=0.7)
        
        ax.set_title('Porównanie Wartości Portfolio w Czasie', fontsize=16, fontweight='bold')
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Wartość Portfolio ($)', fontsize=12)
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        figure.autofmt_xdate()
        
        canvas = FigureCanvasTkAgg(figure, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, parent)
        toolbar.update()
        
    def create_summary_table(self, parent):
        columns = ('Strategia', 'Kapitał początkowy', 'Wartość końcowa', 
                  'Zwrot ($)', 'Zwrot (%)', 'Transakcje', 'Dokładność (%)')
        
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=4)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == 'Strategia':
                tree.column(col, width=180, anchor=tk.W)
            else:
                tree.column(col, width=140, anchor=tk.CENTER)
        
        for strategy_name, result in self.comparison_results.items():
            if result is None:
                tree.insert('', tk.END, values=(
                    strategy_name, 'BŁĄD', 'BŁĄD', 'BŁĄD', 'BŁĄD', 'BŁĄD', 'BŁĄD'
                ))
                continue
            
            stats = result['stats']
            initial_capital = result['initial_capital']
            final_value = stats.get('final_portfolio_value', initial_capital)
            total_return = stats.get('total_return', 0)
            return_pct = stats.get('return_percentage', 0)
            transactions = stats.get('total_transactions', 0)
            accuracy = stats.get('accuracy', 0)
            
            tree.insert('', tk.END, values=(
                strategy_name,
                format_currency(initial_capital),
                format_currency(final_value),
                format_currency(total_return),
                format_percentage(return_pct),
                transactions,
                f"{accuracy:.2f}%"
            ))
        
        tree.pack(fill=tk.X, expand=True)