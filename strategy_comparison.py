import pandas as pd
from datetime import datetime
from agent_simulation import AgentSimulation, BasicStrategy, AggressiveStrategy, ConservativeStrategy

class StrategyComparison:
    def __init__(self, trading_simulator, progress_callback=None):
        self.trading_simulator = trading_simulator
        self.progress_callback = progress_callback
        
        self.strategies = {
            "Basic Strategy": BasicStrategy(),
            "Aggressive Strategy": AggressiveStrategy(),
            "Conservative Strategy": ConservativeStrategy()
        }
        
        self.results = {}
        
    def run_comparison(self):
        total_strategies = len(self.strategies)
        strategy_index = 0
        
        for strategy_name, strategy in self.strategies.items():
            print(f"Running simulation for {strategy_name}...")
            
            def adjusted_progress_callback(current_day, total_days, progress):
                overall_progress = (strategy_index * 100 + progress) / total_strategies
                if self.progress_callback:
                    self.progress_callback(
                        current_day + strategy_index * total_days,
                        total_days * total_strategies,
                        overall_progress
                    )
            
            agent_sim = AgentSimulation(
                self.trading_simulator,
                strategy,
                adjusted_progress_callback
            )
            
            success, message = agent_sim.run_simulation()
            
            if success:
                self.results[strategy_name] = {
                    'daily_portfolio_value': agent_sim.agent_portfolio.daily_portfolio_value.copy(),
                    'stats': agent_sim.stats.copy(),
                    'initial_capital': self.trading_simulator.initial_capital
                }
                print(f"{strategy_name} completed successfully")
            else:
                print(f"{strategy_name} failed: {message}")
                self.results[strategy_name] = None
            
            strategy_index += 1
            
            if strategy_index < total_strategies:
                self.trading_simulator.reset_simulation()
        
        return self.results