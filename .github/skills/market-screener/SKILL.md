---
name: market-screener
description: "Filter and screen NASDAQ/NYSE stocks by market cap, price ranges, 52W performance, volatility. Use for building watchlists, finding opportunities, or scanning for specific market conditions."
argument-hint: "Provide screening criteria or JSON config file"
user-invocable: true
---

# Market Screener

Screen NASDAQ/NYSE stocks based on multiple criteria: market capitalization, price ranges, 52-week performance, volatility, and custom thresholds.

## When to Use

- Find stocks in specific market cap ranges (mega-cap value, small-cap growth, etc.)
- Identify stocks near 52-week highs or lows
- Filter by volatility or price momentum
- Build targeted watchlists for sector analysis
- Discover breakout or breakdown candidates

## Features

- **Market cap screening**: nano, micro, small, mid, large, mega categories
- **Price filtering**: Current price ranges, 52W high/low proximity
- **Performance metrics**: 52W range, volatility calculations
- **Flexible configuration**: CLI flags or JSON config file
- **Multiple output formats**: JSON, CSV, or pretty-printed table

## Procedure

### 1. Screen by Market Cap

```bash
py -3 market_screener.py --input Finance/market_data_output.json --market-cap mega,large
```

Returns: All mega and large-cap stocks from your market data.

### 2. Screen by Price Range

```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --min-price 100 --max-price 500
```

### 3. Screen by 52W Performance

```bash
# Stocks trading near 52W lows (potential value)
py -3 market_screener.py --input Finance/market_data_output.json \
  --near-52w-low 0.15
```

This finds stocks within 15% of their 52-week low.

### 4. Complex Screening (JSON Config)

Create `screen_config.json`:
```json
{
  "market_cap": ["micro", "small"],
  "min_price": 20,
  "max_price": 100,
  "near_52w_high": 0.05,
  "volatility_min": 0.02,
  "volatility_max": 0.15,
  "output_format": "csv"
}
```

Then run:
```bash
py -3 market_screener.py --input Finance/market_data_output.json --config screen_config.json
```

### 5. Save Screened Results

```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap large --output Finance/screened_large_cap.json
```

## Output Options

**JSON** (default):
```json
[
  {
    "ticker": "AAPL",
    "current_price": 189.45,
    "52w_high": 199.62,
    "52w_low": 124.17,
    "market_cap_category": "mega",
    "52w_range_pct": 60.8,
    "distance_from_52w_high": -5.1,
    "distance_from_52w_low": 52.5,
    "volatility": 0.18
  }
]
```

**CSV**:
```
ticker,current_price,52w_high,52w_low,market_cap_category,distance_from_52w_high,volatility
AAPL,189.45,199.62,124.17,mega,-5.1,0.18
```

**Table** (pretty-print):
```
ticker  price    52W High  52W Low  Category  52W Range%
------  -----    --------  -------  --------  ----------
AAPL    $189.45  $199.62   $124.17  mega      60.8%
MSFT    $417.90  $425.00   $310.00  mega      37.1%
```

## Filtering Options

| Flag | Type | Example | Description |
|------|------|---------|-------------|
| `--market-cap` | str | mega,large,mid | Comma-separated categories |
| `--min-price` | float | 50 | Minimum current price |
| `--max-price` | float | 500 | Maximum current price |
| `--near-52w-high` | float | 0.05 | Within X% of 52W high (find breakouts) |
| `--near-52w-low` | float | 0.15 | Within X% of 52W low (value plays) |
| `--volatility-min` | float | 0.10 | Minimum annualized volatility |
| `--volatility-max` | float | 0.40 | Maximum annualized volatility |
| `--output-format` | str | json, csv, table | Output format |
| `--output` | path | Finance/results.json | Save to file |
| `--config` | path | config.json | Load criteria from JSON file |

## Integration with Other Skills

**After market-data-fetcher:**
```bash
py -3 market_data.py --tickers "AAPL,MSFT,GOOG,NVDA,TSLA"
py -3 market_screener.py --input Finance/market_data_output.json --market-cap mega
```

**Feed to watchlist-manager:**
```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap micro,small --output micro_small_stocks.json
py -3 watchlist_manager.py --add micro_small_stocks.json --name "Growth"
```

**Combine with sector analysis:**
```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --near-52w-high 0.10 --output breakouts.json
# Then analyze these breakouts with sector_score.py
```

## Reference

See [market_screener.py](./scripts/market_screener.py) for implementation details.
