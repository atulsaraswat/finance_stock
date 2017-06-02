# Watchlist Manager - Workflow Guide

## Creating Watchlists from Different Sources

### From Market Data Fetch

```bash
# 1. Get live data for a set of tickers
py -3 market_data.py --tickers "AAPL,MSFT,GOOG,NVDA,TSLA"

# 2. Create watchlist from that data
py -3 watchlist_manager.py --name "BigTech" --create \
  --tickers "AAPL,MSFT,GOOG,NVDA,TSLA" \
  --tags "technology,mega-cap" \
  --notes "Top 5 tech mega-caps"
```

### From Screening Results

```bash
# 1. Screen for small-cap stocks
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap small --output small_caps.json

# 2. Convert to watchlist
py -3 watchlist_manager.py --name "SmallCaps" --create \
  --from-file small_caps.json
```

### From Portfolio

```bash
# 1. Create portfolio CSV
# portfolio.csv: ticker,quantity,buy_price
# AAPL,100,150
# MSFT,50,300

# 2. Create watchlist from portfolio tickers
py -3 watchlist_manager.py --name "MyPortfolio" --create \
  --from-file portfolio.csv
```

## Managing Multiple Watchlists

### Create Several Watchlists

```bash
# Growth stocks
py -3 watchlist_manager.py --name "Growth" --create \
  --tickers "NVDA,TSLA,GOOG" --tags "growth"

# Value stocks  
py -3 watchlist_manager.py --name "Value" --create \
  --tickers "JPM,XOM,CVX" --tags "value,dividend"

# Dividend stocks
py -3 watchlist_manager.py --name "Dividend" --create \
  --tickers "JPM,CVX,PG,JNJ" --tags "dividend,income" \
  --notes "Stocks yielding >2%"
```

### List All Watchlists

```bash
py -3 watchlist_manager.py --list-all
```

Output:
```
Watchlists:
  Growth (3 tickers, created 2026-05-26)
  Value (3 tickers, created 2026-05-20)
  Dividend (4 tickers, created 2026-05-15)
```

### View Specific Watchlist

```bash
py -3 watchlist_manager.py --name Growth --show
```

### Track Changes

```bash
py -3 watchlist_manager.py --name Growth --history
```

Output:
```
2026-05-26 14:30  Added: AMZN, ANET
2026-05-26 10:00  Added: NVDA, TSLA, GOOG
2026-05-26 09:30  Created with 0 tickers
```

## Modifying Watchlists

### Add Tickers

```bash
py -3 watchlist_manager.py --name Growth --add "META,AMZN"
```

### Remove Tickers

```bash
py -3 watchlist_manager.py --name Growth --remove "GOOG"
```

### Merge Watchlists

```bash
# Combine Growth and Value into one watchlist
py -3 watchlist_manager.py --merge Growth Value \
  --output merged_watchlist.json
```

## Exporting Watchlists

### Export to CSV (for sector_score.py)

```bash
py -3 watchlist_manager.py --name Growth --export csv \
  --output growth_tickers.csv
```

Creates CSV with one ticker per line, suitable for sector analysis.

### Export to JSON (for further processing)

```bash
py -3 watchlist_manager.py --name Growth --export json \
  --output growth_watchlist.json
```

### Use with Market Analysis

```bash
# 1. Export watchlist
py -3 watchlist_manager.py --name Growth --export csv \
  --output growth.csv

# 2. Analyze sector composition
py -3 sector_score.py --input growth.csv --output growth_analysis.json

# 3. Compute sentiment
py -3 sentiment.py --input growth.csv --output growth_sentiment.json
```

## Watchlist File Format

### JSON Structure

```json
{
  "name": "Growth",
  "tickers": ["NVDA", "TSLA", "GOOG"],
  "tags": ["technology", "growth", "mega-cap"],
  "created": "2026-05-26T10:30:00Z",
  "last_updated": "2026-05-26T14:30:00Z",
  "notes": "High-growth tech stocks",
  "count": 3,
  "history": [
    {
      "timestamp": "2026-05-26T14:30:00Z",
      "action": "add",
      "tickers": ["META", "AMZN"]
    }
  ]
}
```

### CSV Export Format (for sector_score.py)

```csv
ticker
NVDA
TSLA
GOOG
META
AMZN
```

## Workflow Tips

### Workflow 1: Build Themed Watchlists

```bash
# Tech sector
py -3 watchlist_manager.py --name "Tech" --create \
  --tickers "AAPL,MSFT,GOOG,META,NVDA" --tags "technology"

# Finance sector
py -3 watchlist_manager.py --name "Finance" --create \
  --tickers "JPM,BAC,GS,MS" --tags "financials"

# List all
py -3 watchlist_manager.py --list-all
```

### Workflow 2: Screen → Watchlist → Analysis

```bash
# 1. Screen for breakouts
py -3 market_screener.py --input Finance/market_data_output.json \
  --near-52w-high 0.10 --output breakouts.json

# 2. Create watchlist
py -3 watchlist_manager.py --name "Breakouts" --create \
  --from-file breakouts.json

# 3. Analyze
py -3 sector_deep_dive.py --input breakouts.json

# 4. Monitor
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Breakouts.json
```

### Workflow 3: Portfolio Tracking

```bash
# 1. Create watchlist from portfolio
py -3 watchlist_manager.py --name "Portfolio" --create \
  --from-file portfolio.csv \
  --tags "myportfolio"

# 2. Monitor daily
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Portfolio.json \
  --report daily --output daily_summary.json

# 3. Analyze allocation
py -3 portfolio_analyzer.py --portfolio portfolio.csv
```
