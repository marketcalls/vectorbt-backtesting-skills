---
name: optimize
description: Optimize strategy parameters using VectorBT. Tests parameter combinations and generates heatmaps.
argument-hint: "[strategy] [symbol] [exchange] [interval]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Create a parameter optimization script for a VectorBT strategy.

## Arguments

Parse `$ARGUMENTS` as: strategy symbol exchange interval

- `$0` = strategy name (e.g., ema-crossover, rsi, donchian). Default: ema-crossover
- `$1` = symbol (e.g., SBIN, RELIANCE, NIFTY). Default: SBIN
- `$2` = exchange (e.g., NSE, NFO). Default: NSE
- `$3` = interval (e.g., D, 1h, 5m). Default: D

If no arguments, ask the user which strategy to optimize.

## Instructions

1. Read the vectorbt-expert skill for reference patterns
2. Create a `.py` file in `D:\QuantFlow 3\Day17\backtesting\` named `{symbol}_{strategy}_optimize.py`
3. The script must:
   - Load `.env` and fetch data via OpenAlgo `client.history()`
   - Define sensible parameter ranges for the chosen strategy
   - Use loop-based optimization (not broadcasting) to collect multiple metrics per combo
   - Track: total_return, sharpe_ratio, max_drawdown, trade_count for each combination
   - Use `tqdm` for progress bars
   - Find best parameters by total return AND by minimum drawdown
   - Print top 10 results for both criteria
   - Generate Plotly heatmap of total return across parameter grid
   - Generate Plotly heatmap of max drawdown across parameter grid
   - Save results to CSV
4. Never use icons/emojis in code or logger output
5. For futures symbols, use lot-size-aware sizing

## Default Parameter Ranges

| Strategy | Parameter 1 | Parameter 2 |
|----------|------------|-------------|
| ema-crossover | fast EMA: 5-50 | slow EMA: 10-60 |
| rsi | window: 5-30 | oversold: 20-40 |
| donchian | period: 5-50 | - |
| supertrend | period: 5-30 | multiplier: 1.0-5.0 |

## Example Usage

`/optimize ema-crossover RELIANCE NSE D`
`/optimize rsi SBIN`
