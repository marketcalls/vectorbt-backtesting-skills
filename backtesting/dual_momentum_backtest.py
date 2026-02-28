import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from openalgo import api

# --- Config ---
script_dir = Path(__file__).resolve().parent

SYMBOLS = ["NIFTYBEES", "GOLDBEES"]
EXCHANGE = "NSE"
INTERVAL = "D"
INIT_CASH = 10_00_000
FEES = 0.001          # 0.1%
ALLOCATION = 0.75     # 75% of portfolio per rebalance

# --- Fetch Data ---
client = api(
    api_key=os.getenv("OPENALGO_API_KEY", "your-api-key-here"),
    host=os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000"),
)

end_date = datetime.now().date()
start_date = "2018-01-01"

print(f"Fetching data for {SYMBOLS} ({EXCHANGE}) from {start_date} to {end_date}")

dfs = {}
for sym in SYMBOLS:
    df = client.history(
        symbol=sym,
        exchange=EXCHANGE,
        interval=INTERVAL,
        start_date=start_date,
        end_date=end_date.strftime("%Y-%m-%d"),
    )
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
    else:
        df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    dfs[sym] = df
    print(f"  {sym}: {len(df)} bars from {df.index[0].date()} to {df.index[-1].date()}")

# --- Build Panel ---
close_prices = pd.DataFrame({sym: dfs[sym]["close"] for sym in SYMBOLS})
open_prices = pd.DataFrame({sym: dfs[sym]["open"] for sym in SYMBOLS})

# Drop rows where either ETF has no data
close_prices = close_prices.dropna()
open_prices = open_prices.reindex(close_prices.index).ffill().bfill()

print(f"\nAligned data: {len(close_prices)} bars")

# --- Quarterly Returns & Winner Selection ---
# Resample to quarter-end close prices
quarterly_close = close_prices.resample("QE").last().dropna(how="all")

# Quarterly returns
quarterly_returns = quarterly_close.pct_change()
print("\n--- Quarterly Returns ---")
print(quarterly_returns.to_string(float_format="{:.2%}".format))

# Determine winner each quarter (previous quarter's outperformer)
winner = quarterly_returns.idxmax(axis=1)
print("\n--- Quarterly Winner (Previous Quarter Outperformer) ---")
for dt, sym in winner.items():
    ret_n = quarterly_returns.loc[dt, "NIFTYBEES"]
    ret_g = quarterly_returns.loc[dt, "GOLDBEES"]
    if pd.notna(ret_n) and pd.notna(ret_g):
        print(f"  {dt.date()}: {sym} (NIFTYBEES: {ret_n:.2%}, GOLDBEES: {ret_g:.2%})")

# --- Build Daily Allocation Weights ---
# After each quarter ends, invest in the winner for the next quarter
# Shift winner by 1 quarter so we use PREVIOUS quarter's winner
winner_shifted = winner.shift(1).dropna()

alloc_daily = pd.Series(index=close_prices.index, dtype="object")
for dt, sym in winner_shifted.items():
    # Find the next trading day after quarter end
    next_idx_pos = close_prices.index.searchsorted(dt, side="right")
    if next_idx_pos < len(close_prices.index):
        alloc_daily.loc[close_prices.index[next_idx_pos]] = sym

alloc_daily = alloc_daily.ffill()
alloc_daily = alloc_daily.loc[alloc_daily.first_valid_index():]

# Build target weight DataFrame
weights = pd.DataFrame(index=alloc_daily.index, columns=SYMBOLS, dtype=float)
weights["NIFTYBEES"] = np.where(alloc_daily == "NIFTYBEES", ALLOCATION, 0.0)
weights["GOLDBEES"] = np.where(alloc_daily == "GOLDBEES", ALLOCATION, 0.0)

# Only rebalance on switch days (when allocation changes)
switch_mask = alloc_daily.ne(alloc_daily.shift(1))
switch_mask.iloc[0] = True
target_on_switch = weights.where(switch_mask, np.nan)

