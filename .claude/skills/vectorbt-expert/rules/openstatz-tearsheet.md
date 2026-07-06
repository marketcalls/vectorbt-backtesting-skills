---
name: openstatz-tearsheet
description: OpenStatz tearsheet integration - HTML reports, metrics, plots, Monte Carlo simulations for portfolio analytics. OpenStatz replaces QuantStats project-wide.
metadata:
  tags: openstatz, quantstats, tearsheet, report, html, metrics, plots, monte-carlo, analytics, risk
---

# OpenStatz Tearsheet Integration

**OpenStatz is the required tearsheet library for this project - never use QuantStats.** OpenStatz is a modern, actively-maintained rebuild of QuantStats with an enforced numerical-parity contract (`rtol=1e-9`) - same metrics, same plots, same HTML report layout, same function names under a different top-level package. Always offer to generate an OpenStatz tearsheet after every backtest.

## Installation

```bash
pip install openstatz --upgrade
```

## Import Alias: Use `ostz`, Not `os`

OpenStatz's own docs suggest `import openstatz as os`, but every backtest script in this project already does `import os` for `os.getenv()` (API keys) and path handling. **Always alias it as `ostz`** to avoid shadowing the stdlib `os` module:

```python
import openstatz as ostz
```

(The QuantStats-compatible alias `qs` also works if you are porting old code, but prefer `ostz` in new scripts for clarity.)

## Basic Usage with VectorBT

After running a VectorBT backtest, extract returns and generate a tearsheet:

```python
import openstatz as ostz

# Extract daily returns from VectorBT portfolio
strategy_returns = pf.returns()

# If returns have timezone, remove it
if strategy_returns.index.tz is not None:
    strategy_returns.index = strategy_returns.index.tz_convert(None)

# Generate full HTML tearsheet
ostz.reports.html(strategy_returns, benchmark="^NSEI", output="tearsheet.html",
                   title="Strategy Tearsheet")
print("Tearsheet saved to tearsheet.html")
```

## Benchmark Options

```python
# Indian Market - NIFTY 50
ostz.reports.html(returns, benchmark="^NSEI", output="tearsheet.html")

# US Market - S&P 500
ostz.reports.html(returns, benchmark="SPY", output="tearsheet.html")

# Custom benchmark from OpenAlgo (convert to returns first)
bench_returns = bench_close.pct_change().dropna()
bench_returns = bench_returns.reindex(strategy_returns.index).fillna(0)
ostz.reports.html(strategy_returns, benchmark=bench_returns, output="tearsheet.html")
```

## Report Types

```python
import openstatz as ostz

# 1. Full HTML tearsheet (RECOMMENDED - most comprehensive)
ostz.reports.html(returns, benchmark="^NSEI", output="tearsheet.html",
                   title="EMA Crossover - SBIN")

# 2. Full metrics + plots to console
ostz.reports.full(returns, benchmark="^NSEI")

# 3. Basic metrics + plots to console
ostz.reports.basic(returns)

# 4. Metrics only (no plots)
ostz.reports.metrics(returns, mode="full")       # Full metrics
ostz.reports.metrics(returns, mode="basic")      # Basic metrics

# 5. Plots only (no metrics)
ostz.reports.plots(returns, mode="full")
ostz.reports.plots(returns, mode="basic")
```

## Key Metrics (ostz.stats)

```python
import openstatz as ostz

returns = pf.returns()

# Performance
ostz.stats.cagr(returns)                          # CAGR
ostz.stats.sharpe(returns)                        # Sharpe Ratio
ostz.stats.sortino(returns)                       # Sortino Ratio
ostz.stats.adjusted_sortino(returns)              # Adjusted Sortino
ostz.stats.calmar(returns)                        # Calmar Ratio

# Risk
ostz.stats.max_drawdown(returns)                  # Max Drawdown
ostz.stats.volatility(returns)                    # Annualized Volatility
ostz.stats.value_at_risk(returns)                 # VaR (95%)
ostz.stats.conditional_value_at_risk(returns)     # CVaR / Expected Shortfall
ostz.stats.ulcer_index(returns)                   # Ulcer Index

# Trade Analysis (period-based)
ostz.stats.win_rate(returns)                      # Win Rate (% positive days)
ostz.stats.profit_factor(returns)                 # Profit Factor
ostz.stats.payoff_ratio(returns)                  # Payoff Ratio
ostz.stats.consecutive_wins(returns)              # Max Consecutive Wins
ostz.stats.consecutive_losses(returns)            # Max Consecutive Losses

# Other
ostz.stats.best(returns)                          # Best day/period
ostz.stats.worst(returns)                         # Worst day/period
ostz.stats.avg_win(returns)                       # Average winning day
ostz.stats.avg_loss(returns)                      # Average losing day
ostz.stats.kelly_criterion(returns)               # Kelly Criterion
ostz.stats.risk_of_ruin(returns)                  # Risk of Ruin
ostz.stats.information_ratio(returns, benchmark)  # Information Ratio
ostz.stats.gain_to_pain_ratio(returns)            # Gain to Pain Ratio
ostz.stats.tail_ratio(returns)                    # Tail Ratio
ostz.stats.outlier_win_ratio(returns)             # Outlier Win Ratio
ostz.stats.outlier_loss_ratio(returns)            # Outlier Loss Ratio
```

