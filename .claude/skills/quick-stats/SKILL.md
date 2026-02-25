---
name: quick-stats
description: Quickly fetch data and print key backtest stats for a symbol with a default EMA crossover strategy. No file creation needed - runs inline in a notebook cell or prints to console.
argument-hint: "[symbol] [exchange] [interval]"
allowed-tools: Read, Bash, Glob, Grep
---

Generate a quick inline backtest and print stats. Do NOT create a file - output code directly for the user to run or execute in a notebook.

## Arguments

- `$0` = symbol (e.g., SBIN, RELIANCE). Default: SBIN
- `$1` = exchange. Default: NSE
- `$2` = interval. Default: D

## Output Format

Generate a single code block the user can paste into a Jupyter cell or run as a script. The code should:

1. Fetch data from OpenAlgo (or yfinance as fallback)
2. Run EMA 10/20 crossover
3. Print a compact results summary:

```
Symbol: SBIN | Exchange: NSE | Interval: D
Strategy: EMA 10/20 Crossover
Period: 2022-01-01 to 2025-02-25
-------------------------------------------
Total Return:    45.23%
Sharpe Ratio:    1.45
Sortino Ratio:   2.01
Max Drawdown:   -12.34%
Win Rate:        42.5%
Profit Factor:   1.67
Total Trades:    28
Avg Win:         3.2%
Avg Loss:       -1.8%
Best Trade:     15.2%
Worst Trade:    -8.1%
```

4. Show equity curve plot

## Example Usage

`/quick-stats RELIANCE`
`/quick-stats HDFCBANK NSE 1h`
