---
name: backtest
description: Quick backtest a strategy on a symbol. Creates a complete .py script with data fetch, signals, backtest, stats, and plots.
argument-hint: "[strategy] [symbol] [exchange] [interval]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Create a complete VectorBT backtest script for the user.

## Arguments

Parse `$ARGUMENTS` as: strategy symbol exchange interval

- `$0` = strategy name (e.g., ema-crossover, rsi, donchian, supertrend, macd, sda2, momentum)
- `$1` = symbol (e.g., SBIN, RELIANCE, NIFTY). Default: SBIN
- `$2` = exchange (e.g., NSE, NFO). Default: NSE
- `$3` = interval (e.g., D, 1h, 5m). Default: D

If no arguments, ask the user which strategy they want.

## Instructions

1. Read the vectorbt-expert skill for reference patterns
2. Create a `.py` file in `D:\QuantFlow 3\Day17\backtesting\` named `{symbol}_{strategy}_backtest.py`
3. The script must:
   - Load `.env` from the script directory for OpenAlgo credentials
   - Fetch data via `client.history()` from OpenAlgo
   - Implement the requested strategy using vectorbt + openalgo.ta helpers
   - Use `ta.exrem()` to clean duplicate signals
   - Run `vbt.Portfolio.from_signals()` with proper sizing (percent for equities, value for futures)
   - Print full `pf.stats()`
   - Print key metrics: total return, sharpe, max drawdown, win rate, trade count
   - Plot equity curve + drawdown (`subplots=['value', 'underwater', 'cum_returns']`)
   - Export trades to CSV
4. Never use icons/emojis in code or logger output
5. For futures symbols (NIFTY, BANKNIFTY), use lot-size-aware sizing with `min_size` and `size_granularity`

## Available Strategies

| Strategy | Keyword | Description |
|----------|---------|-------------|
| EMA Crossover | `ema-crossover` | Fast/slow EMA crossover |
| RSI | `rsi` | RSI oversold/overbought |
| Donchian Channel | `donchian` | Donchian channel breakout |
| Supertrend | `supertrend` | Supertrend indicator signals |
| MACD Breakout | `macd` | MACD zero-line signal candle breakout |
| SDA2 | `sda2` | SDA2 trend following channel |
| Momentum | `momentum` | Double momentum (MOM + MOM of MOM) |
| Dual Momentum | `dual-momentum` | Relative momentum between 2 ETFs |

## Example Usage

`/backtest ema-crossover RELIANCE NSE D`
`/backtest rsi SBIN`
`/backtest supertrend NIFTY NFO 5m`
