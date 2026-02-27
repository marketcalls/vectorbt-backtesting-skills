---
name: indicators-signals
description: Creating technical indicators and entry/exit signals using TA-Lib exclusively
metadata:
  tags: indicators, signals, rsi, ema, sma, macd, crossover, entries, exits, talib
---

# Creating Indicators & Signals

## CRITICAL RULE: Always Use TA-Lib

**ALWAYS use TA-Lib (`talib`) for ALL technical indicators**, including simple ones like EMA and SMA. NEVER use VectorBT's built-in `vbt.MA.run()`, `vbt.RSI.run()`, or similar. TA-Lib is the industry standard and ensures consistent, verified calculations.

```python
import talib as tl
import pandas as pd
from openalgo import ta
```

## EMA Crossover Strategy

```python
import talib as tl
from openalgo import ta

fast_period, slow_period = 10, 20
ema_fast = pd.Series(tl.EMA(close.values, timeperiod=fast_period), index=close.index)
ema_slow = pd.Series(tl.EMA(close.values, timeperiod=slow_period), index=close.index)

buy_raw = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
sell_raw = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

# ALWAYS clean signals with ta.exrem()
entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))
```

## SMA Crossover Strategy

```python
import talib as tl
from openalgo import ta

fast_sma = pd.Series(tl.SMA(close.values, timeperiod=10), index=close.index)
slow_sma = pd.Series(tl.SMA(close.values, timeperiod=20), index=close.index)

buy_raw = (fast_sma > slow_sma) & (fast_sma.shift(1) <= slow_sma.shift(1))
sell_raw = (fast_sma < slow_sma) & (fast_sma.shift(1) >= slow_sma.shift(1))

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))
```

## RSI Strategy

```python
import talib as tl
from openalgo import ta

rsi = pd.Series(tl.RSI(close.values, timeperiod=14), index=close.index)

buy_raw = (rsi < 30) & (rsi.shift(1) >= 30)      # RSI crosses below 30 (oversold)
sell_raw = (rsi > 70) & (rsi.shift(1) <= 70)      # RSI crosses above 70 (overbought)

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))
```

## MACD Strategy

```python
import talib as tl
from openalgo import ta

macd, macd_signal, macd_hist = tl.MACD(close.values, fastperiod=12, slowperiod=26, signalperiod=9)
macd_series = pd.Series(macd, index=close.index)
signal_series = pd.Series(macd_signal, index=close.index)

buy_raw = (macd_series > signal_series) & (macd_series.shift(1) <= signal_series.shift(1))
sell_raw = (macd_series < signal_series) & (macd_series.shift(1) >= signal_series.shift(1))

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))
```

## Bollinger Bands Strategy

```python
import talib as tl
from openalgo import ta

upper, middle, lower = tl.BBANDS(close.values, timeperiod=20, nbdevup=2, nbdevdn=2)
upper = pd.Series(upper, index=close.index)
lower = pd.Series(lower, index=close.index)

buy_raw = (close < lower) & (close.shift(1) >= lower.shift(1))   # Price touches lower band
sell_raw = (close > upper) & (close.shift(1) <= upper.shift(1))   # Price touches upper band

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))
```

## ATR (Average True Range)

```python
import talib as tl

atr = pd.Series(tl.ATR(high.values, low.values, close.values, timeperiod=14), index=close.index)
```

## Complete TA-Lib Indicator Reference

| Indicator | TA-Lib Function | Usage |
|-----------|----------------|-------|
| EMA | `tl.EMA(close.values, timeperiod=N)` | Trend following |
| SMA | `tl.SMA(close.values, timeperiod=N)` | Trend following |
| WMA | `tl.WMA(close.values, timeperiod=N)` | Weighted trend |
| RSI | `tl.RSI(close.values, timeperiod=14)` | Overbought/oversold |
| MACD | `tl.MACD(close.values, 12, 26, 9)` | Trend + momentum |
| Bollinger | `tl.BBANDS(close.values, 20, 2, 2)` | Volatility bands |
| ATR | `tl.ATR(high.values, low.values, close.values, 14)` | Volatility measure |
| ADX | `tl.ADX(high.values, low.values, close.values, 14)` | Trend strength |
| STDDEV | `tl.STDDEV(close.values, timeperiod=N)` | Standard deviation |
| MOM | `tl.MOM(close.values, timeperiod=N)` | Momentum |
| STOCH | `tl.STOCH(high.values, low.values, close.values)` | Stochastic |
| CCI | `tl.CCI(high.values, low.values, close.values, 14)` | Commodity channel |

Always wrap TA-Lib output in `pd.Series(..., index=close.index)` to preserve the datetime index.

## Signal Cleaning: Why ta.exrem() Matters

Raw crossover signals can produce consecutive buy signals without an intervening sell. `ta.exrem()` keeps only the FIRST entry before an exit and vice versa:

```
Raw:    BUY  BUY  BUY  SELL  SELL  BUY
Clean:  BUY  ---  ---  SELL  ----  BUY
```

Always apply `ta.exrem()` after generating raw signals. See [openalgo-ta-helpers](./openalgo-ta-helpers.md) for full helper reference.

## NEVER Do This

- **NEVER use `vbt.MA.run()`, `vbt.RSI.run()`**, or any VectorBT built-in indicator. Always use TA-Lib
- Never generate signals using future data (lookahead bias)
- Never skip `ta.exrem()` signal cleaning - duplicate signals cause incorrect position sizing
- Never use `close[i]` in Python loops when vectorized operations exist
- Never forget `.fillna(False)` on boolean signal series - NaN signals cause silent errors
- Never forget to wrap TA-Lib output in `pd.Series(..., index=close.index)`
