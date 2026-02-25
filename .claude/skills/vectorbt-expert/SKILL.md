---
name: vectorbt-expert
description: VectorBT backtesting expert. Use when user asks to backtest strategies, create entry/exit signals, analyze portfolio performance, optimize parameters, fetch historical data, use VectorBT/vectorbt, compare strategies, position sizing, equity curves, drawdown charts, or trade analysis. Also triggers for openalgo.ta helpers (exrem, crossover, crossunder, flip, donchian, supertrend).
user-invocable: false
---

# VectorBT Backtesting Expert Skill

## Environment

- Python with vectorbt, pandas, numpy, plotly
- Data source: OpenAlgo Python SDK (`openalgo` package) for Indian markets
- Alternative data: `yfinance` for Yahoo Finance data
- All scripts run from `D:\QuantFlow 3\Day17\backtesting\`
- Environment variables loaded from `.env` file in the script directory
- Never use icons/emojis in code or logger output

## Data Fetching

### OpenAlgo (Primary - Indian Markets)

```python
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from openalgo import api

# Load environment
script_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=script_dir / ".env", override=False)

api_key = os.getenv("OPENALGO_API_KEY")
host = os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000")

client = api(api_key=api_key, host=host)

# Fetch historical data
df = client.history(
    symbol="SBIN",           # OpenAlgo symbol format
    exchange="NSE",          # NSE, BSE, NFO, BFO, CDS, MCX
    interval="5m",           # 1m, 3m, 5m, 10m, 15m, 30m, 1h, D
    start_date="2025-01-01",
    end_date="2025-02-25",
)
# Returns DataFrame with columns: close, high, low, open, volume
# Index: timestamp (datetime with timezone)

close = df["close"]
```

### OpenAlgo Intervals

| Interval | Code |
|----------|------|
| 1 minute | `1m` |
| 3 minutes | `3m` |
| 5 minutes | `5m` |
| 10 minutes | `10m` |
| 15 minutes | `15m` |
| 30 minutes | `30m` |
| 1 hour | `1h` |
| Daily | `D` |

### OpenAlgo Exchange Codes

| Exchange | Code | Description |
|----------|------|-------------|
| NSE | `NSE` | National Stock Exchange equities |
| BSE | `BSE` | Bombay Stock Exchange equities |
| NFO | `NFO` | NSE Futures and Options |
| BFO | `BFO` | BSE Futures and Options |
| CDS | `CDS` | NSE Currency Derivatives |
| BCD | `BCD` | BSE Currency Derivatives |
| MCX | `MCX` | Multi Commodity Exchange |
| NSE_INDEX | `NSE_INDEX` | NSE Indices |
| BSE_INDEX | `BSE_INDEX` | BSE Indices |

### OpenAlgo Symbol Format

- **Equity**: `SBIN`, `RELIANCE`, `INFY`, `HDFCBANK`
- **Futures**: `BANKNIFTY24APR24FUT` (BaseSymbol + ExpiryDate + FUT)
- **Options**: `NIFTY28MAR2420800CE` (BaseSymbol + ExpiryDate + StrikePrice + CE/PE)
- **Index**: `NIFTY`, `BANKNIFTY`, `FINNIFTY` (with exchange=NSE_INDEX)

### Yahoo Finance (Alternative)

```python
import yfinance as yf
import vectorbt as vbt

# Method 1: via yfinance directly
df = yf.download("RELIANCE.NS", start="2015-01-01", end="2026-02-24",
                  interval="1d", auto_adjust=True, multi_level_index=False)
close = df['Close']

# Method 2: via VectorBT wrapper
data = vbt.YFData.download("RELIANCE.NS", start="2015-01-01", end="2026-02-24")
close = data.get("Close")
```

## VectorBT Simulation Modes

### 1. from_signals (Signal-Based) - Most Common

Entry/exit boolean arrays. VectorBT processes signals sequentially - after entry, waits for exit before next entry (unless `accumulate=True`).

```python
import vectorbt as vbt
import numpy as np

