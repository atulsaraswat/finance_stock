---
name: price-alert-monitor
description: "Monitor stocks and trigger alerts when price/trend thresholds are crossed. Track daily price changes, support multiple alert types (email, JSON log, webhook)."
argument-hint: "Provide watchlist and alert configuration"
user-invocable: true
---

# Price Alert Monitor

Monitor your watchlist or portfolio for price movements, technical breakdowns, and trend changes. Trigger alerts when stocks hit target prices, cross key levels, or exhibit unusual volatility.

## When to Use

- Set price targets and get notified when crossed
- Monitor for breakouts and breakdowns
- Track unusual volatility spikes
- Get daily watchlist summaries
- Trigger rebalancing alerts when allocations drift
- Monitor dividend dates and earnings announcements
- Setup background monitoring daemon

## Features

- **Price alerts**: Trigger when stock hits target price
- **Breakout detection**: Alert on 52W highs or support breaks
- **Volatility monitoring**: Alert on unusual volatility spikes
- **Trend monitoring**: Alert on trend reversals
- **Multiple notifications**: JSON log, console, webhook ready
- **Persistent state**: Track alert history and avoid duplicates
- **Flexible scheduling**: One-time checks or background daemon
- **Report generation**: Daily, weekly, monthly price change summaries

## Procedure

### 1. Simple One-Time Alert Check

```bash
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json
```

Output: Current prices + any movements > 2%.

### 2. Set Price Target Alerts

Create `alerts_config.json`:
```json
{
  "alerts": [
    {
      "ticker": "AAPL",
      "alert_type": "target_price",
      "target_price": 200,
      "condition": "above",
      "enabled": true
    },
    {
      "ticker": "MSFT",
      "alert_type": "target_price",
      "target_price": 400,
      "condition": "below",
      "enabled": true
    },
    {
      "ticker": "TSLA",
      "alert_type": "breakout",
      "threshold": 0.02,
      "enabled": true
    }
  ]
}
```

Then run:
```bash
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json \
  --config alerts_config.json
```

### 3. Monitor Volatility Spike

```bash
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json \
  --monitor volatility --threshold 0.05
```

Alerts if any stock moves >5% from previous close.

### 4. Generate Daily Summary Report

```bash
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json \
  --report daily --output Finance/daily_summary.json
```

Output:
```json
{
  "date": "2026-05-26",
  "summary": {
    "gainers": [
      {"ticker": "NVDA", "price": 875.50, "change": 3.2, "change_pct": 0.37},
      {"ticker": "GOOG", "price": 145.20, "change": 1.80, "change_pct": 1.25}
    ],
    "losers": [
      {"ticker": "AAPL", "price": 185.30, "change": -4.15, "change_pct": -2.19},
      {"ticker": "MSFT", "price": 410.50, "change": -7.40, "change_pct": -1.77}
    ],
    "largest_move": {"ticker": "NVDA", "move": 3.2},
    "total_gainers": 4,
    "total_losers": 2
  },
  "alerts_triggered": [
    {
      "ticker": "AAPL",
      "alert_type": "target_price",
      "message": "Price crossed below $190 target (currently $185.30)",
      "timestamp": "2026-05-26T16:30:00Z"
    }
  ]
}
```

### 5. Monitor Portfolio Concentrations

```bash
py -3 price_alert_monitor.py --portfolio portfolio.csv \
  --monitor concentration \
  --max-position-weight 0.30
```

Alerts if any position grows to >30% of portfolio.

### 6. Breakout Detection

```bash
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json \
  --detect-breakouts --range 52w
```

Alerts when stocks break above/below 52W high/low.

### 7. Background Monitoring Service

```bash
# Start monitoring daemon (runs until stopped)
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json \
  --config alerts_config.json \
  --daemon \
  --check-interval 300 \
  --log-file Finance/alerts.log
```

Checks every 5 minutes, logs to file.

### 8. Export Alert History

```bash
py -3 price_alert_monitor.py --show-history \
  --output Finance/alert_history.csv \
  --days 30
```

