---
name: valuation-ratio-analyzer
description: "Analyze P/E, P/B, EV/EBITDA ratios: compare current to sector average and stock's 5-year historical. Use for value investing, mean reversion, and valuation trend analysis."
argument-hint: "Provide tickers, market data file, or watchlist"
user-invocable: true
---

# Valuation Ratio Analyzer

Analyze key valuation ratios (P/E, P/B, EV/EBITDA) with deep comparisons: current value vs. sector average vs. stock's own historical 5-year average. Identify undervalued/overvalued conditions and valuation trends.

## When to Use

- Identify stocks trading below/above their historical averages (mean reversion)
- Compare valuations to sector peers (relative valuation)
- Find undervalued growth stocks or expensive value traps
- Track valuation trend changes over time
- Build value screens with ratio thresholds
- Combine with fundamental analysis for stock selection
- Detect valuation extremes (z-score based)

## Features

- **Three key ratios**: P/E (Price-to-Earnings), P/B (Price-to-Book), EV/EBITDA
- **Multi-level comparison**: Current vs. sector avg vs. 5Y average
- **Valuation z-scores**: Statistical measure of deviation from historical mean
- **Status classification**: Undervalued, Fair, Overvalued, Extremely Overvalued
- **Historical trends**: How ratio has trended over time
- **Sector benchmarking**: Auto-detect or explicit sector assignment
- **Flexible data sources**: Live yfinance or pre-computed market data
- **Multiple output formats**: JSON, CSV, detailed comparison tables

## Procedure

### 1. Basic Analysis (Current Ratios vs. Historical Avg)

```bash
py -3 valuation_ratio_analyzer.py --tickers AAPL,MSFT,GOOG
```

Output shows:
- Current P/E, P/B, EV/EBITDA
- 5-year historical average for each
- How far current is from historical (percentage)
- Valuation status (undervalued/fair/overvalued)

### 2. Compare to Sector Average

```bash
py -3 valuation_ratio_analyzer.py --tickers AAPL,MSFT,GOOG \
  --compare-sectors
```

For each stock, shows:
- Current ratio
- Sector average ratio
- How stock compares to peers
- Valuation z-score

### 3. Full Valuation Analysis Report

```bash
py -3 valuation_ratio_analyzer.py --tickers AAPL,MSFT \
  --report full \
  --output Finance/valuation_analysis.json
```

Includes:
- Current vs. 5Y historical average (table)
- Current vs. sector average
- Valuation z-scores (statistical deviation)
- Status classification
- Historical trend (rising/falling)

### 4. Analyze Using Pre-Computed Market Data

```bash
py -3 valuation_ratio_analyzer.py \
  --input Finance/market_data_output.json \
  --compare-sectors \
  --output enriched_valuations.json
```

### 5. Custom Historical Period

```bash
py -3 valuation_ratio_analyzer.py --tickers AAPL,MSFT \
  --historical-period 3y \
  --compare-sectors
```

Options: 1y, 3y, 5y (default), 10y

### 6. Screen by Valuation Status

```bash
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,GOOG,NVDA,TSLA" \
  --status undervalued \
  --output undervalued_stocks.json
```

Returns only undervalued stocks (trading below 5Y average).

### 7. Find Mean Reversion Candidates

```bash
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,GOOG,NVDA,JPM,XOM" \
  --extreme-z-score \
  --output mean_reversion.json
```

Finds stocks with extreme valuation z-scores (potential mean reversion).

### 8. Export Comparison Table

```bash
py -3 valuation_ratio_analyzer.py --tickers AAPL,MSFT,GOOG \
  --compare-sectors --format csv \
  --output valuation_comparison.csv
```

## Output Examples

**Console Summary (Current vs. 5Y Historical):**
```
╔════════════════════════════════════════════════════════════╗
║           VALUATION RATIO ANALYSIS - AAPL                  ║
╠════════════════════════════════════════════════════════════╣

P/E RATIO:
  Current:        28.5
  5Y Historical:  25.3 (avg)
  Difference:     +12.6% (OVERVALUED)
  Range (5Y):     18.2 - 33.4

P/B RATIO:
  Current:        46.2
  5Y Historical:  42.1 (avg)
  Difference:     +9.7% (FAIR)
  Range (5Y):     32.5 - 58.3

EV/EBITDA:
  Current:        22.1
  5Y Historical:  20.5 (avg)
  Difference:     +7.8% (FAIR)
  Range (5Y):     15.3 - 28.9

VALUATION STATUS: FAIR
```

**Sector Comparison Table:**
```
Ticker  P/E (Cur)  P/E (Sector)  Z-Score  Status
------  ---------  ------------  -------  -----------
AAPL    28.5       24.1          +1.2     OVERVALUED
MSFT    32.1       24.1          +2.8     EXTREMELY OV.
GOOG    25.3       24.1          +0.4     FAIR
NVDA    48.2       24.1          +4.9     EXTREMELY OV.
```