pf = vbt.Portfolio.from_signals(
    close,                      # Price series (required)
    entries,                    # Boolean Series - True = buy signal
    exits,                      # Boolean Series - True = sell signal
    init_cash=1_000_000,        # Starting capital
    fees=0.001,                 # 0.1% per trade
    slippage=0.0005,            # 0.05% slippage
    size=0.75,                  # Position size
    size_type="percent",        # How to interpret size
    direction="longonly",       # longonly, shortonly, both
    freq="1D",                  # Data frequency
    min_size=1,                 # Minimum order size
    size_granularity=1,         # Round to whole shares
    sl_stop=0.05,               # 5% stop loss (optional)
    tp_stop=0.10,               # 10% take profit (optional)
    accumulate=False,           # True = allow pyramiding
)
```

### 2. from_orders (Order-Based) - Direct Orders

Provide explicit order arrays. Fastest simulation mode.

```python
pf = vbt.Portfolio.from_orders(
    close=close,
    size=0.15,                  # Target 15% allocation
    size_type='targetpercent',  # Rebalances to target weight
    group_by=True,              # Group columns as one portfolio
    cash_sharing=True,          # Share cash across assets
    fees=0.001,
    init_cash=1_000_000,
    freq='1D',
    min_size=1,
    size_granularity=1,
)
```

### 3. from_order_func (Custom Callback) - Most Powerful

Numba-compiled functions called at each bar with full portfolio state access. Use for complex logic. `flexible=True` allows multiple orders per symbol per bar.

### 4. from_holding (Buy-and-Hold Benchmark)

```python
pf_benchmark = vbt.Portfolio.from_holding(close, init_cash=1_000_000, fees=0.001)
```

## Position Sizing

| SizeType | `size_type=` | `size=` meaning | Best For |
|----------|-------------|-----------------|----------|
| Amount | `"amount"` | Fixed number of shares | Simple testing |
| Value | `"value"` | Fixed cash amount per trade | Fixed exposure |
| Percent | `"percent"` | Fraction of current portfolio (0.5 = 50%) | Risk-adjusted trading |
| TargetPercent | `"targetpercent"` | Target portfolio weight (rebalances) | Portfolio allocation |
| TargetAmount | `"targetamount"` | Rebalance to target shares | Specific share targets |
| TargetValue | `"targetvalue"` | Rebalance to target dollar value | Specific value targets |

Default: `size=np.inf` with Amount = invest all available cash.

### Percent Sizing (Most Popular)

```python
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    size=0.5,              # 50% of portfolio equity per trade
    size_type="percent",
    init_cash=1_000_000,
    fees=0.001,
    min_size=1,
    size_granularity=1,
    freq="1D"
)
```

## Creating Indicators & Signals

### RSI Strategy

```python
rsi = vbt.RSI.run(close, window=14)
entries = rsi.rsi_crossed_below(30)   # Oversold = buy
exits = rsi.rsi_crossed_above(70)     # Overbought = sell
```

### EMA Crossover Strategy

```python
ema_short = vbt.MA.run(close, 10, ewm=True, short_name='EMA10')
ema_long = vbt.MA.run(close, 20, ewm=True, short_name='EMA20')

entries = ema_short.ma_crossed_above(ema_long)
exits = ema_short.ma_crossed_below(ema_long)
```

### SMA Crossover Strategy

```python
fast_ma = vbt.MA.run(close, window=10)
slow_ma = vbt.MA.run(close, window=20)

entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)
```

## Stop Loss & Take Profit

```python
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    sl_stop=0.05,     # Exit if price drops 5% from entry
    tp_stop=0.10,     # Exit if price rises 10% from entry
    ts_stop=0.03,     # Trailing stop: 3% from highest price since entry
    init_cash=1_000_000,
    fees=0.001,
    freq="1D"
)
```

## Parameter Optimization

### Method 1: Broadcasting (Vectorized - VectorBT's Killer Feature)

Test thousands of parameter combinations simultaneously without loops:

```python
# Test 99 x 99 = 9,801 window combinations at once
fast_ma = vbt.MA.run(close, window=np.arange(2, 101))
slow_ma = vbt.MA.run(close, window=np.arange(2, 101))

entries = fast_ma.ma_crossed_above(slow_ma)
exits = fast_ma.ma_crossed_below(slow_ma)

pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=100_000, fees=0.001, freq="1D")

# Get total return for all combinations
total_returns = pf.total_return()

# Find best parameters
best_idx = total_returns.idxmax()
print(f"Best fast window: {best_idx[0]}, Best slow window: {best_idx[1]}")
print(f"Best return: {total_returns.max():.2%}")
```

### Method 2: Loop-Based Optimization (EMA Crossover Example)

When you need more control over each iteration or want to collect custom metrics:

```python
import vectorbt as vbt
import numpy as np

# Parameter grid
short_spans = np.arange(5, 15, 1)   # 5 to 14
long_spans = np.arange(15, 30, 1)   # 15 to 29

results = []

for short_span in short_spans:
    for long_span in long_spans:
        short_ema = vbt.MA.run(close, short_span, short_name='fast', ewm=True)
        long_ema = vbt.MA.run(close, long_span, short_name='slow', ewm=True)

        entries = short_ema.ma_crossed_above(long_ema)
        exits = short_ema.ma_crossed_below(long_ema)

        portfolio = vbt.Portfolio.from_signals(
            close, entries, exits,
            size=0.5,
            size_type='percent',
            fees=0.001,
            init_cash=100_000,
            freq='1D',
            min_size=1,
            size_granularity=1,
        )

        results.append({
            'short_span': short_span,
            'long_span': long_span,
            'total_return': portfolio.total_return(),
            'sharpe_ratio': portfolio.sharpe_ratio(),
            'max_drawdown': portfolio.max_drawdown(),
            'trade_count': portfolio.trades.count(),
        })

# Convert to DataFrame for analysis
results_df = pd.DataFrame(results)
best = results_df.loc[results_df['total_return'].idxmax()]
print(f"Best: Short EMA={int(best['short_span'])}, Long EMA={int(best['long_span'])}")
print(f"Return: {best['total_return']:.2%}, Sharpe: {best['sharpe_ratio']:.2f}")
```

## Performance Analysis

### Full Stats

```python
pf.stats()                          # Complete performance summary
```

### Individual Metrics

```python
pf.total_return() * 100             # Total return %
pf.sharpe_ratio()                   # Sharpe ratio
pf.sortino_ratio()                  # Sortino ratio
pf.max_drawdown()                   # Maximum drawdown
pf.trades.win_rate()                # Win rate
pf.trades.count()                   # Total trades
pf.trades.profit_factor()           # Profit factor
```

### Trade Records

```python
pf.trades.records_readable          # DataFrame of all trades
pf.orders.records_readable          # DataFrame of all orders
pf.positions.records_readable       # DataFrame of all positions
```

### Equity & Cash

```python
pf.value()                          # Equity curve over time
pf.cash()                           # Cash balance over time
```

### Export Trades

```python
pf.positions.records_readable.to_csv("trades.csv", index=False)
```

### Benchmark Comparison

```python
import yfinance as yf

# Build benchmark returns
nifty = yf.download("^NSEI", start=close.index.min(), end=close.index.max(),
                    auto_adjust=True, multi_level_index=False)["Close"]
bench_rets = nifty.reindex(close.index).ffill().bfill().vbt.to_returns()
pf.returns_stats(benchmark_rets=bench_rets)
```

## Plotting

### Built-in Plots

```python
fig = pf.plot()                                         # Full portfolio plot
fig.show()

fig = pf.plot(subplots=['cum_returns'])                 # Cumulative returns
fig.show()

fig = pf.plot_cum_returns()                             # Dedicated cumulative returns
fig.show()

fig = pf.plot(subplots=['value', 'underwater'])         # Equity + drawdown
fig.show()

