---
name: watchlist-manager
description: "Create, update, and manage stock watchlists. Organize by theme, track changes, merge lists, and export for analysis or sharing."
argument-hint: "Specify action (create/add/merge/export) and watchlist name"
user-invocable: true
---

# Watchlist Manager

Create and manage multiple stock watchlists organized by theme, sector, strategy, or time horizon. Track changes, merge lists, and export for sentiment or sector analysis.

## When to Use

- Organize screening results into themed watchlists
- Build watchlists for sector-specific analysis
- Maintain separate lists for growth, value, income strategies
- Track watchlist changes over time
- Prepare data for sentiment.py or sector_score.py
- Share watchlists or archive historical versions

## Features

- **Multiple watchlists**: Create and manage independent lists by theme
- **Watchlist metadata**: Tags, categories, creation date, last updated
- **Add/remove operations**: Incrementally build or modify lists
- **Merge & combine**: Merge multiple lists or deduplicate
- **Version history**: Track changes with timestamps
- **Export for analysis**: Export as CSV (for sector_score.py) or JSON
- **Summary stats**: Quick overview of what's in each list

## Procedure

### 1. Create a New Watchlist

```bash
py -3 watchlist_manager.py --name Growth --create \
  --tickers "AAPL,MSFT,NVDA,GOOG"
```

Creates: `Finance/watchlist_Growth.json`

### 2. Add Tickers to Existing Watchlist

```bash
py -3 watchlist_manager.py --name Growth --add "TSLA,AMZN"
```

### 3. Create from Market Screener Results

```bash
# First, screen for micro-cap growth stocks
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap micro --near-52w-high 0.10 --output screened.json

# Then add to watchlist
py -3 watchlist_manager.py --name "Micro-Growth" --create --from-file screened.json
```

### 4. List All Watchlists

```bash
py -3 watchlist_manager.py --list-all
```

Output:
```
Watchlists:
  Growth (5 tickers, created 2026-05-20)
  Value (3 tickers, created 2026-05-15)
  Dividend (8 tickers, created 2026-04-10)
```

### 5. View Watchlist Details

```bash
py -3 watchlist_manager.py --name Growth --show
```

Output:
```json
{
  "name": "Growth",
  "tickers": ["AAPL", "MSFT", "NVDA", "GOOG", "TSLA", "AMZN"],
  "tags": ["technology", "mega-cap"],
  "created": "2026-05-20T10:30:00Z",
  "last_updated": "2026-05-26T14:15:00Z",
  "notes": "High-growth tech stocks"
}
```

### 6. Export for Sector Analysis

```bash
# Export as CSV for sector_score.py
py -3 watchlist_manager.py --name Growth --export csv \
  --output watchlist_growth.csv

# Then analyze
py -3 sector_score.py --input watchlist_growth.csv
```

### 7. Merge Watchlists

```bash
py -3 watchlist_manager.py --merge Growth Value \
  --output Finance/watchlist_Combined.json
```

### 8. Remove Tickers from Watchlist

```bash
py -3 watchlist_manager.py --name Growth --remove "TSLA,AMZN"
```

### 9. Track Changes Over Time

```bash
py -3 watchlist_manager.py --name Growth --history
```

Shows all changes with timestamps:
```
2026-05-26 14:15  Added: TSLA, AMZN
2026-05-20 10:30  Created with 5 tickers
```

## Command-Line Options

| Flag | Type | Description |
|------|------|-------------|
| `--name` | str | Watchlist name |
| `--create` | flag | Create new watchlist |
| `--tickers` | str | Comma-separated tickers |
| `--from-file` | path | Load tickers from JSON/CSV file |
| `--add` | str | Add tickers to existing list |
| `--remove` | str | Remove tickers from list |
| `--merge` | str | Merge two or more watchlists |
| `--show` | flag | Display watchlist details |
| `--list-all` | flag | List all watchlists |
| `--history` | flag | Show change history |
| `--export` | str | Export format: csv, json |
| `--output` | path | Save exported file |
| `--tags` | str | Add tags: "tech,mega-cap" |
| `--notes` | str | Add description/notes |

## Output Formats

**CSV Export** (for sector_score.py):
```csv
date,sector,close,ticker,source
2026-05-26,Technology,189.45,AAPL,watchlist_Growth
2026-05-26,Technology,417.90,MSFT,watchlist_Growth
```

**JSON Format**:
```json
{
  "name": "Growth",
  "description": "High-growth tech stocks",
  "tickers": ["AAPL", "MSFT", "NVDA", "GOOG", "TSLA", "AMZN"],
  "tags": ["technology", "mega-cap", "growth"],
  "created": "2026-05-20T10:30:00Z",
  "last_updated": "2026-05-26T14:15:00Z",
  "count": 6,
  "history": [
    {"timestamp": "2026-05-26T14:15:00Z", "action": "add", "tickers": ["TSLA", "AMZN"]},
    {"timestamp": "2026-05-20T10:30:00Z", "action": "create", "tickers": ["AAPL", "MSFT", "NVDA", "GOOG"]}
  ]
}
```

## Integration with Other Skills

**Build watchlist from screener → Export for sentiment:**
```bash
# 1. Screen stocks
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap large --output screened.json

# 2. Create watchlist
py -3 watchlist_manager.py --name "Large-Cap" --create --from-file screened.json

# 3. Export as CSV
py -3 watchlist_manager.py --name "Large-Cap" --export csv --output large_cap.csv

# 4. Analyze sentiment
py -3 sentiment.py --input large_cap.csv
```

**Combine multiple watchlists for portfolio analysis:**
```bash
py -3 watchlist_manager.py --merge Growth Value Dividend \
  --output combined.json

py -3 portfolio_analyzer.py --portfolio combined.json
```

## Reference

See [watchlist_manager.py](./scripts/watchlist_manager.py) for implementation details.
