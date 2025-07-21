import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from config import CHART_COLORS

class ChartWidget:
    def __init__(self, parent):
        self.parent = parent
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.current_data = None
        self.current_ticker = None
        self.current_indicators = []
        self.current_date = None  
        
        self.create_widget()
        
    def create_widget(self):
        chart_frame = ttk.LabelFrame(self.parent, text="Price Chart & Technical Indicators", padding=5)
        chart_frame.pack(fill=tk.BOTH, expand=True)
        
        controls_frame = ttk.Frame(chart_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(controls_frame, text="Chart Period:").pack(side=tk.LEFT)
        self.period_combo = ttk.Combobox(controls_frame, values=['30 days', '60 days', '90 days', '180 days', 'All'], 
                                        state="readonly", width=15)
        self.period_combo.set('90 days')
        self.period_combo.pack(side=tk.LEFT, padx=(5, 15))
        self.period_combo.bind('<<ComboboxSelected>>', self.on_period_changed)
        
        ttk.Label(controls_frame, text="Indicators:").pack(side=tk.LEFT)
        self.indicators_frame = ttk.Frame(controls_frame)
        self.indicators_frame.pack(side=tk.LEFT, padx=(5, 0))
        
        self.indicator_vars = {}
        
        self.figure = Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, chart_frame)
        self.toolbar.update()
    
    def create_indicator_checkboxes(self, indicators):
        for widget in self.indicators_frame.winfo_children():
            widget.destroy()
        
        self.indicator_vars = {}
        
        chart_indicators = ['SMA', 'EMA', 'Bollinger Bands', 'RSI', 'MACD', 'Volume']
        available_indicators = [ind for ind in chart_indicators if ind in indicators or 
                               any(ind.lower() in indicator.lower() for indicator in indicators)]
        
        for i, indicator in enumerate(available_indicators):
            var = tk.BooleanVar()
            self.indicator_vars[indicator] = var
            
            cb = ttk.Checkbutton(self.indicators_frame, text=indicator, variable=var,
                               command=self.on_indicator_changed)
            cb.pack(side=tk.LEFT, padx=2)
            
            if indicator in ['SMA', 'EMA']:
                var.set(True)
    
    def on_period_changed(self, event=None):
        self.update_chart(self.current_ticker, self.current_data, self.current_date, self.current_indicators)
    
    def on_indicator_changed(self):
        self.update_chart(self.current_ticker, self.current_data, self.current_date, self.current_indicators)
    
    def get_period_days(self):
        period_map = {
            '30 days': 30,
            '60 days': 60,
            '90 days': 90,
            '180 days': 180,
            'All': None
        }
        return period_map.get(self.period_combo.get(), 90)
    
    def filter_data_by_period(self, data, current_date):
        if data is None or data.empty:
            return data
            
        if current_date is not None:
            current_date = pd.to_datetime(current_date)
            
            if 'Date' in data.columns:
                data = data[data['Date'] <= current_date]
            else:
                data = data[data.index <= current_date]
        
        period_days = self.get_period_days()
        if period_days is None:
            return data
        
        if current_date is not None:
            start_date = current_date - pd.Timedelta(days=period_days)
            
            if 'Date' in data.columns:
                filtered_data = data[data['Date'] >= start_date]
            else:
                filtered_data = data[data.index >= start_date]
            
            return filtered_data.tail(period_days)
        
        return data.tail(period_days)
    
    def update_chart(self, ticker, data, current_date, indicators):
        if data is None or data.empty:
            return
        
        self.current_ticker = ticker
        self.current_data = data
        self.current_date = current_date 
        self.current_indicators = indicators
        
        if not self.indicator_vars:
            self.create_indicator_checkboxes(indicators)
        
        filtered_data = self.filter_data_by_period(data, current_date)
        
        if filtered_data is None or filtered_data.empty:
            self.figure.clear()
            self.canvas.draw()
            return
        
        self.figure.clear()
        
        selected_indicators = [ind for ind, var in self.indicator_vars.items() if var.get()]
        
        has_oscillators = any(ind in selected_indicators for ind in ['RSI', 'MACD'])
        
        if has_oscillators:
            gs = self.figure.add_gridspec(3, 1, height_ratios=[3, 1, 1], hspace=0.3)
            ax1 = self.figure.add_subplot(gs[0])
            ax2 = self.figure.add_subplot(gs[1])
            ax3 = self.figure.add_subplot(gs[2])
        else:
            gs = self.figure.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.3)
            ax1 = self.figure.add_subplot(gs[0])
            ax2 = self.figure.add_subplot(gs[1])
            ax3 = None
        
        dates = filtered_data.index if 'Date' not in filtered_data.columns else filtered_data['Date']
        
        ax1.plot(dates, filtered_data['Close'], label='Close Price', 
                color=CHART_COLORS['price'], linewidth=1.5)
        
        if 'SMA' in selected_indicators:
            for col in filtered_data.columns:
                if 'SMA' in col:
                    ax1.plot(dates, filtered_data[col], label=col, 
                            color=CHART_COLORS['sma'], alpha=0.7)
        
        if 'EMA' in selected_indicators:
            for col in filtered_data.columns:
                if 'EMA' in col:
                    ax1.plot(dates, filtered_data[col], label=col, 
                            color=CHART_COLORS['ema'], alpha=0.7)
        
        if 'Bollinger Bands' in selected_indicators:
            if 'BB_Upper' in filtered_data.columns:
                ax1.plot(dates, filtered_data['BB_Upper'], label='BB Upper', 
                        color=CHART_COLORS['bollinger_upper'], alpha=0.6)
                ax1.plot(dates, filtered_data['BB_Middle'], label='BB Middle', 
                        color=CHART_COLORS['bollinger_middle'], alpha=0.6)
                ax1.plot(dates, filtered_data['BB_Lower'], label='BB Lower', 
                        color=CHART_COLORS['bollinger_lower'], alpha=0.6)
                ax1.fill_between(dates, filtered_data['BB_Upper'], filtered_data['BB_Lower'], 
                               alpha=0.1, color=CHART_COLORS['bollinger_upper'])
        
        if current_date and current_date in dates.values if hasattr(dates, 'values') else current_date in dates:
            ax1.axvline(x=current_date, color='red', linestyle='--', alpha=0.7, label='Current Date')
        
        ax1.set_title(f'{ticker} - Price Chart', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=10)
        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.3)
        
        if 'Volume' in selected_indicators and 'Volume' in filtered_data.columns:
            ax2.bar(dates, filtered_data['Volume'], alpha=0.6, color=CHART_COLORS['volume'])
            ax2.set_ylabel('Volume', fontsize=10)
            ax2.set_title('Volume', fontsize=12)
            ax2.grid(True, alpha=0.3)
        
        oscillator_ax = ax3 if ax3 is not None else ax2
        
        if 'RSI' in selected_indicators and 'RSI_14' in filtered_data.columns:
            if ax3 is not None:
                ax2.plot(dates, filtered_data['RSI_14'], label='RSI(14)', 
                        color=CHART_COLORS['rsi'], linewidth=1.5)
                ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5)
                ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5)
                ax2.set_ylabel('RSI', fontsize=10)
                ax2.set_title('RSI (14)', fontsize=12)
                ax2.set_ylim(0, 100)
                ax2.grid(True, alpha=0.3)
        
        if 'MACD' in selected_indicators and 'MACD' in filtered_data.columns:
            if ax3 is not None:
                ax3.plot(dates, filtered_data['MACD'], label='MACD', 
                        color=CHART_COLORS['macd'], linewidth=1.5)
                if 'MACD_Signal' in filtered_data.columns:
                    ax3.plot(dates, filtered_data['MACD_Signal'], label='Signal', 
                            color=CHART_COLORS['macd_signal'], linewidth=1.5)
                if 'MACD_Hist' in filtered_data.columns:
                    ax3.bar(dates, filtered_data['MACD_Hist'], alpha=0.3, 
                           color='gray', label='Histogram')
                ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                ax3.set_ylabel('MACD', fontsize=10)
                ax3.set_title('MACD', fontsize=12)
                ax3.legend(loc='upper left', fontsize=8)
                ax3.grid(True, alpha=0.3)
        
        if not has_oscillators and 'Volume' not in selected_indicators:
            ax2.remove()
        
        self.figure.suptitle(f'{ticker} Technical Analysis', fontsize=16, fontweight='bold')
        
        plt.setp(self.figure.get_axes()[-1].xaxis.get_majorticklabels(), rotation=45)
        
        self.canvas.draw()