fig = pf.plot(subplots=['drawdowns', 'underwater'])     # Drawdown periods
fig.show()
```

### Available Subplots

```python
list(pf.subplots.keys())   # See all available subplot names
# Common: 'value', 'cum_returns', 'underwater', 'drawdowns', 'trades', 'orders'
```

### Custom Subplot Settings

```python
fig = pf.plot(
    subplots=['value', 'underwater'],
    subplot_settings={
        'value': {'title': 'Equity Curve'},
        'underwater': {'title': 'Drawdown', 'yaxis_kwargs': {'tickformat': '.1%'}}
    }
)
fig.show()
```

### Custom Strategy vs Benchmark Chart (Plotly)

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

cum_pf = pf.value() / pf.value().iloc[0] - 1
cum_bm = (nifty / nifty.iloc[0] - 1).reindex(cum_pf.index).ffill().bfill()
dd_pf = cum_pf / cum_pf.cummax() - 1

fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    row_heights=[0.65, 0.35], vertical_spacing=0.07)
fig.add_trace(go.Scatter(x=cum_pf.index, y=cum_pf, name='Strategy (cum %)'), row=1, col=1)
fig.add_trace(go.Scatter(x=cum_bm.index, y=cum_bm, name='NIFTY 50 (cum %)'), row=1, col=1)
fig.add_trace(go.Scatter(x=dd_pf.index, y=dd_pf, name='Drawdown', mode='lines'), row=2, col=1)
fig.update_yaxes(tickformat='.1%', row=1, col=1)
fig.update_yaxes(title_text='Drawdown', tickformat='.1%', row=2, col=1)
fig.update_layout(title='Cumulative Returns vs NIFTY 50 + Drawdown')
fig.show()
```

## Direction

| Direction | `direction=` | Behavior |
|-----------|-------------|----------|
| Long Only | `"longonly"` | Only buy and sell (default) |
| Short Only | `"shortonly"` | Only short and cover |
| Both | `"both"` | Can go long and short |

## Key Parameters Reference

| Parameter | Default | Description |
|-----------|---------|-------------|
| `init_cash` | 100 | Starting capital |
| `fees` | 0 | Transaction fee as decimal (0.001 = 0.1%) |
| `fixed_fees` | 0 | Flat fee per trade |
| `slippage` | 0 | Price slippage as decimal |
| `size` | np.inf | Position size |
| `size_type` | Amount | How to interpret size |
| `direction` | longonly | Trade direction |
| `freq` | auto | Data frequency (1D, 1H, 5T, etc.) |
| `accumulate` | False | Allow pyramiding |
| `sl_stop` | None | Stop loss (decimal, e.g. 0.05 = 5%) |
| `tp_stop` | None | Take profit (decimal) |
| `ts_stop` | None | Trailing stop (decimal) |
| `min_size` | 0 | Minimum order size |
| `size_granularity` | None | Round size to this increment |

## Template: Full Backtest Script with OpenAlgo Data

```python
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import vectorbt as vbt
from dotenv import load_dotenv
from openalgo import api

# --- Config ---
script_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=script_dir / ".env", override=False)

SYMBOL = os.getenv("OPENALGO_SYMBOL", "SBIN")
EXCHANGE = os.getenv("OPENALGO_EXCHANGE", "NSE")
INTERVAL = os.getenv("OPENALGO_INTERVAL", "D")
INIT_CASH = 1_000_000
FEES = 0.001
ALLOCATION = 0.75

# --- Fetch Data ---
client = api(
    api_key=os.getenv("OPENALGO_API_KEY"),
    host=os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000"),
)

end_date = datetime.now().date()
start_date = end_date - timedelta(days=365 * 3)

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

# --- Strategy: EMA Crossover ---
ema_short = vbt.MA.run(close, 10, ewm=True, short_name='EMA10')
ema_long = vbt.MA.run(close, 20, ewm=True, short_name='EMA20')

entries = ema_short.ma_crossed_above(ema_long)
exits = ema_short.ma_crossed_below(ema_long)

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
print(pf.stats())
print(f"\nTotal Return: {pf.total_return() * 100:.2f}%")
print(f"Sharpe Ratio: {pf.sharpe_ratio():.2f}")
print(f"Max Drawdown: {pf.max_drawdown() * 100:.2f}%")
print(f"Win Rate: {pf.trades.win_rate() * 100:.1f}%")
print(f"Total Trades: {pf.trades.count()}")

# --- Plot ---
fig = pf.plot(subplots=['value', 'underwater', 'cum_returns'])
fig.show()

# --- Export ---
pf.positions.records_readable.to_csv(
    script_dir / f"{SYMBOL}_backtest_trades.csv", index=False
)
```

