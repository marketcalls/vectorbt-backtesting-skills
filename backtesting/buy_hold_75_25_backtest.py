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
WEIGHTS = {"NIFTYBEES": 0.60, "GOLDBEES": 0.40}
EXCHANGE = "NSE"
INTERVAL = "D"
INIT_CASH = 10_00_000
FEES = 0.001  # 0.1%
FD_CAGR = 0.0645  # HDFC Bank FD rate 6.45%


def calc_cagr(start_val, end_val, years):
    """Calculate CAGR given start value, end value, and number of years."""
    if start_val <= 0 or end_val <= 0 or years <= 0:
        return 0.0
    return (end_val / start_val) ** (1 / years) - 1

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

# --- Build Price Panel ---
close_prices = pd.DataFrame({sym: dfs[sym]["close"] for sym in SYMBOLS}).dropna()
print(f"\nAligned data: {len(close_prices)} bars")

# --- Buy & Hold: One-time allocation on Day 1 ---
# Size = target weight on first bar, NaN thereafter (hold forever)
size_df = pd.DataFrame(np.nan, index=close_prices.index, columns=SYMBOLS)
size_df.iloc[0] = [WEIGHTS[sym] for sym in SYMBOLS]

pf = vbt.Portfolio.from_orders(
    close=close_prices,
    size=size_df,
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
print("  Buy & Hold Backtest")
print(f"  NIFTYBEES {WEIGHTS['NIFTYBEES']*100:.0f}% + GOLDBEES {WEIGHTS['GOLDBEES']*100:.0f}%")
print("=" * 60)
print(pf.stats())

print("\n--- Key Metrics ---")
print(f"Total Return:    {pf.total_return() * 100:.2f}%")
print(f"Sharpe Ratio:    {pf.sharpe_ratio():.2f}")
print(f"Sortino Ratio:   {pf.sortino_ratio():.2f}")
print(f"Max Drawdown:    {pf.max_drawdown() * 100:.2f}%")
print(f"Final Value:     {pf.value().iloc[-1]:,.0f}")

# --- Benchmarks ---
# NIFTY 50 Index
print("\nFetching NIFTY 50 index data for benchmark...")
df_nifty = client.history(
    symbol="NIFTY", exchange="NSE_INDEX", interval=INTERVAL,
    start_date=start_date, end_date=end_date.strftime("%Y-%m-%d"),
)
if "timestamp" in df_nifty.columns:
    df_nifty["timestamp"] = pd.to_datetime(df_nifty["timestamp"])
    df_nifty = df_nifty.set_index("timestamp")
else:
    df_nifty.index = pd.to_datetime(df_nifty.index)
df_nifty = df_nifty.sort_index()
nifty_close = df_nifty["close"].reindex(close_prices.index).ffill().bfill()

# Individual B&H benchmarks
pf_niftybees = vbt.Portfolio.from_holding(
    close_prices["NIFTYBEES"], init_cash=INIT_CASH, fees=FEES, freq="1D",
)
pf_goldbees = vbt.Portfolio.from_holding(
    close_prices["GOLDBEES"], init_cash=INIT_CASH, fees=FEES, freq="1D",
)

# --- CAGR Calculations ---
equity = pf.value()
n_days = (close_prices.index[-1] - close_prices.index[0]).days
n_years = n_days / 365.25

cagr_portfolio = calc_cagr(INIT_CASH, equity.iloc[-1], n_years)
cagr_niftybees = calc_cagr(
    close_prices["NIFTYBEES"].iloc[0], close_prices["NIFTYBEES"].iloc[-1], n_years
)
cagr_goldbees = calc_cagr(
    close_prices["GOLDBEES"].iloc[0], close_prices["GOLDBEES"].iloc[-1], n_years
)
cagr_nifty50 = calc_cagr(nifty_close.iloc[0], nifty_close.iloc[-1], n_years)

# FD compounding
fd_final = INIT_CASH * (1 + FD_CAGR) ** n_years

print(f"\n--- CAGR Benchmark Comparison ({n_years:.1f} years) ---")
bench_stats = pd.DataFrame({
    "75/25 Portfolio": [
        f"{cagr_portfolio * 100:.2f}%",
        f"{pf.total_return() * 100:.2f}%",
        f"{pf.sharpe_ratio():.2f}",
        f"{pf.sortino_ratio():.2f}",
        f"{pf.max_drawdown() * 100:.2f}%",
        f"{equity.iloc[-1]:,.0f}",
    ],
    "100% NIFTYBEES": [
        f"{cagr_niftybees * 100:.2f}%",
        f"{pf_niftybees.total_return() * 100:.2f}%",
        f"{pf_niftybees.sharpe_ratio():.2f}",
        f"{pf_niftybees.sortino_ratio():.2f}",
        f"{pf_niftybees.max_drawdown() * 100:.2f}%",
        f"{pf_niftybees.value().iloc[-1]:,.0f}",
    ],
    "100% GOLDBEES": [
        f"{cagr_goldbees * 100:.2f}%",
        f"{pf_goldbees.total_return() * 100:.2f}%",
        f"{pf_goldbees.sharpe_ratio():.2f}",
        f"{pf_goldbees.sortino_ratio():.2f}",
        f"{pf_goldbees.max_drawdown() * 100:.2f}%",
        f"{pf_goldbees.value().iloc[-1]:,.0f}",
    ],
    "NIFTY 50 Index": [
        f"{cagr_nifty50 * 100:.2f}%",
        "-",
        "-",
        "-",
        "-",
        "-",
    ],
    f"HDFC FD ({FD_CAGR*100:.2f}%)": [
        f"{FD_CAGR * 100:.2f}%",
        f"{(fd_final / INIT_CASH - 1) * 100:.2f}%",
        "-",
        "-",
        "0.00%",
        f"{fd_final:,.0f}",
    ],
}, index=["CAGR", "Total Return", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown", "Final Value"])
print(bench_stats.to_string())

# --- FD equity curve (daily compounding at annual rate) ---
fd_daily_rate = (1 + FD_CAGR) ** (1 / 365.25) - 1
fd_equity = pd.Series(
    INIT_CASH * (1 + fd_daily_rate) ** np.arange(len(close_prices)),
    index=close_prices.index,
)

# --- Cumulative returns ---
cum_strat = equity / equity.iloc[0] - 1
cum_niftybees = close_prices["NIFTYBEES"] / close_prices["NIFTYBEES"].iloc[0] - 1
cum_goldbees = close_prices["GOLDBEES"] / close_prices["GOLDBEES"].iloc[0] - 1
cum_nifty50 = nifty_close / nifty_close.iloc[0] - 1
cum_fd = fd_equity / fd_equity.iloc[0] - 1

running_max = equity.cummax()
drawdown = equity / running_max - 1

# --- Plot 1: Full Dashboard with FD ---
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    row_heights=[0.65, 0.35],
    vertical_spacing=0.07,
    subplot_titles=[
        "Cumulative Returns: All Benchmarks (incl. HDFC FD 6.45%)",
        "Drawdown",
    ],
)

fig.add_trace(go.Scatter(
    x=cum_strat.index, y=cum_strat.values,
    name="75/25 Portfolio", line=dict(color="#00d4aa", width=2.5),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_nifty50.index, y=cum_nifty50.values,
    name="NIFTY 50 Index", line=dict(color="#ff6688", width=1.5, dash="dash"),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_niftybees.index, y=cum_niftybees.values,
    name="NIFTYBEES (B&H)", line=dict(color="#4488ff", width=1, dash="dot"),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_goldbees.index, y=cum_goldbees.values,
    name="GOLDBEES (B&H)", line=dict(color="#ffaa00", width=1, dash="dot"),
), row=1, col=1)
fig.add_trace(go.Scatter(
    x=cum_fd.index, y=cum_fd.values,
    name=f"HDFC FD {FD_CAGR*100:.2f}%", line=dict(color="#888888", width=1.5, dash="dashdot"),
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=drawdown.index, y=drawdown.values,
    name="Drawdown", fill="tozeroy",
    line=dict(color="#ff4444", width=1),
), row=2, col=1)

fig.update_yaxes(tickformat=".1%", row=1, col=1)
fig.update_yaxes(tickformat=".1%", row=2, col=1)
fig.update_layout(
    template="plotly_dark",
    title="Buy & Hold: 75% NIFTYBEES + 25% GOLDBEES vs All Benchmarks (2018 - Present)",
    height=700,
    showlegend=True,
    legend=dict(x=0.01, y=0.99),
)
fig.show()

# --- Plot 2: Strategy vs NIFTY 50 vs FD (CAGR comparison) ---
fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=cum_strat.index, y=cum_strat.values * 100,
    name=f"75/25 Portfolio (CAGR: {cagr_portfolio*100:.2f}%)",
    line=dict(color="#00d4aa", width=2.5),
))
fig2.add_trace(go.Scatter(
    x=cum_nifty50.index, y=cum_nifty50.values * 100,
    name=f"NIFTY 50 B&H (CAGR: {cagr_nifty50*100:.2f}%)",
    line=dict(color="#ff6688", width=2),
))
fig2.add_trace(go.Scatter(
    x=cum_fd.index, y=cum_fd.values * 100,
    name=f"HDFC FD (CAGR: {FD_CAGR*100:.2f}%)",
    line=dict(color="#888888", width=2, dash="dashdot"),
))
fig2.update_layout(
    template="plotly_dark",
    title="75/25 Portfolio vs NIFTY 50 vs HDFC FD (Cumulative Return %)",
    xaxis_title="Date",
    yaxis_title="Cumulative Return (%)",
    yaxis=dict(ticksuffix="%"),
    height=600,
    showlegend=True,
    legend=dict(x=0.01, y=0.99),
)
fig2.show()

