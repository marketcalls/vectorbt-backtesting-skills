---
name: openalgo-ta-helpers
description: OpenAlgo TA helper functions - signal helpers (exrem, crossover, crossunder, flip) and built-in indicators (supertrend, donchian, ichimoku, sma, ema, kama, alma, etc.)
metadata:
  tags: openalgo, ta, exrem, crossover, crossunder, flip, donchian, supertrend, ichimoku, sma, ema, kama, indicators
---

# OpenAlgo TA Helper Functions (`openalgo.ta`)

The `openalgo` package provides signal helper functions AND built-in technical indicators.

```python
from openalgo import ta
```

## Signal Helpers

### exrem - Remove Excess Signals (CRITICAL)

Keeps only the first entry before an exit, and the first exit before an entry. Prevents duplicate consecutive buy/sell signals.

```python
entries = ta.exrem(buy_raw, sell_raw)
exits = ta.exrem(sell_raw, buy_raw)
```

**Before exrem:** `BUY BUY BUY SELL SELL BUY`
**After exrem:**  `BUY --- --- SELL ---- BUY`

Always use `ta.exrem()` after generating raw signals.

### crossover - Series Crosses Above

```python
cross_up = ta.crossover(close, upper_band)
```

### crossunder - Series Crosses Below

```python
cross_down = ta.crossunder(close, lower_band)
```

### flip - Regime Detection

Returns True regime from trigger1 until trigger2 fires:

```python
bull_regime = ta.flip(bull_trigger, bear_trigger)
bear_regime = ta.flip(bear_trigger, bull_trigger)
```

## Built-in Indicators

### Supertrend (Use OpenAlgo ta, NOT TA-Lib)

For Supertrend, always use `ta.supertrend()` - it is NOT available in TA-Lib:

```python
st_line, st_direction = ta.supertrend(df['high'], df['low'], df['close'], period=10, multiplier=3.0)
# direction: -1 = uptrend (bullish), 1 = downtrend (bearish)
```

### Donchian Channel (Use OpenAlgo ta)

```python
upper, middle, lower = ta.donchian(df['high'], df['low'], period=20)
# Always shift by 1 to avoid lookahead:
upper_shifted = upper.shift(1)
```

### Ichimoku Cloud (Use OpenAlgo ta)

```python
conversion, base, span_a, span_b, lagging = ta.ichimoku(
    df['high'], df['low'], df['close'],
    conversion_periods=9, base_periods=26,
    lagging_span2_periods=52, displacement=26
)
```

### Moving Averages (Available in OpenAlgo ta)

```python
df['SMA_20'] = ta.sma(df['close'], 20)
df['EMA_20'] = ta.ema(df['close'], 20)
df['WMA_20'] = ta.wma(df['close'], 20)
df['HMA_16'] = ta.hma(df['close'], 16)
df['DEMA_20'] = ta.dema(df['close'], 20)
df['TEMA_20'] = ta.tema(df['close'], 20)
df['ZLEMA_20'] = ta.zlema(df['close'], 20)
df['KAMA'] = ta.kama(df['close'], length=14, fast_length=2, slow_length=30)
df['ALMA'] = ta.alma(df['close'], period=21, offset=0.85, sigma=6.0)
df['VWMA_20'] = ta.vwma(df['close'], df['volume'], 20)
```

## When to Use OpenAlgo ta vs TA-Lib

| Indicator | Use | Reason |
|-----------|-----|--------|
| Supertrend | `ta.supertrend()` | Not available in TA-Lib |
| Donchian Channel | `ta.donchian()` | Not available in TA-Lib |
| Ichimoku Cloud | `ta.ichimoku()` | Not available in TA-Lib |
| KAMA | `ta.kama()` | OpenAlgo version has better defaults |
| ALMA | `ta.alma()` | Not available in TA-Lib |
| HMA | `ta.hma()` | Not available in TA-Lib |
| ZLEMA | `ta.zlema()` | Not available in TA-Lib |
| VWMA | `ta.vwma()` | Not available in TA-Lib |
| EMA, SMA | `tl.EMA()`, `tl.SMA()` | TA-Lib preferred for standard indicators |
| RSI | `tl.RSI()` | TA-Lib preferred |
| MACD | `tl.MACD()` | TA-Lib preferred |
| Bollinger Bands | `tl.BBANDS()` | TA-Lib preferred |
| ATR | `tl.ATR()` | TA-Lib preferred |
| ADX | `tl.ADX()` | TA-Lib preferred |
| STDDEV | `tl.STDDEV()` | TA-Lib preferred |
| MOM | `tl.MOM()` | TA-Lib preferred |

**Rule:** Use TA-Lib for indicators it supports. Use OpenAlgo ta for indicators NOT in TA-Lib (Supertrend, Donchian, Ichimoku, HMA, KAMA, ALMA, ZLEMA, VWMA).

## Common Signal Pipeline

```python
from openalgo import ta
import talib as tl

# 1. Compute indicators (TA-Lib for standard, openalgo.ta for specialty)
ema_fast = pd.Series(tl.EMA(close.values, timeperiod=10), index=close.index)
ema_slow = pd.Series(tl.EMA(close.values, timeperiod=20), index=close.index)

# 2. Generate raw signals
buy_raw = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
sell_raw = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

# 3. Fill NaN with False
buy_raw = buy_raw.fillna(False)
sell_raw = sell_raw.fillna(False)

# 4. Clean with exrem
entries = ta.exrem(buy_raw, sell_raw)
exits = ta.exrem(sell_raw, buy_raw)
```

## NEVER Do This

- Never skip `ta.exrem()` - duplicate signals corrupt position sizing
- Never forget `.fillna(False)` before `ta.exrem()` - NaN values propagate incorrectly
- Never use shifted Donchian/channel values without `.shift(1)` - that is lookahead bias
- Never use TA-Lib for Supertrend or Donchian - use OpenAlgo ta instead