## Common Patterns

### Multiple Timeframe Data Fetch

```python
# Daily data
df_daily = client.history(symbol="RELIANCE", exchange="NSE", interval="D",
                          start_date="2024-01-01", end_date="2025-02-25")

# 5-minute intraday data
df_5m = client.history(symbol="RELIANCE", exchange="NSE", interval="5m",
                       start_date="2025-02-01", end_date="2025-02-25")
```

### Multi-Asset Portfolio

```python
symbols = ["RELIANCE", "HDFCBANK", "INFY", "TCS"]
dfs = {}
for sym in symbols:
    dfs[sym] = client.history(symbol=sym, exchange="NSE", interval="D",
                              start_date="2024-01-01", end_date="2025-02-25")

close_prices = pd.DataFrame({sym: dfs[sym]["close"] for sym in symbols})
```

### Random Signal Baseline

```python
pf_random = vbt.Portfolio.from_random_signals(close, n=50, init_cash=1_000_000, fees=0.001)
```

### Save/Load Portfolio

```python
pf.save("my_backtest.pkl")
pf_loaded = vbt.Portfolio.load("my_backtest.pkl")
```

---

## OpenAlgo TA Helper Functions (`openalgo.ta`)

The `openalgo` package provides signal helper functions critical for clean signal generation:

```python
from openalgo import ta

# exrem: Remove excess signals - keeps only first entry before an exit, first exit before an entry
# Prevents duplicate consecutive buy/sell signals
entries = ta.exrem(buy_raw, sell_raw)
exits = ta.exrem(sell_raw, buy_raw)

# crossover: True when series1 crosses above series2
cross_up = ta.crossover(close, upper_band)

# crossunder: True when series1 crosses below series2
cross_down = ta.crossunder(close, lower_band)

# flip: Returns True regime from trigger1 until trigger2 fires (and vice versa)
bull_regime = ta.flip(bull_trigger, bear_trigger)
bear_regime = ta.flip(bear_trigger, bull_trigger)

# donchian: Returns (upper, middle, lower) Donchian channel
upper, middle, lower = ta.donchian(high, low, period=20)

# supertrend: Returns (supertrend_line, direction)
st_line, st_direction = ta.supertrend(high, low, close, period=10, multiplier=3.0)
```

---

## CSV Data Loading & Resampling

### Load Minute-Level CSV Data

```python
import pandas as pd
from pathlib import Path

csv_file = Path("data") / "NIFTYF.csv"
df = pd.read_csv(
    csv_file,
    usecols=["Ticker", "Date", "Time", "Open", "High", "Low", "Close", "Volume"]
)

# Build datetime index
df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"])
df = df.set_index("datetime").sort_index()
df = df.drop(columns=["Date", "Time", "Ticker"])
```

### Resample to Different Timeframes

```python
def resample_df(df, tf="D"):
    if tf == "D":
        return df.resample("D").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna()
    elif tf == "H":
        # 60-min bars aligned to Indian market open (09:15)
        return df.resample("60min", origin="start_day", offset="9h15min").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna()
    elif tf == "5min":
        return df.resample("5min", origin="start_day", offset="9h15min",
                           label="right", closed="right").agg({
            "Open": "first", "High": "max", "Low": "min", "Close": "last", "Volume": "sum"
        }).dropna()
    else:
        raise ValueError("Unsupported timeframe")

timeframe = "H"
df_resampled = resample_df(df, tf=timeframe)
close = df_resampled["Close"]
```

---

## Futures Backtesting (Lot Size)

For NIFTY/BANKNIFTY futures, use `min_size` and `size_granularity` set to the lot size, and `size_type="value"` for fixed capital deployment:

```python
lot_size = 75  # NIFTY Futures lot size
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    init_cash=30_00_000,        # 30 lakh
    size=20_00_000,             # Deploy 20L of 30L per trade
    size_type="value",
    direction="longonly",
    fees=0.0003,                # 0.03% for futures
    min_size=lot_size,          # Minimum = 1 lot
    size_granularity=lot_size,  # Round to lot multiples
    freq="1D" if timeframe == "D" else "1h",
)
```

