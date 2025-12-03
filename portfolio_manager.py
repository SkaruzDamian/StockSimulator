import pandas as pd
from datetime import datetime
from utils import format_currency, format_percentage, calculate_returns

class PortfolioManager:
    def __init__(self, initial_capital, commission_rate):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.commission_rate = commission_rate
        self.positions = {}
        self.transaction_history = []
        self.daily_portfolio_value = []
        
    def get_available_cash(self):
        return self.current_capital
    
    def get_position(self, ticker):
        return self.positions.get(ticker, {'shares': 0, 'avg_price': 0.0, 'total_cost': 0.0})
    
    def can_buy(self, ticker, shares, price):
        total_cost = shares * price
        commission = total_cost * self.commission_rate
        return (total_cost + commission) <= self.current_capital
    
    def can_sell(self, ticker, shares):
        position = self.get_position(ticker)
        return position['shares'] >= shares
    
    def buy_stock(self, ticker, shares, price, date):
        total_cost = shares * price
        commission = total_cost * self.commission_rate
        total_with_commission = total_cost + commission
        
        if not self.can_buy(ticker, shares, price):
            return False, "Insufficient funds"
        
        self.current_capital -= total_with_commission
        
        if ticker in self.positions:
            old_shares = self.positions[ticker]['shares']
            old_total_cost = self.positions[ticker]['total_cost']
            
            new_shares = old_shares + shares
            new_total_cost = old_total_cost + total_cost
            new_avg_price = new_total_cost / new_shares
            
            self.positions[ticker] = {
                'shares': new_shares,
                'avg_price': new_avg_price,
                'total_cost': new_total_cost
            }
        else:
            self.positions[ticker] = {
                'shares': shares,
                'avg_price': price,
                'total_cost': total_cost
            }
        
        self.transaction_history.append({
            'date': date,
            'ticker': ticker,
            'action': 'BUY',
            'shares': shares,
            'price': price,
            'commission': commission,
            'total_cost': total_with_commission
        })
        
        return True, f"Bought {shares} shares of {ticker} at {format_currency(price)}"
    
    def sell_stock(self, ticker, shares, price, date):
        if not self.can_sell(ticker, shares):
            return False, "Insufficient shares"
        
        total_revenue = shares * price
        commission = total_revenue * self.commission_rate
        net_revenue = total_revenue - commission
        
        self.current_capital += net_revenue
        
        position = self.positions[ticker]
        remaining_shares = position['shares'] - shares
        
        if remaining_shares == 0:
            del self.positions[ticker]
        else:
            cost_per_share = position['total_cost'] / position['shares']
            remaining_cost = remaining_shares * cost_per_share
            
            self.positions[ticker] = {
                'shares': remaining_shares,
                'avg_price': position['avg_price'],
                'total_cost': remaining_cost
            }
        
        self.transaction_history.append({
            'date': date,
            'ticker': ticker,
            'action': 'SELL',
            'shares': shares,
            'price': price,
            'commission': commission,
            'net_revenue': net_revenue
        })
        
        return True, f"Sold {shares} shares of {ticker} at {format_currency(price)}"
    
    def get_portfolio_value(self, current_prices):
        portfolio_value = self.current_capital
        
        for ticker, position in self.positions.items():
            current_price = current_prices.get(ticker, position['avg_price'])
            portfolio_value += position['shares'] * current_price
        
        return portfolio_value
    
    def get_portfolio_summary(self, current_prices):
        total_value = self.get_portfolio_value(current_prices)
        total_return = total_value - self.initial_capital
        return_percentage = calculate_returns(self.initial_capital, total_value)
        
        positions_summary = []
        for ticker, position in self.positions.items():
            current_price = current_prices.get(ticker, position['avg_price'])
            market_value = position['shares'] * current_price
            unrealized_pnl = market_value - position['total_cost']
            unrealized_pnl_pct = calculate_returns(position['total_cost'], market_value)
            
            positions_summary.append({
                'ticker': ticker,
                'shares': position['shares'],
                'avg_price': position['avg_price'],
                'current_price': current_price,
                'market_value': market_value,
                'unrealized_pnl': unrealized_pnl,
                'unrealized_pnl_pct': unrealized_pnl_pct
            })
        
        return {
            'cash': self.current_capital,
            'total_value': total_value,
            'total_return': total_return,
            'return_percentage': return_percentage,
            'positions': positions_summary
        }
    
    def record_daily_value(self, date, current_prices):
        portfolio_value = self.get_portfolio_value(current_prices)
        self.daily_portfolio_value.append({
            'date': date,
            'value': portfolio_value,
            'return': calculate_returns(self.initial_capital, portfolio_value)
        })
        print(f"DEBUG: Zapisano wartość portfolio na {date}: ${portfolio_value:.2f}")
    def get_transaction_history(self):
        return pd.DataFrame(self.transaction_history)
    
    def get_performance_history(self):
        return pd.DataFrame(self.daily_portfolio_value)
    
    def reset_portfolio(self):
        self.current_capital = self.initial_capital
        self.positions = {}
        self.transaction_history = []
        self.daily_portfolio_value = []