**Valuation Z-Score:**
- Z = (Current - 5Y Avg) / 5Y StdDev
- Z > 2.0 = Extremely overvalued
- Z > 1.0 = Overvalued
- Z -1.0 to 1.0 = Fair value
- Z < -1.0 = Undervalued
- Z < -2.0 = Extremely undervalued

**JSON Output:**
```json
{
  "ticker": "AAPL",
  "analysis_date": "2026-05-26",
  "current_ratios": {
    "pe": 28.5,
    "pb": 46.2,
    "ev_ebitda": 22.1
  },
  "historical_avg": {
    "period": "5y",
    "pe": 25.3,
    "pb": 42.1,
    "ev_ebitda": 20.5
  },
  "sector_avg": {
    "sector": "Technology",
    "pe": 24.1,
    "pb": 38.5,
    "ev_ebitda": 19.8
  },
  "z_scores": {
    "pe": 1.2,
    "pb": 0.8,
    "ev_ebitda": 0.6
  },
  "valuation_status": "FAIR",
  "comparison": {
    "vs_historical": "+12.6%",
    "vs_sector": "+18.3%"
  },
  "trend": "rising"
}
```

## Command-Line Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--tickers` | str | None | Comma-separated tickers (AAPL,MSFT,GOOG) |
| `--input` | path | None | Market data JSON file (alternative to --tickers) |
| `--watchlist` | path | None | Watchlist JSON file |
| `--compare-sectors` | flag | False | Add sector average comparison |
| `--historical-period` | str | 5y | Historical lookback: 1y, 3y, 5y, 10y |
| `--status` | str | None | Filter by: undervalued, fair, overvalued, extreme |
| `--extreme-z-score` | flag | False | Show only extreme valuation z-scores |
| `--report` | str | summary | Type: summary, full, sectors, comparison |
| `--format` | str | json | Output format: json, csv, table |
| `--output` | path | None | Save to file |
| `--sector` | str | None | Override sector for all tickers |
| `--debug` | flag | False | Show data sources and API calls |

## Valuation Status Classification

| Status | Z-Score | Meaning |
|--------|---------|---------|
| Extremely Undervalued | < -2.0 | Trading far below historical average (strong buy signal?) |
| Undervalued | -2.0 to -1.0 | Trading below average (potential value) |
| Fair | -1.0 to 1.0 | Trading in normal range |
| Overvalued | 1.0 to 2.0 | Trading above average (potential sell signal?) |
| Extremely Overvalued | > 2.0 | Trading far above average (warning signal) |

## Ratio Definitions

### P/E Ratio (Price-to-Earnings)
- **Formula**: Stock Price / Earnings Per Share
- **Interpretation**: Lower = cheaper relative to earnings, Higher = growth premium
- **Typical Range**: 15-25 (by sector)
- **Use**: Most common valuation metric

### P/B Ratio (Price-to-Book)
- **Formula**: Stock Price / Book Value Per Share
- **Interpretation**: <1.0 = trading below book value, >1.0 = premium to book
- **Typical Range**: 1.0-5.0 (varies by industry)
- **Use**: Asset-heavy industries (finance, manufacturing)

### EV/EBITDA (Enterprise Value to EBITDA)
- **Formula**: (Market Cap + Debt - Cash) / EBITDA
- **Interpretation**: Lower = cheaper, less influenced by capital structure
- **Typical Range**: 8-15 (mature companies), 15-25 (growth)
- **Use**: Comparing companies with different capital structures

## Integration with Other Skills

**Combine with market-data-fetcher:**
```bash
# 1. Fetch market data
py -3 market_data.py --tickers "AAPL,MSFT,GOOG,NVDA"

# 2. Analyze valuations
py -3 valuation_ratio_analyzer.py --input Finance/market_data_output.json \
  --compare-sectors
```

**Combine with fundamental-enricher:**
```bash
# 1. Enrich with P/E, dividend yield, etc.
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --valuation-score

# 2. Deep dive on valuation ratios
py -3 valuation_ratio_analyzer.py --input enriched.json \
  --compare-sectors --report full
```

**Screen + Analyze Valuations:**
```bash
# 1. Screen for mega-cap stocks
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap mega --output mega_caps.json

# 2. Analyze valuations
py -3 valuation_ratio_analyzer.py --input mega_caps.json \
  --compare-sectors --extreme-z-score
```

**Build watchlist of undervalued stocks:**
```bash
# 1. Find undervalued stocks
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,JPM,XOM,CVX,BAC" \
  --status undervalued --output undervalued.json

# 2. Create watchlist
py -3 watchlist_manager.py --name "Undervalued" --create \
  --from-file undervalued.json --tags "value,undervalued"

# 3. Monitor
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Undervalued.json
```

## Reference

See [valuation_ratio_analyzer.py](./scripts/valuation_ratio_analyzer.py) for implementation details and advanced configuration.
