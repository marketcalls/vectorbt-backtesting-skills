---
name: vectorbt-expert
description: VectorBT backtesting expert. Use when user asks to backtest strategies, create entry/exit signals, analyze portfolio performance, optimize parameters, fetch historical data, use VectorBT/vectorbt, compare strategies, position sizing, equity curves, drawdown charts, or trade analysis. Also triggers for openalgo.ta helpers (exrem, crossover, crossunder, flip, donchian, supertrend).
user-invocable: false
---

# VectorBT Backtesting Expert Skill

## Environment

- Python with vectorbt, pandas, numpy, plotly
- Data sources: OpenAlgo (Indian markets), yfinance (US/Global), CCXT (Crypto), custom providers
- API keys loaded from `.env` via `python-dotenv` — never hardcode keys
- Technical indicators: **TA-Lib** (ALWAYS - never use VectorBT built-in indicators)
- Specialty indicators: `openalgo.ta` for Supertrend, Donchian, Ichimoku, HMA, KAMA, ALMA, ZLEMA, VWMA
- Signal cleaning: `openalgo.ta` for exrem, crossover, crossunder, flip
- Fee model: Zerodha brokerage calculator values with Rs 20/order
- Benchmark: NIFTY 50 via OpenAlgo (`NSE_INDEX`) by default
- Charts: Plotly with `template="plotly_dark"`
- Environment variables loaded from `.env` file in the script directory
- Scripts go in `backtesting/{strategy_name}/` directories
- Never use icons/emojis in code or logger output

## Critical Rules

1. **ALWAYS use TA-Lib** for ALL technical indicators (EMA, SMA, RSI, MACD, BBANDS, ATR, ADX, STDDEV, MOM). NEVER use `vbt.MA.run()`, `vbt.RSI.run()`, or any VectorBT built-in indicator.
2. **Use OpenAlgo ta** for indicators NOT in TA-Lib: Supertrend, Donchian, Ichimoku, HMA, KAMA, ALMA, ZLEMA, VWMA.
3. **Use OpenAlgo ta** for signal utilities: `ta.exrem()`, `ta.crossover()`, `ta.crossunder()`, `ta.flip()`.
4. **Always clean signals** with `ta.exrem()` after generating raw buy/sell signals. Always `.fillna(False)` before exrem.
5. **Market-specific fees**: India=Zerodha ([indian-market-costs](rules/indian-market-costs.md)), US=IBKR ([us-market-costs](rules/us-market-costs.md)), Crypto=Binance ([crypto-market-costs](rules/crypto-market-costs.md)). Auto-select based on user's market.
6. **Default benchmarks**: India=NIFTY via OpenAlgo, US=S&P 500 (`^GSPC`), Crypto=Bitcoin (`BTC-USD`). See [data-fetching](rules/data-fetching.md) Market Selection Guide.
7. **Always produce** a Strategy vs Benchmark comparison table after every backtest.
8. **Always explain** the backtest report in plain language so even normal traders understand risk and strength.
9. **Plotly candlestick charts** must use `xaxis type="category"` to avoid weekend gaps.
10. **Whole shares**: Always set `min_size=1, size_granularity=1` for equities.

## Modular Rule Files

Detailed reference for each topic is in `rules/`:

| Rule File | Topic |
|-----------|-------|
| [data-fetching](rules/data-fetching.md) | OpenAlgo (India), yfinance (US), CCXT (Crypto), custom providers, .env setup |
| [simulation-modes](rules/simulation-modes.md) | from_signals, from_orders, from_holding, direction types |
| [position-sizing](rules/position-sizing.md) | Amount/Value/Percent/TargetPercent sizing |
| [indicators-signals](rules/indicators-signals.md) | TA-Lib indicator reference, signal generation |
| [openalgo-ta-helpers](rules/openalgo-ta-helpers.md) | OpenAlgo ta: exrem, crossover, Supertrend, Donchian, Ichimoku, MAs |
| [stop-loss-take-profit](rules/stop-loss-take-profit.md) | Fixed SL, TP, trailing stop |
| [parameter-optimization](rules/parameter-optimization.md) | Broadcasting and loop-based optimization |
| [performance-analysis](rules/performance-analysis.md) | Stats, metrics, benchmark comparison, CAGR |
| [plotting](rules/plotting.md) | Candlestick (category x-axis), VectorBT plots, custom Plotly |
| [indian-market-costs](rules/indian-market-costs.md) | Zerodha fee model by segment |
| [us-market-costs](rules/us-market-costs.md) | IBKR fee model (stocks, options, futures) |
| [crypto-market-costs](rules/crypto-market-costs.md) | Binance fee model (spot, USDT-M, COIN-M futures) |
| [futures-backtesting](rules/futures-backtesting.md) | Lot sizes (SEBI revised Dec 2025), value sizing |
| [long-short-trading](rules/long-short-trading.md) | Simultaneous long/short, direction comparison |
| [csv-data-resampling](rules/csv-data-resampling.md) | Loading CSV, resampling with Indian market alignment |
| [walk-forward](rules/walk-forward.md) | Walk-forward analysis, WFE ratio |
| [robustness-testing](rules/robustness-testing.md) | Monte Carlo, noise test, parameter sensitivity, delay test |
| [pitfalls](rules/pitfalls.md) | Common mistakes and checklist before going live |
| [strategy-catalog](rules/strategy-catalog.md) | Strategy reference with code snippets |
| [quantstats-tearsheet](rules/quantstats-tearsheet.md) | QuantStats HTML reports, metrics, plots, Monte Carlo |