Shows all alerts from past 30 days.

## Output Examples

**Real-Time Alert (Console):**
```
🔔 PRICE ALERT
  Ticker: AAPL
  Alert:  Price crossed below $190 target
  Current: $185.30 (-2.19%)
  Time:   2026-05-26 16:30:00 UTC
  Status: TRIGGERED
```

**Alert Log (JSON):**
```json
{
  "alerts": [
    {
      "id": "alert_20260526_001",
      "timestamp": "2026-05-26T16:30:00Z",
      "ticker": "AAPL",
      "alert_type": "target_price",
      "condition": "below",
      "target": 190,
      "current_price": 185.30,
      "previous_price": 189.45,
      "change_pct": -2.19,
      "message": "Price $185.30 crossed below target $190",
      "acknowledged": false
    },
    {
      "id": "alert_20260526_002",
      "timestamp": "2026-05-26T14:15:00Z",
      "ticker": "NVDA",
      "alert_type": "breakout",
      "condition": "above_52w_high",
      "current_price": 875.50,
      "52w_high": 872.00,
      "change_pct": 0.40,
      "message": "Price $875.50 broke above 52W high $872.00",
      "acknowledged": false
    }
  ]
}
```

## Alert Types

| Type | Description | Config Example |
|------|-------------|-----------------|
| target_price | Alert when stock hits a price | `{"ticker": "AAPL", "target_price": 200, "condition": "above"}` |
| breakout | Alert on 52W high/low breaks | `{"ticker": "GOOG", "threshold": 0.02}` |
| volatility | Alert on unusual movement | `{"ticker": "TSLA", "volatility_threshold": 0.05}` |
| trend_reversal | Alert on trend changes | `{"ticker": "MSFT", "monitor": "rsi_overbought"}` |
| concentration | Alert on position size drift | `{"ticker": "AAPL", "max_weight": 0.30}` |
| dividend | Alert on dividend dates | `{"ticker": "JPM", "monitor": "dividend_dates"}` |

## Command-Line Options

| Flag | Type | Description |
|------|------|-------------|
| `--watchlist` | path | Watchlist JSON or CSV |
| `--portfolio` | path | Portfolio CSV |
| `--config` | path | Alert configuration JSON |
| `--monitor` | str | Type: volatility, concentration, trends, breakouts |
| `--report` | str | Report type: daily, weekly, monthly, alerts |
| `--threshold` | float | Movement threshold (e.g., 0.05 = 5%) |
| `--detect-breakouts` | flag | Enable breakout detection |
| `--range` | str | Range for breakouts: 1m, 3m, 6m, 1y, 52w |
| `--daemon` | flag | Run as background service |
| `--check-interval` | int | Seconds between checks (daemon mode) |
| `--log-file` | path | Log file location |
| `--show-history` | flag | Display alert history |
| `--days` | int | History lookback days |
| `--output` | path | Save results to file |
| `--format` | str | Output format: json, csv, table |

## Integration with Other Skills

**Monitor screened results:**
```bash
# 1. Screen for breakout candidates
py -3 market_screener.py --input Finance/market_data_output.json \
  --near-52w-high 0.05 --output breakout_candidates.json

# 2. Setup watchlist
py -3 watchlist_manager.py --name "Breakouts" \
  --create --from-file breakout_candidates.json

# 3. Monitor for breakouts
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Breakouts.json \
  --detect-breakouts --range 1y
```

**Portfolio monitoring:**
```bash
# Monitor your positions for drift
py -3 price_alert_monitor.py --portfolio portfolio.csv \
  --monitor concentration --max-position-weight 0.30

# Get daily summary
py -3 price_alert_monitor.py --portfolio portfolio.csv \
  --report daily --output daily_moves.json
```

**Combine with alerts + sentiment:**
```bash
# 1. Get price movements
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Growth.json \
  --report daily > daily_moves.json

# 2. Then analyze sentiment of movers
py -3 sentiment.py --input prices.csv
```

## Reference

See [price_alert_monitor.py](./scripts/price_alert_monitor.py) for implementation details.