Common lot sizes: NIFTY=75, BANKNIFTY=30, Stock futures=varies (see LOTSIZE.csv).

---

## Strategy Catalog

### 1. EMA Crossover with TA-Lib

```python
import talib as tl
from openalgo import ta

fast_period, slow_period = 12, 26
ema_fast = pd.Series(tl.EMA(close.values, timeperiod=fast_period), index=close.index)
ema_slow = pd.Series(tl.EMA(close.values, timeperiod=slow_period), index=close.index)

buy_raw = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
sell_raw = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))
```

### 2. Donchian Channel Breakout

```python
from openalgo import ta

upper, middle, lower = ta.donchian(df["HIGH"], df["LOW"], period=20)

# Use shifted levels (previous bar's channel) to avoid lookahead
upper_shifted = upper.shift(1)
lower_shifted = lower.shift(1)

entries = pd.Series(ta.crossover(df["CLOSE"], upper_shifted), index=df.index)
exits = pd.Series(ta.crossunder(df["CLOSE"], lower_shifted), index=df.index)
```

### 3. Momentum (MOM) Strategy - Long & Short

```python
import talib as tl
from openalgo import ta

LENGTH = 12
mom0 = pd.Series(tl.MOM(close.values, timeperiod=LENGTH), index=close.index)
mom1 = pd.Series(tl.MOM(mom0.values, timeperiod=1), index=close.index)

# Conditions
cond_long = (mom0 > 0) & (mom1 > 0)
cond_short = (mom0 < 0) & (mom1 < 0)

# Next-bar fill (shift conditions by 1, confirm with price breakout)
prev_high = high.shift(1)
prev_low = low.shift(1)
MINTICK = 0.05

entries_long = (cond_long.shift(1) & (high >= (prev_high + MINTICK))).fillna(False)
entries_short = (cond_short.shift(1) & (low <= (prev_low - MINTICK))).fillna(False)

# Clean overlapping signals
entries_long = ta.exrem(entries_long, entries_short)
entries_short = ta.exrem(entries_short, entries_long)

# Exits = opposite entry
exits_long = entries_short
exits_short = entries_long
```

### 4. MACD Signal-Candle Breakout

```python
import talib as tl
from openalgo import ta

macd, macd_signal, macd_hist = tl.MACD(close.values, fastperiod=12, slowperiod=26, signalperiod=9)
macd_series = pd.Series(macd, index=close.index)
zero = pd.Series(0.0, index=close.index)

# MACD zero-line flips define regimes
bull_flip = ta.crossover(macd_series, zero)
bear_flip = ta.crossunder(macd_series, zero)

bull_regime = ta.flip(bull_flip, bear_flip)
bear_regime = ta.flip(bear_flip, bull_flip)

# Signal candle levels (capture and carry forward)
sig_high = high.where(bull_flip).ffill()
sig_low = low.where(bear_flip).ffill()

# Entries: price breaks signal candle level during matching regime
long_entry_raw = ta.crossover(high, sig_high) & bull_regime
short_entry_raw = ta.crossunder(low, sig_low) & bear_regime

# Only first entry per regime
entries_long = ta.exrem(long_entry_raw, bear_flip)
entries_short = ta.exrem(short_entry_raw, bull_flip)

# Exits on opposite regime flip
exits_long = ta.exrem(bear_flip, entries_long)
exits_short = ta.exrem(bull_flip, entries_short)
```

### 5. SDA2 Trend Following System

```python
import talib as tl
from openalgo import ta

# SDA2 Channel: WMA of ((H+L)/2 + (O-C)) with STDDEV and ATR bands
base = ((high + low) / 2.0) + (df_resampled["Open"] - close)
derived = pd.Series(tl.WMA(base.astype(float).values, timeperiod=3), index=close.index)

sd7 = pd.Series(tl.STDDEV(derived.values, timeperiod=7, nbdev=1.0), index=close.index)
atr2 = pd.Series(tl.ATR(high.values, low.values, close.values, timeperiod=2), index=close.index)

upper = derived + sd7 + (atr2 / 1.5)
lower = derived - sd7 - (atr2 / 1.0)

# Entry/Exit: price crosses channel bands
entries = (close > upper) & (close.shift(1) <= upper.shift(1))
exits = (lower > close) & (lower.shift(1) <= close.shift(1))

entries = ta.exrem(entries.fillna(False), exits.fillna(False))
exits = ta.exrem(exits.fillna(False), entries)
```

