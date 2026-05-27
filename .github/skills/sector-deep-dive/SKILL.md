---
name: sector-deep-dive
description: "Analyze sector performance: composition, trends, concentration, inter-sector correlations. Use for sector allocation decisions and comparative analysis."
argument-hint: "Provide sector or watchlist data"
user-invocable: true
---

# Sector Deep Dive

Perform in-depth sector analysis including composition breakdown, performance trends, concentration metrics, and inter-sector correlations. Make data-driven sector allocation decisions.

## When to Use

- Analyze sector composition and largest holdings
- Track sector performance trends and momentum
- Identify over/under-represented sectors in portfolio
- Study sector correlations and diversification benefits
- Find sector leaders and laggards
- Plan sector rotation strategies
- Compare sector valuations

## Features

- **Sector breakdown**: Top holdings, concentration, size distribution
- **Performance analysis**: Returns, volatility, momentum by sector
- **Correlation analysis**: How sectors move together
- **Trend detection**: Bullish/bearish sectors with momentum scores
- **Valuation comparison**: P/E and dividend yield by sector
- **Concentration risk**: Herfindahl index and top-5 concentration
- **Relative strength**: Sector rankings and rotation signals

## Procedure

### 1. Basic Sector Analysis (from market_data_output.json)

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --analyze sectors
```

Output shows:
- Sector composition and weights
- Average valuations by sector
- Sector-level statistics

### 2. Sector Performance Report

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --report performance --period 1y
```

Compares sector returns, volatility, Sharpe ratio.

### 3. Concentration Analysis

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --analyze concentration
```

Output:
```
SECTOR CONCENTRATION:
  Technology:    42.3% (HHI = 0.18)
    - AAPL: 15.2%
    - MSFT: 12.1%
    - GOOG:  8.5%
    - NVDA:  6.5%

  Financials:    28.1% (HHI = 0.12)
    - JPM:   14.0%
    - BAC:    8.2%
    - WFC:    5.9%

  Energy:       16.5% (HHI = 0.14)
    - XOM:    9.2%
    - CVX:    7.3%
```

HHI (Herfindahl-Hirschman Index): 0 = perfectly diversified, 1 = all in one stock.

### 4. Correlation Matrix

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --analyze correlations --output sector_correlations.json
```

Shows how sector movements relate to each other.

### 5. Find Sector Leaders and Laggards

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --rank-sectors --period 1y
```

Output:
```
SECTOR RANKINGS (1Y Performance):
  1. Technology      +35.2% (9.2% volatility)
  2. Financials      +12.1% (8.1% volatility)
  3. Consumer        +8.3% (7.5% volatility)
  ---
  9. Utilities       -2.1% (5.2% volatility)
 10. Energy          -5.8% (12.1% volatility)
```

### 6. Sector Valuation Comparison

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --compare-valuations --output sector_valuations.json
```

Compares P/E ratios, dividend yields by sector.

### 7. Detect Sector Rotation Signals

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --detect-rotation --sensitivity high
```

Identifies which sectors are gaining/losing momentum.

### 8. Build Sector-Balanced Portfolio Report

```bash
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --portfolio portfolio.csv \
  --target-allocation "30% Tech,25% Finance,20% Energy,25% Other" \
  --output rebalance_plan.json
```

Shows current vs. target, rebalancing suggestions.

## Output Examples

**Sector Composition (JSON):**
```json
{
  "sectors": {
    "Technology": {
      "weight": 0.423,
      "stock_count": 4,
      "avg_market_cap_category": "mega",
      "holdings": [
        {"ticker": "AAPL", "weight": 0.152},
        {"ticker": "MSFT", "weight": 0.121},
        {"ticker": "GOOG", "weight": 0.085},
        {"ticker": "NVDA", "weight": 0.065}
      ],
      "avg_pe": 28.3,
      "avg_dividend_yield": 0.006,
      "concentration_hhi": 0.18
    },
    "Financials": {
      "weight": 0.281,
      "stock_count": 3,
      "holdings": [
        {"ticker": "JPM", "weight": 0.140},
        {"ticker": "BAC", "weight": 0.082}
      ]
    }
  }
}
```

**Sector Correlations (Matrix):**
```
              Tech  Finance  Energy  Consumer
Technology    1.00    0.62    0.15     0.58
Financials    0.62    1.00    0.42     0.71
Energy        0.15    0.42    1.00     0.22
Consumer      0.58    0.71    0.22     1.00
```

## Command-Line Options

| Flag | Type | Description |
|------|------|-------------|
| `--input` | path | Market data or portfolio JSON |
| `--analyze` | str | Type: sectors, concentration, correlations, trends |
| `--report` | str | Report type: overview, performance, comparison |
| `--rank-sectors` | flag | Rank sectors by performance |
| `--compare-valuations` | flag | Compare P/E and yields by sector |
| `--detect-rotation` | flag | Find rotation signals |
| `--portfolio` | path | Portfolio CSV for allocation analysis |
| `--target-allocation` | str | Target allocation for comparison |
| `--period` | str | Time period: 1y, 6m, 3m, 1m |
| `--sensitivity` | str | Signal sensitivity: low, medium, high |
| `--output` | path | Save results to file |
| `--format` | str | Output format: json, csv, table |

## Integration with Other Skills

**Screen by sector, then analyze:**
```bash
# 1. Screen tech stocks
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap mega > tech_stocks.json

# 2. Deep dive on tech sector
py -3 sector_deep_dive.py --input tech_stocks.json --analyze sectors

# 3. Compare tech to other sectors
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --compare-valuations
```

**Portfolio rebalancing:**
```bash
# Analyze current portfolio sector allocation
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --portfolio portfolio.csv \
  --target-allocation "40% Tech,30% Finance,30% Other"

# Get rebalancing suggestions
py -3 sector_deep_dive.py --input rebalance_plan.json --report rebalancing
```

**Combine with sentiment analysis:**
```bash
# First do sector analysis
py -3 sector_deep_dive.py --input Finance/market_data_output.json \
  --rank-sectors --output sector_rankings.json

# Then run sentiment on top-performing sectors
py -3 sentiment.py --input prices.csv
```

## Sector Categories

Standard GICS sectors used:
- Technology
- Financials
- Healthcare
- Industrials
- Consumer Discretionary
- Consumer Staples
- Energy
- Utilities
- Real Estate
- Materials
- Communication Services

## Reference

See [sector_deep_dive.py](./scripts/sector_deep_dive.py) for implementation details.
