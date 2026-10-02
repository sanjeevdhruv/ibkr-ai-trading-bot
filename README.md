# IBKR AI Trading Bot

A Python-based trading bot that connects directly to Interactive Brokers (IBKR) for live market data and order execution, with optional OpenAI integration for advanced signal processing.

## Features

- **IBKR Connectivity:** Real-time data and order management via ib_insync
- **Entry Filters:** VWAP alignment, RSI thresholds, MACD crossover, volume-spike detection
- **Position Sizing:** 5% of account equity per trade
- **Exits:** Tiered profit targets (25%, 75%, 150%) with partial exits
- **Risk Management:** Configurable stop-loss (default 2%)
- **OpenAI Integration (Optional):** AI-driven signal evaluation and dynamic filter adjustment

## Setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r req.txt
```
Run TWS or IB Gateway with the API enabled and verify the connection with `python connect_test.py` (see [docs/CONNECTING.md](docs/CONNECTING.md), paper port 7497 by default). Then start the bot script you need (`m1_backtest.py` and `m2_code.py` for backtesting, `m3_code.py` for the Tkinter GUI). Put any API keys (e.g. OpenAI) in a local `.env` file, which is git-ignored.