### 6. Supertrend Intraday (with Time-Based Exit)

```python
from openalgo import ta
from datetime import time

# Supertrend indicator
st_line, st_direction = ta.supertrend(df5["HIGH"], df5["LOW"], df5["CLOSE"],
                                       period=10, multiplier=3.0)

close = df5["CLOSE"]
t = df5.index.time

# Cross signals
cross_up = (close > st_line) & (close.shift(1) <= st_line.shift(1))
cross_down = (close < st_line) & (close.shift(1) >= st_line.shift(1))

# Time windows: entries 09:30-15:00, forced exit at 15:15
entry_window = (t >= time(9, 30)) & (t <= time(15, 0))
at_1515 = (t == time(15, 15))

long_entries = cross_up & entry_window
long_exits = cross_down | at_1515
short_entries = cross_down & entry_window
short_exits = cross_up | at_1515
```

### 7. Dual Momentum (NIFTYBEES vs GOLDBEES)

```python
import numpy as np
import vectorbt as vbt

# Assumes panel DataFrame with close_NIFTYBEES, close_GOLDBEES columns
# Resample to 3-month periods
res_3m_close = pd.DataFrame({
    "NIFTYBEES": panel["close_NIFTYBEES"].resample("3ME").last(),
    "GOLDBEES": panel["close_GOLDBEES"].resample("3ME").last(),
}).dropna(how="all")

# 3M returns determine winner
ret_3m = res_3m_close.pct_change()
winner_3m = np.where(ret_3m["NIFTYBEES"] >= ret_3m["GOLDBEES"], "NIFTYBEES", "GOLDBEES")
winner_3m = pd.Series(winner_3m, index=ret_3m.index)

# Build daily allocation from 3M decisions (applied from next bar)
alloc_daily = pd.Series(index=panel.index, dtype="object")
for dt, val in winner_3m.items():
    next_idx_pos = panel.index.searchsorted(dt, side="right")
    if next_idx_pos < len(panel.index):
        alloc_daily.loc[panel.index[next_idx_pos]] = val
alloc_daily = alloc_daily.ffill().loc[alloc_daily.first_valid_index():]

# Build target weights
weights = pd.DataFrame(index=alloc_daily.index, columns=["NIFTYBEES", "GOLDBEES"], dtype=float)
weights["NIFTYBEES"] = (alloc_daily == "NIFTYBEES").astype(float)
weights["GOLDBEES"] = (alloc_daily == "GOLDBEES").astype(float)

switch_mask = alloc_daily.ne(alloc_daily.shift(1))
switch_mask.iloc[0] = True
target_on_switch = weights.where(switch_mask, np.nan)

# Execute with targetpercent and cash_sharing
price_df = pd.DataFrame({
    "NIFTYBEES": panel.loc[alloc_daily.index, "open_NIFTYBEES"],
    "GOLDBEES": panel.loc[alloc_daily.index, "open_GOLDBEES"],
})

pf = vbt.Portfolio.from_orders(
    close=price_df,
    size=target_on_switch,
    size_type="targetpercent",
    fees=0.0025,
    init_cash=1_000_000,
    cash_sharing=True,
    call_seq="auto",
    freq="1D",
)
```

---

## Long + Short Backtesting

Use `short_entries` and `short_exits` for simultaneous long/short:

```python
# Long + Short (both directions)
pf_both = vbt.Portfolio.from_signals(
    close,
    entries=entries_long,
    exits=exits_long,
    short_entries=entries_short,
    short_exits=exits_short,
    init_cash=30_00_000,
    size=20_00_000,
    size_type="value",
    fees=0.0003,
    min_size=lot_size,
    size_granularity=lot_size,
    freq="1h",
)
# Note: direction="both" is ignored when short_entries/short_exits are provided
```

### Compare Long-Only vs Short-Only vs Both