## Strategy Templates (in rules/assets/)

Production-ready scripts with Zerodha fees, NIFTY benchmark, comparison table, and plain-language report:

| Template | Path | Description |
|----------|------|-------------|
| EMA Crossover | `assets/ema_crossover/backtest.py` | EMA 10/20 crossover |
| RSI | `assets/rsi/backtest.py` | RSI(14) oversold/overbought |
| Donchian | `assets/donchian/backtest.py` | Donchian channel breakout |
| Supertrend | `assets/supertrend/backtest.py` | Supertrend with intraday sessions |
| MACD | `assets/macd/backtest.py` | MACD signal-candle breakout |
| SDA2 | `assets/sda2/backtest.py` | SDA2 trend following |
| Momentum | `assets/momentum/backtest.py` | Double momentum (MOM + MOM-of-MOM) |
| Dual Momentum | `assets/dual_momentum/backtest.py` | Quarterly ETF rotation |
| Buy & Hold | `assets/buy_hold/backtest.py` | Static multi-asset allocation |
| RSI Accumulation | `assets/rsi_accumulation/backtest.py` | Weekly RSI slab-wise accumulation |
| Walk-Forward | `assets/walk_forward/template.py` | Walk-forward analysis template |
| Realistic Costs | `assets/realistic_costs/template.py` | Transaction cost impact comparison |

## Quick Template: Standard Backtest Script

```python
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import talib as tl
import vectorbt as vbt
from dotenv import load_dotenv
from openalgo import api, ta

# --- Config ---
script_dir = Path(__file__).resolve().parent
load_dotenv(dotenv_path=script_dir / ".env", override=False)

SYMBOL = "SBIN"
EXCHANGE = "NSE"
INTERVAL = "D"
INIT_CASH = 1_000_000
FEES = 0.00111              # Zerodha delivery equity
FIXED_FEES = 20             # Rs 20 per order
ALLOCATION = 0.75
BENCHMARK_SYMBOL = "NIFTY"
BENCHMARK_EXCHANGE = "NSE_INDEX"

# --- Fetch Data ---
client = api(
    api_key=os.getenv("OPENALGO_API_KEY"),
    host=os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000"),
)

end_date = datetime.now().date()
start_date = end_date - timedelta(days=365 * 3)

df = client.history(
    symbol=SYMBOL, exchange=EXCHANGE, interval=INTERVAL,
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
)
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
else:
    df.index = pd.to_datetime(df.index)
df = df.sort_index()
if df.index.tz is not None:
    df.index = df.index.tz_convert(None)

close = df["close"]

# --- Strategy: EMA Crossover (TA-Lib) ---
ema_fast = pd.Series(tl.EMA(close.values, timeperiod=10), index=close.index)
ema_slow = pd.Series(tl.EMA(close.values, timeperiod=20), index=close.index)

buy_raw = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
sell_raw = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))

# --- Backtest ---
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    init_cash=INIT_CASH, size=ALLOCATION, size_type="percent",
    fees=FEES, fixed_fees=FIXED_FEES, direction="longonly",
    min_size=1, size_granularity=1, freq="1D",
)

# --- Benchmark ---
df_bench = client.history(
    symbol=BENCHMARK_SYMBOL, exchange=BENCHMARK_EXCHANGE, interval=INTERVAL,
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
)
if "timestamp" in df_bench.columns:
    df_bench["timestamp"] = pd.to_datetime(df_bench["timestamp"])
    df_bench = df_bench.set_index("timestamp")
else:
    df_bench.index = pd.to_datetime(df_bench.index)
df_bench = df_bench.sort_index()
if df_bench.index.tz is not None:
    df_bench.index = df_bench.index.tz_convert(None)
bench_close = df_bench["close"].reindex(close.index).ffill().bfill()
pf_bench = vbt.Portfolio.from_holding(bench_close, init_cash=INIT_CASH, fees=FEES, freq="1D")

# --- Results ---
print(pf.stats())

# --- Strategy vs Benchmark ---
comparison = pd.DataFrame({
    "Strategy": [
        f"{pf.total_return() * 100:.2f}%", f"{pf.sharpe_ratio():.2f}",
        f"{pf.sortino_ratio():.2f}", f"{pf.max_drawdown() * 100:.2f}%",
        f"{pf.trades.win_rate() * 100:.1f}%", f"{pf.trades.count()}",
        f"{pf.trades.profit_factor():.2f}",
    ],
    f"Benchmark ({BENCHMARK_SYMBOL})": [
        f"{pf_bench.total_return() * 100:.2f}%", f"{pf_bench.sharpe_ratio():.2f}",
        f"{pf_bench.sortino_ratio():.2f}", f"{pf_bench.max_drawdown() * 100:.2f}%",
        "-", "-", "-",
    ],
}, index=["Total Return", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown",
          "Win Rate", "Total Trades", "Profit Factor"])
print(comparison.to_string())

# --- Explain ---
print(f"* Total Return: {pf.total_return() * 100:.2f}% vs NIFTY {pf_bench.total_return() * 100:.2f}%")
print(f"* Max Drawdown: {pf.max_drawdown() * 100:.2f}%")
print(f"  -> On Rs {INIT_CASH:,}, worst temporary loss = Rs {abs(pf.max_drawdown()) * INIT_CASH:,.0f}")

# --- Plot ---
fig = pf.plot(subplots=['value', 'underwater', 'cum_returns'], template="plotly_dark")
fig.show()

# --- Export ---
pf.positions.records_readable.to_csv(script_dir / f"{SYMBOL}_trades.csv", index=False)
```
