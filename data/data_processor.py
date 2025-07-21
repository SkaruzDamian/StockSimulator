import talib
import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self):
        pass

    def calculate_technical_indicators(self, data, indicators, selected_features=None): 
        data_copy = data.copy()
        
        data_copy = data_copy.dropna()
        
        if len(data_copy) < 50:
            raise ValueError("Not enough data points for technical indicators")
        
        try:
            high = data_copy['High'].astype(float).values if 'High' in data_copy.columns else None
            low = data_copy['Low'].astype(float).values if 'Low' in data_copy.columns else None
            close = data_copy['Close'].astype(float).values if 'Close' in data_copy.columns else None
            volume = data_copy['Volume'].astype(float).values if 'Volume' in data_copy.columns else None
            open_price = data_copy['Open'].astype(float).values if 'Open' in data_copy.columns else None
        except Exception as e:
            raise ValueError(f"Error converting data to float: {str(e)}")
        
        for indicator in indicators:
            try:
                if indicator == 'SMA' and close is not None:
                    data_copy['SMA_10'] = talib.SMA(close, timeperiod=10)
                    data_copy['SMA_20'] = talib.SMA(close, timeperiod=20)
                    data_copy['SMA_50'] = talib.SMA(close, timeperiod=50)
         
                elif indicator == 'EMA' and close is not None:
                    data_copy['EMA_10'] = talib.EMA(close, timeperiod=10)
                    data_copy['EMA_20'] = talib.EMA(close, timeperiod=20)
                    
                elif indicator == 'RSI' and close is not None:
                    data_copy['RSI_14'] = talib.RSI(close, timeperiod=14)
                    
                elif indicator == 'MACD' and close is not None:
                    macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
                    data_copy['MACD'] = macd
                    data_copy['MACD_Signal'] = macdsignal
                    data_copy['MACD_Hist'] = macdhist
                    
                elif indicator == 'Bollinger Bands' and close is not None:
                    upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
                    data_copy['BB_Upper'] = upper
                    data_copy['BB_Middle'] = middle
                    data_copy['BB_Lower'] = lower
                    data_copy['BB_Width'] = (upper - lower) / middle
                    data_copy['BB_Position'] = (close - lower) / (upper - lower)
                    
                elif indicator == 'Stochastic Oscillator' and high is not None and low is not None and close is not None:
                    slowk, slowd = talib.STOCH(high, low, close,
                                            fastk_period=14, slowk_period=3, slowk_matype=0,
                                            slowd_period=3, slowd_matype=0)
                    data_copy['Stoch_K'] = slowk
                    data_copy['Stoch_D'] = slowd
                    
                elif indicator == 'Williams_R' and high is not None and low is not None and close is not None:
                    data_copy['Williams_R'] = talib.WILLR(high, low, close, timeperiod=14)
                    
                elif indicator == 'ATR' and high is not None and low is not None and close is not None:
                    data_copy['ATR'] = talib.ATR(high, low, close, timeperiod=14)
                    
                elif indicator == 'CCI' and high is not None and low is not None and close is not None:
                    data_copy['CCI'] = talib.CCI(high, low, close, timeperiod=14)
                    
                elif indicator == 'MFI' and high is not None and low is not None and close is not None and volume is not None:
                    data_copy['MFI'] = talib.MFI(high, low, close, volume, timeperiod=14)
                    
                elif indicator == 'ROC' and close is not None:
                    data_copy['ROC'] = talib.ROC(close, timeperiod=10)
                    
                elif indicator == 'OBV' and close is not None and volume is not None:
                    data_copy['OBV'] = talib.OBV(close, volume)
                    
                elif indicator == 'AD' and high is not None and low is not None and close is not None and volume is not None:
                    data_copy['AD'] = talib.AD(high, low, close, volume)
                    
                elif indicator == 'MOM' and close is not None:
                    data_copy['MOM'] = talib.MOM(close, timeperiod=10)
                    
                elif indicator == 'Price Change' and close is not None:
                    data_copy['Price_Change'] = data_copy['Close'].diff()
                    
                elif indicator == 'High Low Ratio' and high is not None and low is not None:
                    data_copy['High_Low_Ratio'] = data_copy['High'] / data_copy['Low']
                    
                elif indicator == 'Volume SMA' and volume is not None:
                    data_copy['Volume_SMA'] = talib.SMA(volume, timeperiod=10)
                    
                elif indicator == 'Volume Ratio' and volume is not None:
                    volume_sma = talib.SMA(volume, timeperiod=10)
                    data_copy['Volume_Ratio'] = volume / volume_sma
                    
            except Exception as e:
                print(f"Warning: Failed to calculate {indicator}: {str(e)}")
                continue

        return data_copy

    def make_target(self, data, days_ahead):  
        data_copy = data.copy()
        
        if len(data_copy) <= days_ahead:
            raise ValueError(f"Not enough data to create target with {days_ahead} days ahead")
        
        if 'Close' not in data_copy.columns:
            raise ValueError("Close price is required for target creation")
            
        future_close = data_copy['Close'].iloc[days_ahead:].values
        current_close = data_copy['Close'].iloc[:-days_ahead].values
        
        target = np.where(future_close > current_close, 1, 0)
        
        data_copy = data_copy.iloc[:-days_ahead].copy()
        data_copy['Target'] = target
        
        data_copy.dropna(inplace=True)
        return data_copy

    def split_data(self, data, date_start, date_end, days_ahead):  
        data_copy = data.copy()
        
        if 'Date' not in data_copy.columns:
            if isinstance(data_copy.index, pd.DatetimeIndex):
                data_copy['Date'] = data_copy.index
            else:
                data_copy['Date'] = pd.to_datetime(data_copy.index)
        else:
            data_copy['Date'] = pd.to_datetime(data_copy['Date'])
        
        data_copy = data_copy.reset_index(drop=True)
        
        date_start = pd.to_datetime(date_start)
        date_end = pd.to_datetime(date_end)
        
        test_mask = (data_copy['Date'] >= date_start) & (data_copy['Date'] <= date_end)
        test_data = data_copy[test_mask].copy()
        
        if len(test_data) == 0:
            raise ValueError(f"No data found between {date_start} and {date_end}")
        
        first_test_position = data_copy[test_mask].index[0]
        
        if first_test_position >= days_ahead:
            train_end_position = first_test_position - days_ahead
            train_data = data_copy.iloc[:train_end_position].copy()
        else:
            raise ValueError(f"Not enough data before test period. Need at least {days_ahead} days.")
        
        test_start_idx_in_data_copy = test_data.index[0] if len(test_data) > 0 else None
        test_end_idx_in_data_copy = test_data.index[-1] if len(test_data) > 0 else None
        
        return train_data, test_data, test_start_idx_in_data_copy, test_end_idx_in_data_copy