rebalance_count = switch_mask.sum()
print(f"\nTotal rebalance events: {rebalance_count}")
print("\n--- Rebalance Schedule ---")
for dt in alloc_daily.index[switch_mask]:
    print(f"  {dt.date()}: Buy {alloc_daily.loc[dt]} ({ALLOCATION*100:.0f}%)")

# --- Backtest with VectorBT ---
price_df = open_prices.loc[alloc_daily.index]

pf = vbt.Portfolio.from_orders(
    close=price_df,
    size=target_on_switch,
    size_type="targetpercent",
    fees=FEES,
    init_cash=INIT_CASH,
    cash_sharing=True,
    call_seq="auto",
    group_by=True,
    freq="1D",
    min_size=1,
    size_granularity=1,
)

# --- Results ---
print("\n" + "=" * 60)
print("  Dual Momentum Backtest - NIFTYBEES vs GOLDBEES")
print("  Quarterly Rebalance | 75% Allocation | Long Only")
print("=" * 60)
print(pf.stats())

print("\n--- Key Metrics ---")
print(f"Total Return:    {pf.total_return() * 100:.2f}%")
print(f"Sharpe Ratio:    {pf.sharpe_ratio():.2f}")
print(f"Sortino Ratio:   {pf.sortino_ratio():.2f}")
print(f"Max Drawdown:    {pf.max_drawdown() * 100:.2f}%")

# --- Benchmark: NIFTY 50 Index ---
print("\nFetching NIFTY 50 index data for benchmark...")
df_nifty = client.history(
    symbol="NIFTY",
    exchange="NSE_INDEX",
    interval=INTERVAL,
    start_date=start_date,
    end_date=end_date.strftime("%Y-%m-%d"),
)
if "timestamp" in df_nifty.columns:
    df_nifty["timestamp"] = pd.to_datetime(df_nifty["timestamp"])
    df_nifty = df_nifty.set_index("timestamp")
else:
    df_nifty.index = pd.to_datetime(df_nifty.index)
df_nifty = df_nifty.sort_index()
nifty_close = df_nifty["close"].reindex(alloc_daily.index).ffill().bfill()
print(f"  NIFTY 50: {len(df_nifty)} bars loaded")

# Benchmark: Buy-and-Hold NIFTYBEES
pf_bench_bees = vbt.Portfolio.from_holding(
    close_prices.loc[alloc_daily.index, "NIFTYBEES"],
    init_cash=INIT_CASH, fees=FEES, freq="1D",
)

# Benchmark: Buy-and-Hold GOLDBEES
pf_bench_gold = vbt.Portfolio.from_holding(
    close_prices.loc[alloc_daily.index, "GOLDBEES"],
    init_cash=INIT_CASH, fees=FEES, freq="1D",
)

