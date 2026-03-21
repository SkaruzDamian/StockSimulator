# Stock Market Trading Simulator

A desktop application for backtesting ML-based stock trading strategies. Built as part of a university project — the idea was to combine machine learning with real stock market data and see if you can actually make the models do something useful.

## What it does

The app lets you pick a set of stock tickers, choose a date range, configure technical indicators, train a classifier (or a few of them), and then run a full backtest simulation to see how your strategy would have performed historically. You can also run an autonomous agent simulation where different strategies compete against each other.

Features:
- Fetches real historical stock data via `yfinance`
- Computes 18 technical indicators (RSI, MACD, Bollinger Bands, ATR, OBV, etc.)
- Trains one of 6 ML models on the processed data
- Backtests buy/sell decisions driven by model predictions
- Tracks portfolio value, transactions, returns over time
- Visualizes everything with charts inside the app
- Agent mode: 3 strategies (Basic, Aggressive, Conservative) run simultaneously and you can compare results
- Strategy comparison view across multiple tickers

## Models available

| Model | Notes |
|---|---|
| Decision Tree | fast, easy to interpret |
| Random Forest | usually the most reliable one |
| SVM | slow on big datasets but decent |
| KNN | simple baseline |
| Logistic Regression | surprisingly not bad |
| Ensemble | RF + SVM + LR voting classifier |

Model hyperparameters are stored in `model_params.json` and loaded via `model_config_loader.py`, so you can tweak them without touching the code.

## Tech stack

- **Python 3.10+**
- **Tkinter** — GUI (yeah, not the prettiest, but it works and has no external dependencies beyond the standard library)
- **scikit-learn** — all the ML stuff
- **TA-Lib** — technical indicator calculations
- **yfinance** — stock data
- **pandas / numpy** — data processing
- **matplotlib** — charts embedded in the app

## Installation

> ⚠️ TA-Lib can be annoying to install. On Windows you'll probably need to grab a precompiled wheel from [here](https://github.com/cgohlke/talib-build/releases). On Linux: `sudo apt-get install libta-lib-dev` first.

```bash
git clone https://github.com/yourusername/trading-simulator.git
cd trading-simulator

pip install -r requirements.txt
```

Then just run:

```bash
python main.py
```

## Project structure

```
.
├── main.py                     # entry point
├── main_window.py              # main GUI window
├── config.py                   # global settings, available models/indicators
├── requirements.txt
│
├── # Simulation core
├── trading_simulator.py        # backtesting logic
├── agent_simulation.py         # autonomous agent with 3 strategies
├── portfolio_manager.py        # tracks positions, capital, P&L
├── transaction_logger.py       # logs all buy/sell events
│
├── # Data
├── data_loader.py              # fetches data from yfinance
├── data_processor.py           # indicator calculation, feature engineering, train/test split
│
├── # ML Models
├── decision_tree_model.py
├── random_forest_model.py
├── svm_model.py
├── knn_model.py
├── logistic_regression_model.py
├── ensemble_model.py
├── model_config_loader.py      # loads params from model_params.json
├── model_params.json
│
├── # GUI Windows
├── simulation_window.py
├── agent_window.py
├── agent_results_window.py
├── manual_results_window.py
├── strategy_comparison_window.py
├── chart_widget.py
├── portfolio_widget.py
│
├── # Strategy logic
├── strategy_comparison.py
│
├── # Utils
├── utils.py
│
└── # Tests
    ├── test_data_processor.py
    ├── test_portfolio_manager.py
    ├── test_functional.py
    ├── test_integration.py
    └── run_all_tests.py
```

## Default config

From `config.py`:

```python
DEFAULT_SETTINGS = {
    'initial_capital': 10000.0,
    'commission': 0.002,       # 0.2% per trade
    'days_ahead': 1,           # predict 1 day ahead
    'start_date': '2020-01-01',
    'end_date': '2023-12-31'
}
```

## Running tests

```bash
python run_all_tests.py
```

Or individually:

```bash
python -m pytest test_data_processor.py
python -m pytest test_portfolio_manager.py
python -m pytest test_functional.py
python -m pytest test_integration.py
```

## Notes / known issues

- TA-Lib installation can be painful depending on your OS — check their official docs if pip fails
- Some tickers might not have full data for the selected date range, the app will skip them and notify you
- The GUI is built with Tkinter so don't expect anything fancy visually
- On very long date ranges with many tickers, training can take a while (especially SVM)

## Disclaimer

This is a university project, not financial advice. Don't use this to make actual investment decisions. Past performance in a backtest means nothing in real markets.

---