```python
common_kwargs = dict(
    init_cash=1_000_000,
    size=500_000,
    size_type="value",
    fees=0.00022,
    freq="5min",
)

EMPTY = pd.Series(False, index=close.index)

pf_long = vbt.Portfolio.from_signals(close, entries=LE, exits=LX,
                                      direction="longonly", **common_kwargs)
pf_short = vbt.Portfolio.from_signals(close, short_entries=SE, short_exits=SX,
                                       direction="shortonly", **common_kwargs)
pf_both = vbt.Portfolio.from_signals(close, entries=LE, exits=LX,
                                      short_entries=SE, short_exits=SX, **common_kwargs)

# Side-by-side comparison
stats = pd.concat([
    pf_long.stats().to_frame("Long Only"),
    pf_short.stats().to_frame("Short Only"),
    pf_both.stats().to_frame("Both"),
], axis=1)
print(stats)
```

---

## Optimization Heatmap Visualization

```python
import plotly.graph_objects as go

# Pivot results for heatmap (from loop-based optimization)
pivot_return = results_df.pivot_table(
    values='total_return',
    index='long_span',
    columns='short_span',
    aggfunc='first',
)

fig = go.Figure(data=go.Heatmap(
    z=pivot_return.values * 100,
    x=pivot_return.columns,
    y=pivot_return.index,
    colorscale='RdYlGn',
    text=np.round(pivot_return.values * 100, 1),
    texttemplate='%{text}%',
    textfont={"size": 8},
    colorbar=dict(title="Return %"),
))
fig.update_layout(
    title="EMA Crossover Optimization - Total Return Heatmap",
    xaxis_title="Fast EMA Period",
    yaxis_title="Slow EMA Period",
    template="plotly_dark",
    height=800,
    width=800,
)
fig.show()
```

---

## Consecutive Wins/Losses Analysis

```python
def analyze_consecutive_trades(pf):
    """Analyze max consecutive wins and losses from a portfolio."""
    trades_df = pf.trades.records_readable
    if len(trades_df) == 0:
        return {}

    pnl_list = ((trades_df['Exit Price'] - trades_df['Entry Price']) > 0).tolist()

    consecutive_wins, consecutive_losses = [], []
    current_wins, current_losses = 0, 0

    for is_win in pnl_list:
        if is_win:
            if current_losses > 0:
                consecutive_losses.append(current_losses)
                current_losses = 0
            current_wins += 1
        else:
            if current_wins > 0:
                consecutive_wins.append(current_wins)
                current_wins = 0
            current_losses += 1

    if current_wins > 0:
        consecutive_wins.append(current_wins)
    if current_losses > 0:
        consecutive_losses.append(current_losses)

    return {
        'max_consecutive_wins': max(consecutive_wins) if consecutive_wins else 0,
        'max_consecutive_losses': max(consecutive_losses) if consecutive_losses else 0,
        'avg_consecutive_wins': np.mean(consecutive_wins) if consecutive_wins else 0,
        'avg_consecutive_losses': np.mean(consecutive_losses) if consecutive_losses else 0,
    }
```

---

## Full VectorBT Plot Pack (7-Panel)

```python
fig = pf.plot(
    subplots=[
        "value",          # equity curve
        "underwater",     # % drawdown over time
        "drawdowns",      # top-N drawdown ranges
        "orders",         # buy/sell markers
        "trades",         # entry/exit lines
        "net_exposure",   # net exposure
        "cash",           # cash curve
    ],
    make_subplots_kwargs=dict(
        rows=7, cols=1, shared_xaxes=True, vertical_spacing=0.04,
        row_heights=[0.25, 0.12, 0.12, 0.16, 0.12, 0.12, 0.11],
    ),
    template="plotly_dark",
    title="Strategy Backtest Results",
)
fig.show()
```

---

## Stop Loss Variations

```python
# Fixed stop loss + take profit
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    sl_stop=0.05, tp_stop=0.10,          # 5% SL, 10% TP
    fees=0.0003, init_cash=30_00_000, freq="1D",
)

# Trailing stop loss (follows price up, exits on pullback)
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    sl_trail=0.05,                        # 5% trailing stop
    fees=0.0003, init_cash=30_00_000, freq="1D",
)
```