## Key Plots (ostz.plots)

```python
import openstatz as ostz

returns = pf.returns()

# Performance
ostz.plots.returns(returns, benchmark="^NSEI", show=True)
ostz.plots.log_returns(returns, benchmark="^NSEI", show=True)
ostz.plots.yearly_returns(returns, benchmark="^NSEI", show=True)

# Risk
ostz.plots.drawdown(returns, show=True)
ostz.plots.drawdowns_periods(returns, show=True)
ostz.plots.distribution(returns, show=True)
ostz.plots.histogram(returns, show=True)

# Rolling
ostz.plots.rolling_sharpe(returns, show=True)
ostz.plots.rolling_sortino(returns, show=True)
ostz.plots.rolling_volatility(returns, show=True)
ostz.plots.rolling_beta(returns, benchmark="^NSEI", show=True)

# Summary
ostz.plots.snapshot(returns, title="Strategy Snapshot", show=True)
ostz.plots.monthly_heatmap(returns, show=True)
ostz.plots.daily_returns(returns, show=True)

# Monte Carlo
ostz.plots.montecarlo(returns, sims=1000, show=True)
ostz.plots.montecarlo_distribution(returns, sims=1000, show=True)
```

## Monte Carlo Simulations

```python
import openstatz as ostz

returns = pf.returns()

# Run Monte Carlo simulation
mc = ostz.stats.montecarlo(returns, sims=1000, bust=-0.20, goal=0.50)

# Probabilities
print(f"Bust probability (>20% loss): {mc.bust_probability:.1%}")
print(f"Goal probability (>50% gain): {mc.goal_probability:.1%}")

# Plot Monte Carlo
mc.plot()
```

## Complete Backtest Integration Template

Add this block at the end of every backtest script:

```python
# --- OpenStatz Tearsheet ---
try:
    import openstatz as ostz

    strategy_returns = pf.returns()
    if strategy_returns.index.tz is not None:
        strategy_returns.index = strategy_returns.index.tz_convert(None)

    tearsheet_file = script_dir / f"{SYMBOL}_tearsheet.html"
    ostz.reports.html(
        strategy_returns,
        benchmark="^NSEI",
        output=str(tearsheet_file),
        title=f"{SYMBOL} - Strategy Tearsheet",
    )
    print(f"\nOpenStatz tearsheet saved to {tearsheet_file}")

    # Quick Monte Carlo
    mc = ostz.stats.montecarlo(strategy_returns, sims=1000, bust=-0.10, goal=0.30)
    print(f"Monte Carlo (1000 sims): Bust prob={mc.bust_probability:.1%}, Goal prob={mc.goal_probability:.1%}")

except ImportError:
    print("\nOpenStatz not installed. Run: pip install openstatz")
    print("Skipping tearsheet generation.")
```

## Important Notes

- OpenStatz analyzes **return series** (daily returns), not discrete trade data
- Win Rate in OpenStatz = percentage of **days** with positive returns (not trade-level)
- For trade-level metrics, use VectorBT's `pf.trades.win_rate()` and `pf.trades.profit_factor()`
- Both metrics are valid - they measure different things
- Always remove timezone from returns index before passing to OpenStatz
- For Indian market benchmark, use `^NSEI` (NIFTY 50 on Yahoo Finance)
- For US market benchmark, use `SPY` (S&P 500 ETF)
- Never alias the import as `os` in a backtest script - it shadows the stdlib `os` module already used for `os.getenv()`
- If porting an existing QuantStats script instead of writing a new one, `openstatz.compat.install_quantstats_shim()` followed by `import quantstats as qs` lets old `qs.*` code run unchanged against the OpenStatz engine - but new scripts should just call `openstatz` directly
