---
name: quantstats-tearsheet
description: QuantStats tearsheet integration - HTML reports, metrics, plots, Monte Carlo simulations for portfolio analytics
metadata:
  tags: quantstats, tearsheet, report, html, metrics, plots, monte-carlo, analytics, risk
---

# QuantStats Tearsheet Integration

QuantStats generates professional portfolio analytics reports. Always offer to generate a QuantStats tearsheet after every backtest.

## Installation

```bash
pip install quantstats --upgrade
```

## Basic Usage with VectorBT

After running a VectorBT backtest, extract returns and generate a tearsheet:

```python
import quantstats as qs

# Extract daily returns from VectorBT portfolio
strategy_returns = pf.returns()

# If returns have timezone, remove it
if strategy_returns.index.tz is not None:
    strategy_returns.index = strategy_returns.index.tz_convert(None)

# Generate full HTML tearsheet
qs.reports.html(strategy_returns, benchmark="^NSEI", output="tearsheet.html",
                title="Strategy Tearsheet")
print("Tearsheet saved to tearsheet.html")
```

## Benchmark Options

```python
# Indian Market - NIFTY 50
qs.reports.html(returns, benchmark="^NSEI", output="tearsheet.html")

# US Market - S&P 500
qs.reports.html(returns, benchmark="SPY", output="tearsheet.html")

# Custom benchmark from OpenAlgo (convert to returns first)
bench_returns = bench_close.pct_change().dropna()
bench_returns = bench_returns.reindex(strategy_returns.index).fillna(0)
qs.reports.html(strategy_returns, benchmark=bench_returns, output="tearsheet.html")
```

## Report Types

```python
import quantstats as qs

# 1. Full HTML tearsheet (RECOMMENDED - most comprehensive)
qs.reports.html(returns, benchmark="^NSEI", output="tearsheet.html",
                title="EMA Crossover - SBIN")

# 2. Full metrics + plots to console
qs.reports.full(returns, benchmark="^NSEI")

# 3. Basic metrics + plots to console
qs.reports.basic(returns)

# 4. Metrics only (no plots)
qs.reports.metrics(returns, mode="full")       # Full metrics
qs.reports.metrics(returns, mode="basic")      # Basic metrics

# 5. Plots only (no metrics)
qs.reports.plots(returns, mode="full")
qs.reports.plots(returns, mode="basic")
```

## Key Metrics (qs.stats)

```python
import quantstats as qs

returns = pf.returns()

# Performance
qs.stats.cagr(returns)                          # CAGR
qs.stats.sharpe(returns)                        # Sharpe Ratio
qs.stats.sortino(returns)                       # Sortino Ratio
qs.stats.adjusted_sortino(returns)              # Adjusted Sortino
qs.stats.calmar(returns)                        # Calmar Ratio

# Risk
qs.stats.max_drawdown(returns)                  # Max Drawdown
qs.stats.volatility(returns)                    # Annualized Volatility
qs.stats.value_at_risk(returns)                 # VaR (95%)
qs.stats.conditional_value_at_risk(returns)     # CVaR / Expected Shortfall
qs.stats.ulcer_index(returns)                   # Ulcer Index

# Trade Analysis (period-based)
qs.stats.win_rate(returns)                      # Win Rate (% positive days)
qs.stats.profit_factor(returns)                 # Profit Factor
qs.stats.payoff_ratio(returns)                  # Payoff Ratio
qs.stats.consecutive_wins(returns)              # Max Consecutive Wins
qs.stats.consecutive_losses(returns)            # Max Consecutive Losses

# Other
qs.stats.best(returns)                          # Best day/period
qs.stats.worst(returns)                         # Worst day/period
qs.stats.avg_win(returns)                       # Average winning day
qs.stats.avg_loss(returns)                      # Average losing day
qs.stats.kelly_criterion(returns)               # Kelly Criterion
qs.stats.risk_of_ruin(returns)                  # Risk of Ruin
qs.stats.recovery_factor(returns)               # Recovery Factor
qs.stats.information_ratio(returns, benchmark)  # Information Ratio
qs.stats.gain_to_pain_ratio(returns)            # Gain to Pain Ratio
qs.stats.tail_ratio(returns)                    # Tail Ratio
qs.stats.common_sense_ratio(returns)            # Common Sense Ratio
qs.stats.outlier_win_ratio(returns)             # Outlier Win Ratio
qs.stats.outlier_loss_ratio(returns)            # Outlier Loss Ratio
```

## Key Plots (qs.plots)

```python
import quantstats as qs

returns = pf.returns()

# Performance
qs.plots.returns(returns, benchmark="^NSEI", show=True)
qs.plots.log_returns(returns, benchmark="^NSEI", show=True)
qs.plots.yearly_returns(returns, benchmark="^NSEI", show=True)

# Risk
qs.plots.drawdown(returns, show=True)
qs.plots.drawdowns_periods(returns, show=True)
qs.plots.distribution(returns, show=True)
qs.plots.histogram(returns, show=True)

# Rolling
qs.plots.rolling_sharpe(returns, show=True)
qs.plots.rolling_sortino(returns, show=True)
qs.plots.rolling_volatility(returns, show=True)
qs.plots.rolling_beta(returns, benchmark="^NSEI", show=True)

# Summary
qs.plots.snapshot(returns, title="Strategy Snapshot", show=True)
qs.plots.monthly_heatmap(returns, show=True)
qs.plots.daily_returns(returns, show=True)

# Monte Carlo
qs.plots.montecarlo(returns, sims=1000, show=True)
qs.plots.montecarlo_distribution(returns, sims=1000, show=True)
```

## Monte Carlo Simulations

```python
import quantstats as qs

returns = pf.returns()

# Run Monte Carlo simulation
mc = qs.stats.montecarlo(returns, sims=1000, bust=-0.20, goal=0.50)

# Probabilities
print(f"Bust probability (>20% loss): {mc.bust_probability:.1%}")
print(f"Goal probability (>50% gain): {mc.goal_probability:.1%}")

# Plot Monte Carlo
mc.plot()

```

## Complete Backtest Integration Template

Add this block at the end of every backtest script:

```python
# --- QuantStats Tearsheet ---
try:
    import quantstats as qs

    strategy_returns = pf.returns()
    if strategy_returns.index.tz is not None:
        strategy_returns.index = strategy_returns.index.tz_convert(None)

    tearsheet_file = script_dir / f"{SYMBOL}_tearsheet.html"
    qs.reports.html(
        strategy_returns,
        benchmark="^NSEI",
        output=str(tearsheet_file),
        title=f"{SYMBOL} - Strategy Tearsheet",
    )
    print(f"\nQuantStats tearsheet saved to {tearsheet_file}")

    # Quick Monte Carlo
    mc = qs.stats.montecarlo(strategy_returns, sims=1000, bust=-0.10, goal=0.30)
    print(f"Monte Carlo (1000 sims): Bust prob={mc.bust_probability:.1%}, Goal prob={mc.goal_probability:.1%}")

except ImportError:
    print("\nQuantStats not installed. Run: pip install quantstats")
    print("Skipping tearsheet generation.")
```

## Important Notes

- QuantStats analyzes **return series** (daily returns), not discrete trade data
- Win Rate in QuantStats = percentage of **days** with positive returns (not trade-level)
- For trade-level metrics, use VectorBT's `pf.trades.win_rate()` and `pf.trades.profit_factor()`
- Both metrics are valid - they measure different things
- Always remove timezone from returns index before passing to QuantStats
- For Indian market benchmark, use `^NSEI` (NIFTY 50 on Yahoo Finance)
- For US market benchmark, use `SPY` (S&P 500 ETF)
