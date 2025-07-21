import yfinance as yf
import pandas as pd

class DataLoader:
    def __init__(self, ticker):
        self.ticker = ticker 

    def load_data(self):
        data = yf.download(self.ticker, period="max", auto_adjust=True, prepost=True, threads=True)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        
        data = data.dropna()
        
        if data.index.name != 'Date':
            data = data.reset_index()
            
        return data