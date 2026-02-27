# VectorBT Backtesting Skills for Agentic Coding Tools

A comprehensive collection of backtesting skills for trading strategies using VectorBT. Works with **40+ AI coding agents** via [skills.sh](https://github.com/vercel-labs/skills) — including Claude Code, Cursor, Codex, OpenCode, Cline, Windsurf, GitHub Copilot, Gemini CLI, Roo Code, and more.

Supports **Indian markets** (OpenAlgo + Zerodha fees), **US markets** (yfinance + IBKR fees), and **Crypto markets** (yfinance/CCXT + Binance fees). Includes TA-Lib indicators, market-specific benchmarking, QuantStats tearsheets, and robustness testing.

## Quick Install

Install the skills into your project using [npx skills](https://github.com/vercel-labs/skills). The CLI auto-detects your AI coding agent and installs skills to the correct directory.

```bash
# GitHub shorthand
npx skills add marketcalls/vectorbt-backtesting-skills

# Full GitHub URL
npx skills add https://github.com/marketcalls/vectorbt-backtesting-skills
```

Install a specific skill only:

```bash
npx skills add marketcalls/vectorbt-backtesting-skills -s backtest
npx skills add marketcalls/vectorbt-backtesting-skills -s optimize
npx skills add marketcalls/vectorbt-backtesting-skills -s vectorbt-expert
npx skills add marketcalls/vectorbt-backtesting-skills -s setup
```

List available skills before installing:

```bash
npx skills add marketcalls/vectorbt-backtesting-skills -l
```

Install globally (available across all projects):

```bash
npx skills add marketcalls/vectorbt-backtesting-skills -g
```

### Supported AI Coding Agents

Skills are installed via [skills.sh](https://github.com/vercel-labs/skills) which supports 40+ agents. Each agent reads skills from its own directory:

| Agent | Skills Directory |
|-------|-----------------|
| Claude Code | `.claude/skills/` |
| Cursor | `.agents/skills/` |
| Codex | `.agents/skills/` |
| OpenCode | `.agents/skills/` |
| Cline | `.agents/skills/` |
| Windsurf | `.agents/skills/` |
| GitHub Copilot | `.agents/skills/` |
| Gemini CLI | `.agents/skills/` |
| Roo Code | `.agents/skills/` |
| + 30 more | Auto-detected by `npx skills` |

The `npx skills add` command detects which agents you have installed and places the skill files in the correct paths automatically.

## Supported Markets

| Market | Data Source | Fee Model | Default Benchmark |
|--------|------------|-----------|-------------------|
| **India** | OpenAlgo (NSE, BSE, NFO, MCX) | Zerodha (4-segment) | NIFTY 50 |
| **US** | yfinance (NYSE, NASDAQ) | IBKR Pro/Lite | S&P 500 |
| **Crypto** | yfinance / CCXT (Binance) | Binance (spot + futures) | Bitcoin |
| **Custom** | Any provider via extensible pattern | User-defined | User-defined |

## Capabilities

### Skills (User-Invocable Commands)

| Command | What It Does |
|---------|-------------|
| `/setup` | Detects OS, creates venv, installs TA-Lib + all packages, creates `backtesting/` folders, configures `.env` with API keys |
| `/backtest` | Generates a complete backtest script with signals, market-specific fees, benchmark comparison, plain-language report, QuantStats tearsheet |
| `/optimize` | Parameter grid search with TA-Lib indicators, tqdm progress bars, Plotly heatmaps, best params vs benchmark |
| `/quick-stats` | Inline code block (no file) — fetch data, run EMA crossover, print compact stats + benchmark alpha |
| `/strategy-compare` | Side-by-side comparison of multiple strategies on same symbol, overlaid equity curves |

### Pre-Built Strategy Templates (12)

| Strategy | Type | Description |
|----------|------|-------------|
| EMA Crossover | Trend | EMA 10/20 crossover |
| RSI | Mean-reversion | RSI(14) oversold/overbought |
| Donchian Channel | Breakout | Channel breakout with shifted levels (no lookahead) |
| Supertrend | Trend | Supertrend with intraday session windows (9:30-15:00, exit 15:15) |
| MACD | Trend + Breakout | MACD zero-line regime + signal-candle breakout |
| SDA2 | Trend | WMA + STDDEV + ATR band system |
| Double Momentum | Momentum | MOM + MOM-of-MOM with next-bar fill |
| Dual Momentum | Rotation | Quarterly ETF rotation (NIFTYBEES vs GOLDBEES) |
| Buy & Hold | Passive | Static multi-asset allocation with FD benchmark |
| RSI Accumulation | Accumulation | Weekly RSI slab-wise buying (5%/10%/20% by RSI level) |
| Walk-Forward | Validation | Rolling train/test optimization with WFE scoring |
| Realistic Costs | Analysis | Same strategy across 5 fee models (zero to Zerodha delivery) |

### Knowledge Base (20 Rule Files)

| Category | What's Covered |
|----------|---------------|
| **Data** | OpenAlgo (India), yfinance (US/Global), CCXT (Crypto), custom providers, `.env` + `python-dotenv`, CSV loading, resampling |
| **Indicators** | TA-Lib mandatory (EMA, SMA, RSI, MACD, BBands, ATR, ADX, STDDEV, MOM). OpenAlgo ta for Supertrend, Donchian, Ichimoku, HMA, KAMA, ALMA, ZLEMA, VWMA |
| **Signals** | `ta.exrem()` signal cleaning, `ta.crossover()`, `ta.crossunder()`, `ta.flip()` regime detection |
| **Simulation** | `from_signals`, `from_orders`, `from_holding`, long/short/both directions |
| **Sizing** | Percent, Value, TargetPercent, whole shares (`min_size=1`), futures lot sizes, fractional crypto |
| **Costs** | **India**: Zerodha 4-segment (Delivery 0.111%, Intraday 0.0225%, Futures 0.018%, Options 0.098% + Rs 20). **US**: IBKR Pro/Lite (Stocks $0.005/share, Options $0.65/contract, Futures $0.85/contract). **Crypto**: Binance (Spot 0.1%, USDT-M Futures 0.02%/0.05% maker/taker, funding rates) |
| **Futures** | SEBI revised lot sizes (Dec 2025): NIFTY=65, BANKNIFTY=30, FINNIFTY=60. US: E-mini/Micro contract specs |
| **Risk** | Stop loss, take profit, trailing stop (`sl_trail`) |
| **Optimization** | Loop-based (TA-Lib compliant) + broadcasting (vbt.MA exception for parameter sweeps) |
| **Benchmarking** | India: NIFTY 50 via OpenAlgo. US: S&P 500 (`^GSPC`). Crypto: Bitcoin (`BTC-USD`). Strategy vs Benchmark table always produced |
| **Reporting** | Plain-language backtest explanation for normal traders. QuantStats HTML tearsheets with 30+ metrics, Monte Carlo simulations |
| **Plotting** | Plotly dark theme, candlestick with `xaxis type="category"` (no weekend gaps), VectorBT 7-panel plot pack |
| **Validation** | Walk-forward analysis (WFE ratio), robustness testing (Monte Carlo trade shuffle, noise injection, parameter sensitivity, entry/exit delay, cross-symbol validation) |
| **Safety** | 10 common pitfalls with prevention, checklist before going live |

## Prerequisites

### 1. AI Coding Agent

Install any supported AI coding agent. For example:

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) — `npm install -g @anthropic-ai/claude-code`
- [Cursor](https://cursor.com) — Desktop IDE with built-in AI
- [Codex](https://github.com/openai/codex) — `npm install -g @openai/codex`
- [OpenCode](https://github.com/opencode-ai/opencode) — `go install github.com/opencode-ai/opencode@latest`
- [Cline](https://github.com/cline/cline) — VS Code extension
- [Windsurf](https://windsurf.com) — Desktop IDE with AI
- Or any of the [40+ supported agents](https://github.com/vercel-labs/skills)

Then install the skills:

```bash
npx skills add marketcalls/vectorbt-backtesting-skills
```

### 2. Data Source Setup

**Indian Markets** — requires [OpenAlgo](https://github.com/marketcalls/openalgo):

```bash
git clone https://github.com/marketcalls/openalgo.git
cd openalgo
pip install -r requirements.txt
python app.py
```

OpenAlgo runs locally at `http://127.0.0.1:5000`. You need a broker account connected via OpenAlgo and an API key from the dashboard. See [OpenAlgo documentation](https://docs.openalgo.in/).

**US Markets** — no setup needed. Uses yfinance (public Yahoo Finance data).

**Crypto Markets** — no setup needed for public data (yfinance or CCXT). Binance API keys are optional (only for private endpoints).

### 3. Python Environment Setup

Use the `/setup` skill for automated setup, or manually:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Install TA-Lib C library first
brew install ta-lib         # macOS
# sudo apt install libta-lib-dev  # Linux

# Install Python packages
pip install openalgo vectorbt plotly anywidget nbformat ta-lib pandas numpy yfinance python-dotenv tqdm scipy numba ipywidgets quantstats ccxt
```

### 4. Configure API Keys

```bash
cp .env.sample .env
# Edit .env with your API keys
```

## Usage Examples

### `/setup` - Environment Setup

Detects OS, creates venv, installs dependencies, creates folder structure, and collects API keys into `.env`.

```
/setup
/setup python3.12
```

### `/backtest` - Quick Backtest

Create a complete backtest script with market-specific fees, benchmark comparison, plain-language report, and QuantStats tearsheet.

```
# Indian Markets
/backtest ema-crossover SBIN NSE D
/backtest rsi RELIANCE NSE D
/backtest supertrend NIFTY NFO 5m

# US Markets
/backtest ema-crossover AAPL
/backtest rsi MSFT

# Crypto Markets
/backtest ema-crossover BTC-USD
```

### `/optimize` - Parameter Optimization

Optimize strategy parameters, generate Plotly heatmaps, and compare best parameters vs benchmark.

```
/optimize ema-crossover SBIN NSE D
/optimize rsi AAPL
```

### `/quick-stats` - Inline Stats

Print key backtest stats with benchmark comparison without creating a file.

```
/quick-stats RELIANCE
/quick-stats AAPL
/quick-stats BTC-USD
```

### `/strategy-compare` - Compare Strategies

Compare multiple strategies side-by-side with benchmark.

```
/strategy-compare RELIANCE ema-crossover rsi donchian
/strategy-compare AAPL ema-crossover rsi macd
```

## Key Features

### Multi-Market Transaction Costs

Realistic fee models for each market, auto-selected based on the asset:

#### Indian Markets (Zerodha)

| Segment | `fees` | `fixed_fees` |
|---------|--------|-------------|
| Delivery Equity | 0.00111 (0.111%) | Rs 20/order |
| Intraday Equity | 0.000225 (0.0225%) | Rs 20/order |
| F&O Futures | 0.00018 (0.018%) | Rs 20/order |
| F&O Options | 0.00098 (0.098%) | Rs 20/order |

#### US Markets (Interactive Brokers)

| Segment | `fees` | `fixed_fees` |
|---------|--------|-------------|
| Stocks (IBKR Pro Fixed) | 0.0001 (0.01%) | $1.00/order |
| Stocks (IBKR Lite) | 0.00001 (~0.001%) | $0 |
| Options | 0.002 (0.2%) | $0.65/contract |
| E-mini Futures (ES, NQ) | 0.000009 (~0.001%) | $2.25/contract |
| Micro Futures (MES, MNQ) | 0.00002 (~0.002%) | $0.55/contract |

#### Crypto Markets (Binance)

| Segment | `fees` | `fixed_fees` |
|---------|--------|-------------|
| Spot (Base) | 0.001 (0.1%) | $0 |
| Spot (BNB Discount) | 0.00075 (0.075%) | $0 |
| USDT-M Futures (Taker) | 0.0005 (0.05%) | $0 |
| USDT-M Futures (Maker) | 0.0002 (0.02%) | $0 |
| COIN-M Futures (Taker) | 0.0005 (0.05%) | $0 |

### TA-Lib Indicators (Mandatory)

All strategies use TA-Lib for technical indicators. VectorBT built-in indicators are never used.

```python
import talib as tl
ema_fast = pd.Series(tl.EMA(close.values, timeperiod=10), index=close.index)
```

### OpenAlgo TA for Specialty Indicators

Supertrend, Donchian, Ichimoku, HMA, KAMA, ALMA, ZLEMA, VWMA — plus signal utilities (exrem, crossover, crossunder, flip).

```python
from openalgo import ta
st_line, st_direction = ta.supertrend(high, low, close, period=10, multiplier=3.0)
entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
```

### Market-Specific Benchmarks

| Market | Default Benchmark | Source |
|--------|-------------------|--------|
| India | NIFTY 50 | OpenAlgo (`NSE_INDEX`) |
| US | S&P 500 | yfinance (`^GSPC` or `SPY`) |
| Crypto | Bitcoin | yfinance (`BTC-USD`) |

Every backtest produces a Strategy vs Benchmark comparison table.

### QuantStats Tearsheets

Professional HTML reports with 30+ metrics, drawdown analysis, rolling statistics, monthly heatmaps, and Monte Carlo simulations.

```python
import quantstats as qs
qs.reports.html(pf.returns(), benchmark="^NSEI", output="tearsheet.html")
```

### Plain-Language Report Explanation

Every backtest explains results so normal traders can understand:

```
* Total Return: Your strategy made 45.23% while NIFTY 50 made 32.10%
  -> BEAT the market by 13.13%
* Max Drawdown: -12.34% - the biggest drop from peak
  -> On Rs 10,00,000 capital, worst temporary loss = Rs 1,23,400
* Sharpe Ratio: 1.45 (return per unit of risk, >1 decent, >2 excellent)
```

### Extensible Data Providers

Built-in support for OpenAlgo, yfinance, and CCXT. Add custom providers (Alpaca, Twelve Data, etc.) following the pattern in `data-fetching.md`. All API keys stored in `.env` via `python-dotenv`.

### SEBI Revised Lot Sizes (Effective 31 Dec 2025)

| Index | Lot Size | Exchange |
|-------|----------|----------|
| Nifty 50 | 65 | NFO |
| Nifty Bank | 30 | NFO |
| Nifty Financial Services | 60 | NFO |
| Nifty Midcap Select | 120 | NFO |
| Nifty Next 50 | 25 | NFO |
| BSE Sensex | 20 | BFO |
| BSE Bankex | 30 | BFO |
| BSE Sensex 50 | 70 | BFO |

### Backtesting Folder Structure

Strategy name = folder name. Symbol name = file prefix. Each strategy folder is self-contained.

```
backtesting/
├── ema_crossover/
│   ├── .env
│   ├── SBIN_ema_crossover_backtest.py
│   ├── SBIN_ema_crossover_trades.csv
│   ├── SBIN_tearsheet.html
│   ├── AAPL_ema_crossover_backtest.py
│   └── AAPL_ema_crossover_trades.csv
├── rsi/
│   ├── .env
│   ├── INFY_rsi_backtest.py
│   └── ...
├── supertrend/
│   └── ...
└── custom/
    └── ...
```

## Project Structure

```
.
├── .claude/
│   └── skills/
│       ├── setup/                    # /setup - Environment setup
│       │   └── SKILL.md
│       ├── backtest/                 # /backtest - Quick backtest
│       │   └── SKILL.md
│       ├── optimize/                 # /optimize - Parameter optimization
│       │   └── SKILL.md
│       ├── quick-stats/              # /quick-stats - Inline stats
│       │   └── SKILL.md
│       ├── strategy-compare/         # /strategy-compare - Compare strategies
│       │   └── SKILL.md
│       └── vectorbt-expert/          # Knowledge base (auto-loaded)
│           ├── SKILL.md              # Main skill (modular reference hub)
│           └── rules/                # 20 modular rule files
│               ├── data-fetching.md
│               ├── simulation-modes.md
│               ├── position-sizing.md
│               ├── indicators-signals.md
│               ├── openalgo-ta-helpers.md
│               ├── stop-loss-take-profit.md
│               ├── parameter-optimization.md
│               ├── performance-analysis.md
│               ├── plotting.md
│               ├── indian-market-costs.md
│               ├── us-market-costs.md
│               ├── crypto-market-costs.md
│               ├── futures-backtesting.md
│               ├── long-short-trading.md
│               ├── csv-data-resampling.md
│               ├── walk-forward.md
│               ├── robustness-testing.md
│               ├── pitfalls.md
│               ├── strategy-catalog.md
│               ├── quantstats-tearsheet.md
│               └── assets/           # Production-ready templates
│                   ├── ema_crossover/backtest.py
│                   ├── rsi/backtest.py
│                   ├── donchian/backtest.py
│                   ├── supertrend/backtest.py
│                   ├── macd/backtest.py
│                   ├── sda2/backtest.py
│                   ├── momentum/backtest.py
│                   ├── dual_momentum/backtest.py
│                   ├── buy_hold/backtest.py
│                   ├── rsi_accumulation/backtest.py
│                   ├── walk_forward/template.py
│                   └── realistic_costs/template.py
├── .env.sample                      # Environment template (copy to .env)
├── backtesting/                      # Generated backtest scripts (per strategy)
│   ├── ema_crossover/
│   ├── rsi/
│   ├── donchian/
│   ├── supertrend/
│   ├── macd/
│   ├── sda2/
│   ├── momentum/
│   ├── dual_momentum/
│   ├── buy_hold/
│   ├── rsi_accumulation/
│   ├── walk_forward/
│   └── custom/
└── README.md
```

## Rule Files Reference

| Rule File | Description |
|-----------|-------------|
| `data-fetching.md` | OpenAlgo (India), yfinance (US), CCXT (Crypto), custom providers, `.env` setup |
| `simulation-modes.md` | from_signals, from_orders, from_holding, direction types |
| `position-sizing.md` | Amount/Value/Percent/TargetPercent sizing, whole shares |
| `indicators-signals.md` | TA-Lib mandatory indicator reference, signal generation |
| `openalgo-ta-helpers.md` | OpenAlgo ta: exrem, crossover, Supertrend, Donchian, Ichimoku, MAs |
| `stop-loss-take-profit.md` | Fixed SL, TP, trailing stop configurations |
| `parameter-optimization.md` | Broadcasting and loop-based optimization, heatmaps |
| `performance-analysis.md` | Stats, metrics, benchmark comparison, CAGR calculation |
| `plotting.md` | Candlestick (category x-axis), VectorBT plots, custom Plotly |
| `indian-market-costs.md` | Zerodha fee model by segment with detailed breakdown |
| `us-market-costs.md` | IBKR fee model — US stocks, options, futures (Fixed/Tiered, SEC, FINRA TAF) |
| `crypto-market-costs.md` | Binance fee model — spot, USDT-M/COIN-M futures, funding rates, VIP tiers |
| `futures-backtesting.md` | SEBI revised lot sizes (Dec 2025), US contract specs, value sizing |
| `long-short-trading.md` | Simultaneous long/short, direction comparison |
| `csv-data-resampling.md` | Loading CSV data, resampling with Indian market alignment |
| `walk-forward.md` | Walk-forward analysis, WFE ratio, rolling optimization |
| `robustness-testing.md` | Monte Carlo, noise test, parameter sensitivity, delay test |
| `pitfalls.md` | 10 common mistakes and checklist before going live |
| `strategy-catalog.md` | All strategy types with code snippets and asset references |
| `quantstats-tearsheet.md` | QuantStats HTML reports, 30+ metrics, Monte Carlo |

## Data Sources

| Source | Use Case | Tickers/Codes | API Key Required |
|--------|----------|---------------|------------------|
| OpenAlgo | Indian markets (primary) | NSE, BSE, NFO, BFO, CDS, MCX, NSE_INDEX, BSE_INDEX | Yes (`OPENALGO_API_KEY`) |
| yfinance | US markets, global, crypto | `AAPL`, `SPY`, `^GSPC`, `^NSEI`, `BTC-USD`, `ETH-USD` | No |
| CCXT | Crypto exchanges (Binance, etc.) | `BTC/USDT`, `ETH/USDT` (higher resolution data) | Optional |
| Custom | Any provider | User-defined | User-defined |

## Configuration

Copy the `.env.sample` and fill in your API keys:

```bash
cp .env.sample .env
```

The `.env` file supports:

```
# Indian Markets (OpenAlgo)
OPENALGO_API_KEY=your_openalgo_api_key_here
OPENALGO_HOST=http://127.0.0.1:5000

# Crypto Markets (Binance via CCXT) - Optional
BINANCE_API_KEY=
BINANCE_SECRET_KEY=

# Custom Data Providers - add your own keys
# ALPACA_API_KEY=
# TWELVEDATA_API_KEY=
```

US market data via yfinance does not require an API key.

## License

MIT