# --- Period-wise CAGR Comparison (1Y, 2Y, 3Y, 5Y) ---
last_date = close_prices.index[-1]
periods = {"1Y": 1, "2Y": 2, "3Y": 3, "5Y": 5}

print(f"\n--- Period-wise CAGR Comparison (as of {last_date.date()}) ---")

period_rows = []
for label, yrs in periods.items():
    lookback_date = last_date - timedelta(days=int(yrs * 365.25))
    # Find nearest available trading day
    mask = close_prices.index >= lookback_date
    if mask.sum() == 0:
        continue
    start_idx = close_prices.index[mask][0]
    y = (last_date - start_idx).days / 365.25

    # Portfolio
    eq_start = equity.loc[start_idx]
    eq_end = equity.iloc[-1]
    cagr_pf = calc_cagr(eq_start, eq_end, y)

    # NIFTYBEES
    nb_start = close_prices.loc[start_idx, "NIFTYBEES"]
    nb_end = close_prices["NIFTYBEES"].iloc[-1]
    cagr_nb = calc_cagr(nb_start, nb_end, y)

    # GOLDBEES
    gb_start = close_prices.loc[start_idx, "GOLDBEES"]
    gb_end = close_prices["GOLDBEES"].iloc[-1]
    cagr_gb = calc_cagr(gb_start, gb_end, y)

    # NIFTY 50
    n50_start = nifty_close.loc[start_idx]
    n50_end = nifty_close.iloc[-1]
    cagr_n50 = calc_cagr(n50_start, n50_end, y)

    # FD
    cagr_fd = FD_CAGR

    period_rows.append({
        "Period": label,
        "75/25 Portfolio": f"{cagr_pf * 100:.2f}%",
        "NIFTYBEES": f"{cagr_nb * 100:.2f}%",
        "GOLDBEES": f"{cagr_gb * 100:.2f}%",
        "NIFTY 50": f"{cagr_n50 * 100:.2f}%",
        f"HDFC FD": f"{cagr_fd * 100:.2f}%",
    })

period_df = pd.DataFrame(period_rows).set_index("Period")
print(period_df.to_string())

# --- Export ---
orders_file = script_dir / "buy_hold_75_25_orders.csv"
pf.orders.records_readable.to_csv(orders_file, index=False)
print(f"\nOrders exported to {orders_file}")
