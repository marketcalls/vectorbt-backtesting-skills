---
name: strategy-compare
description: Compare multiple strategies or directions (long vs short vs both) on the same symbol. Generates side-by-side stats table.
argument-hint: "[symbol] [strategies...]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

Create a strategy comparison script.

## Arguments

Parse `$ARGUMENTS` as: symbol followed by strategy names

- `$0` = symbol (e.g., SBIN, RELIANCE, NIFTY)
- Remaining args = strategies to compare (e.g., ema-crossover rsi donchian)

If only a symbol is given with no strategies, compare: ema-crossover, rsi, donchian, supertrend.
If "long-vs-short" is one of the strategies, compare longonly vs shortonly vs both for the first real strategy.

## Instructions

1. Read the vectorbt-expert skill for reference patterns
2. Create a `.py` file in `D:\QuantFlow 3\Day17\backtesting\` named `{symbol}_strategy_comparison.py`
3. The script must:
   - Fetch data once via OpenAlgo
   - Run each strategy on the same data
   - Collect `pf.stats()` from each into a side-by-side DataFrame
   - Print the comparison table
   - Plot overlaid equity curves for all strategies using Plotly
   - Save comparison to CSV
4. Never use icons/emojis in code or logger output

## Example Usage

`/strategy-compare RELIANCE ema-crossover rsi donchian`
`/strategy-compare SBIN long-vs-short ema-crossover`
