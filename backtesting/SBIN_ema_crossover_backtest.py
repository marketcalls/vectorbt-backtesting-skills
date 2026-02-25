import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import vectorbt as vbt
from openalgo import api, ta

# --- Config ---
script_dir = Path(__file__).resolve().parent

SYMBOL = "SBIN"
EXCHANGE = "NSE"
INTERVAL = "D"
FAST_EMA = 10
SLOW_EMA = 20
INIT_CASH = 1_000_000
FEES = 0.001
ALLOCATION = 0.75

# --- Fetch Data ---
client = api(
    api_key=os.getenv("OPENALGO_API_KEY", "your-api-key-here"),
    host=os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000"),
)

end_date = datetime.now().date()
start_date = end_date - timedelta(days=365 * 3)

print(f"Fetching {SYMBOL} ({EXCHANGE}) {INTERVAL} data from {start_date} to {end_date}")

df = client.history(
    symbol=SYMBOL,
    exchange=EXCHANGE,
    interval=INTERVAL,
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
)

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
else:
    df.index = pd.to_datetime(df.index)

df = df.sort_index()
close = df["close"]

print(f"Data loaded: {len(df)} bars from {df.index[0]} to {df.index[-1]}")

# --- Strategy: EMA {FAST_EMA}/{SLOW_EMA} Crossover ---
ema_fast = vbt.MA.run(close, FAST_EMA, ewm=True, short_name=f"EMA{FAST_EMA}")
ema_slow = vbt.MA.run(close, SLOW_EMA, ewm=True, short_name=f"EMA{SLOW_EMA}")

buy_raw = ema_fast.ma_crossed_above(ema_slow)
sell_raw = ema_fast.ma_crossed_below(ema_slow)

# Clean duplicate signals
entries = ta.exrem(buy_raw, sell_raw)
exits = ta.exrem(sell_raw, buy_raw)

print(f"Signals - Entries: {entries.sum()}, Exits: {exits.sum()}")

# --- Backtest ---
pf = vbt.Portfolio.from_signals(
    close,
    entries,
    exits,
    init_cash=INIT_CASH,
    size=ALLOCATION,
    size_type="percent",
    fees=FEES,
    direction="longonly",
    min_size=1,
    size_granularity=1,
    freq="1D",
)

# --- Results ---
print("\n" + "=" * 60)
print(f"  EMA {FAST_EMA}/{SLOW_EMA} Crossover Backtest - {SYMBOL} ({EXCHANGE})")
print("=" * 60)
print(pf.stats())

print("\n--- Key Metrics ---")
print(f"Total Return:    {pf.total_return() * 100:.2f}%")
print(f"Sharpe Ratio:    {pf.sharpe_ratio():.2f}")
print(f"Sortino Ratio:   {pf.sortino_ratio():.2f}")
print(f"Max Drawdown:    {pf.max_drawdown() * 100:.2f}%")
print(f"Win Rate:        {pf.trades.win_rate() * 100:.1f}%")
print(f"Total Trades:    {pf.trades.count()}")
print(f"Profit Factor:   {pf.trades.profit_factor():.2f}")

# --- Plot ---
fig = pf.plot(
    subplots=["value", "underwater", "cum_returns"],
    template="plotly_dark",
    title=f"EMA {FAST_EMA}/{SLOW_EMA} Crossover - {SYMBOL} ({EXCHANGE} {INTERVAL})",
)
fig.show()

# --- Export Trades ---
trades_file = script_dir / f"{SYMBOL}_ema_crossover_trades.csv"
pf.positions.records_readable.to_csv(trades_file, index=False)
print(f"\nTrades exported to {trades_file}")
