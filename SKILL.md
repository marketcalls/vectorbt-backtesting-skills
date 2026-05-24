---
name: vectorbt-backtesting-skills
description: 外部 VectorBT 专业回测引擎 — 参数网格搜索 / Walk-Forward 验证 / Monte Carlo 鲁棒性测试 / 12套策略模板
source: https://github.com/marketcalls/vectorbt-backtesting-skills
install_status: PENDING (GitHub 网络不可用, 2026-05-24)
---

# VectorBT Backtesting Skills

> ⚠️ **安装状态**: 存根文件。因 GitHub 连接被阻断，实际代码未克隆。
> **安装**: `git clone https://github.com/marketcalls/vectorbt-backtesting-skills.git ~/.claude/skills/vectorbt-backtesting-skills`

## 可用命令 (克隆后)

| 命令 | 功能 |
|------|------|
| `/setup` | 自动检测 OS, 创建 venv, 安装 TA-Lib + 所有包 |
| `/backtest` | 生成完整的 VectorBT 回测脚本 (含信号、费用、基准、QuantStats 报告) |
| `/optimize` | 参数网格搜索 + Plotly 热力图 |
| `/quick-stats` | 内联统计 + 基准 Alpha |
| `/strategy-compare` | 多策略并排对比 |

## 内置 12 套策略模板

| 模板 | 说明 |
|------|------|
| SMA Crossover | 简单移动平均线交叉 |
| RSI Mean Reversion | RSI 均值回归 |
| MACD Trend Following | MACD 趋势跟踪 |
| Bollinger Breakout | 布林带突破 |
| **Walk-Forward Validation** | 滚动训练/测试优化 + WFE 评分 |
| Machine Learning | 机器学习策略 |
| Multi-Timeframe | 多时间框架汇流 |
| Portfolio Optimization | 投资组合优化 |
| Options Strategies | 期权策略 |
| Crypto Strategies | 加密货币策略 (含 CCXT 费用模型) |
| Custom Strategy | 自定义策略模板 |
| Statistical Arbitrage | 统计套利 |

## 鲁棒性测试包含

- Monte Carlo 交易顺序打乱
- 噪声注入 (滑点/延迟/缺失数据)
- 参数灵敏度分析
- 入场/出场延迟模拟
- 跨品种验证

## 市场支持

- 印度市场 (OpenAlgo) — SEBI 费用模型
- 美国市场 (yfinance) — 每股/每合约费用
- 加密货币 (CCXT) — Maker/Taker 费用模型

## Aegis V7.0 集成方式

```python
# 在 aegis_backtest_v4.py 中使用 vectorbt
import vectorbt as vbt

# 生成信号 (从 Blackboard 读取融合信号)
signals = ...  # 从 OODA 循环提取

# VectorBT 回测
portfolio = vbt.Portfolio.from_signals(
    price=price_data,
    entries=entries,
    exits=exits,
    slippage=0.001,
    freq='1h',
)

# 输出 QuantStats 报告
stats = portfolio.stats()
```

## 依赖

- Python 3.9+
- vectorbt
- quantstats
- plotly
- TA-Lib (自动安装)
