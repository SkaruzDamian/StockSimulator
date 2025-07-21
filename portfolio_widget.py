import tkinter as tk
from tkinter import ttk
from utils import format_currency, format_percentage

class PortfolioWidget:
    def __init__(self, parent):
        self.parent = parent
        self.create_widget()
        
    def create_widget(self):
        summary_frame = ttk.LabelFrame(self.parent, text="Portfolio Summary", padding=10)
        summary_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cash_label = ttk.Label(summary_frame, text="Cash: $0.00", font=("Arial", 11))
        self.cash_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.total_value_label = ttk.Label(summary_frame, text="Total Value: $0.00", 
                                          font=("Arial", 11, "bold"))
        self.total_value_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.total_return_label = ttk.Label(summary_frame, text="Total Return: $0.00 (0.00%)", 
                                           font=("Arial", 11))
        self.total_return_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        positions_frame = ttk.LabelFrame(self.parent, text="Current Positions", padding=5)
        positions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.positions_tree = ttk.Treeview(positions_frame, 
                                          columns=('Ticker', 'Shares', 'Avg Price', 'Current Price', 
                                                  'Market Value', 'P&L', 'P&L %'), 
                                          show='headings', height=8)
        
        self.positions_tree.heading('Ticker', text='Ticker')
        self.positions_tree.heading('Shares', text='Shares')
        self.positions_tree.heading('Avg Price', text='Avg Price')
        self.positions_tree.heading('Current Price', text='Current Price')
        self.positions_tree.heading('Market Value', text='Market Value')
        self.positions_tree.heading('P&L', text='P&L')
        self.positions_tree.heading('P&L %', text='P&L %')
        
        self.positions_tree.column('Ticker', width=60, anchor=tk.CENTER)
        self.positions_tree.column('Shares', width=70, anchor=tk.CENTER)
        self.positions_tree.column('Avg Price', width=80, anchor=tk.CENTER)
        self.positions_tree.column('Current Price', width=90, anchor=tk.CENTER)
        self.positions_tree.column('Market Value', width=90, anchor=tk.CENTER)
        self.positions_tree.column('P&L', width=80, anchor=tk.CENTER)
        self.positions_tree.column('P&L %', width=70, anchor=tk.CENTER)
        
        scrollbar_positions = ttk.Scrollbar(positions_frame, orient=tk.VERTICAL, 
                                           command=self.positions_tree.yview)
        self.positions_tree.configure(yscrollcommand=scrollbar_positions.set)
        
        self.positions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_positions.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.positions_tree.tag_configure('profit', foreground='green')
        self.positions_tree.tag_configure('loss', foreground='red')
        self.positions_tree.tag_configure('neutral', foreground='black')
        
    def update_display(self, portfolio_summary):
        self.cash_label.config(text=f"Cash: {format_currency(portfolio_summary['cash'])}")
        self.total_value_label.config(text=f"Total Value: {format_currency(portfolio_summary['total_value'])}")
        
        return_text = f"Total Return: {format_currency(portfolio_summary['total_return'])} ({format_percentage(portfolio_summary['return_percentage'])})"
        
        if portfolio_summary['total_return'] > 0:
            self.total_return_label.config(text=return_text, foreground='green')
        elif portfolio_summary['total_return'] < 0:
            self.total_return_label.config(text=return_text, foreground='red')
        else:
            self.total_return_label.config(text=return_text, foreground='black')
        
        for item in self.positions_tree.get_children():
            self.positions_tree.delete(item)
        
        for position in portfolio_summary['positions']:
            pnl = position['unrealized_pnl']
            pnl_pct = position['unrealized_pnl_pct']
            
            if pnl > 0:
                tag = 'profit'
            elif pnl < 0:
                tag = 'loss'
            else:
                tag = 'neutral'
            
            self.positions_tree.insert('', tk.END, 
                                      values=(
                                          position['ticker'],
                                          int(position['shares']),
                                          format_currency(position['avg_price']),
                                          format_currency(position['current_price']),
                                          format_currency(position['market_value']),
                                          format_currency(pnl),
                                          format_percentage(pnl_pct)
                                      ),
                                      tags=(tag,))
        
        if not portfolio_summary['positions']:
            self.positions_tree.insert('', tk.END, 
                                      values=('No positions', '', '', '', '', '', ''),
                                      tags=('neutral',))