# Benchmark comparison table
print("\n--- Benchmark Comparison ---")
bench_stats = pd.DataFrame({
    "Dual Momentum": [
        f"{pf.total_return() * 100:.2f}%",
        f"{pf.sharpe_ratio():.2f}",
        f"{pf.sortino_ratio():.2f}",
        f"{pf.max_drawdown() * 100:.2f}%",
    ],
    "NIFTYBEES B&H": [
        f"{pf_bench_bees.total_return() * 100:.2f}%",
        f"{pf_bench_bees.sharpe_ratio():.2f}",
        f"{pf_bench_bees.sortino_ratio():.2f}",
        f"{pf_bench_bees.max_drawdown() * 100:.2f}%",
    ],
    "GOLDBEES B&H": [
        f"{pf_bench_gold.total_return() * 100:.2f}%",
        f"{pf_bench_gold.sharpe_ratio():.2f}",
        f"{pf_bench_gold.sortino_ratio():.2f}",
        f"{pf_bench_gold.max_drawdown() * 100:.2f}%",
    ],
}, index=["Total Return", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown"])
print(bench_stats.to_string())

# --- Plot: Strategy vs Benchmarks + Drawdown ---
equity = pf.value()
equity_bees = close_prices.loc[alloc_daily.index, "NIFTYBEES"]
equity_gold = close_prices.loc[alloc_daily.index, "GOLDBEES"]

# Normalize to cumulative returns
cum_strat = equity / equity.iloc[0] - 1
cum_bees = equity_bees / equity_bees.iloc[0] - 1
cum_gold = equity_gold / equity_gold.iloc[0] - 1
cum_nifty50 = nifty_close / nifty_close.iloc[0] - 1

# Drawdown
running_max = equity.cummax()
drawdown = equity / running_max - 1

# Highlight which ETF is held
hold_nifty = alloc_daily == "NIFTYBEES"
hold_gold = alloc_daily == "GOLDBEES"

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    row_heights=[0.50, 0.25, 0.25],
    vertical_spacing=0.06,
    subplot_titles=[
        "Cumulative Returns: Strategy vs Benchmarks",
        "Drawdown",
        "Current Holding",
    ],
)

# Row 1: Cumulative returns
fig.add_trace(go.Scatter(
    x=cum_strat.index, y=cum_strat.values,
    name="Dual Momentum", line=dict(color="#00d4aa", width=2.5),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_nifty50.index, y=cum_nifty50.values,
    name="NIFTY 50 Index", line=dict(color="#ff6688", width=1.5, dash="dash"),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_bees.index, y=cum_bees.values,
    name="NIFTYBEES (B&H)", line=dict(color="#4488ff", width=1, dash="dot"),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_gold.index, y=cum_gold.values,
    name="GOLDBEES (B&H)", line=dict(color="#ffaa00", width=1, dash="dot"),
), row=1, col=1)

# Row 2: Drawdown
fig.add_trace(go.Scatter(
    x=drawdown.index, y=drawdown.values,
    name="Drawdown", fill="tozeroy",
    line=dict(color="#ff4444", width=1),
), row=2, col=1)

# Row 3: Holding indicator (1 = NIFTYBEES, 0 = GOLDBEES)
holding_indicator = hold_nifty.astype(int)
fig.add_trace(go.Scatter(
    x=holding_indicator.index, y=holding_indicator.values,
    name="Holding", mode="lines",
    line=dict(color="#aa88ff", width=2, shape="hv"),
), row=3, col=1)

fig.update_yaxes(tickformat=".1%", side="right", row=1, col=1)
fig.update_yaxes(tickformat=".1%", side="right", row=2, col=1)
fig.update_yaxes(
    tickvals=[0, 1], ticktext=["GOLDBEES", "NIFTYBEES"],
    side="right", row=3, col=1,
)

fig.update_layout(
    template="plotly_dark",
    title="Dual Momentum: NIFTYBEES vs GOLDBEES vs NIFTY 50 (Quarterly Rebalance)",
    height=800,
    showlegend=True,
    legend=dict(x=0.01, y=0.99),
)
fig.show()

# --- Chart 2: Strategy vs NIFTY 50 (Clean Comparison) ---
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=cum_strat.index, y=cum_strat.values * 100,
    name="Dual Momentum Strategy",
    line=dict(color="#00d4aa", width=2.5),
))
fig2.add_trace(go.Scatter(
    x=cum_nifty50.index, y=cum_nifty50.values * 100,
    name="NIFTY 50 Buy & Hold",
    line=dict(color="#ff6688", width=2),
))
fig2.update_layout(
    template="plotly_dark",
    title="Strategy Equity vs NIFTY 50 Buy & Hold (Cumulative Return %)",
    xaxis_title="Date",
    yaxis_title="Cumulative Return (%)",
    yaxis=dict(ticksuffix="%"),
    height=600,
    showlegend=True,
    legend=dict(x=0.01, y=0.99),
)
fig2.update_yaxes(side="right")
fig2.show()

# --- Export ---
# Build a rebalance log
rebalance_log = pd.DataFrame({
    "date": alloc_daily.index[switch_mask],
    "buy_etf": alloc_daily[switch_mask].values,
    "portfolio_value": equity.reindex(alloc_daily.index[switch_mask]).values,
})
trades_file = script_dir / "dual_momentum_rebalance_log.csv"
rebalance_log.to_csv(trades_file, index=False)
print(f"\nRebalance log exported to {trades_file}")

orders_file = script_dir / "dual_momentum_orders.csv"
pf.orders.records_readable.to_csv(orders_file, index=False)
print(f"Orders exported to {orders_file}")
