# Market Screener - Usage Examples

## Quick Start

Screen for mega-cap stocks:
```bash
py -3 market_screener.py --input Finance/market_data_output.json --market-cap mega
```

## Common Workflows

### Find Value Stocks (Low Price, Not at 52W Low)

```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap large,mega \
  --min-price 50 \
  --max-price 200 \
  --near-52w-low 0.20
```

Returns: Large/mega-cap stocks trading within 20% of 52W low in $50-200 range.

### Find Breakout Candidates (Near 52W High, High Volatility)

```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap mega \
  --near-52w-high 0.05 \
  --volatility-min 0.15 \
  --output breakout_candidates.json
```

### Screen Using JSON Config

Create `micro_growth.json`:
```json
{
  "market_cap": ["micro", "small"],
  "min_price": 5,
  "max_price": 50,
  "volatility_min": 0.20,
  "output_format": "table"
}
```

Run:
```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --config micro_growth.json
```

## Integration Examples

**Step 1: Fetch market data**
```bash
py -3 market_data.py --tickers "AAPL,MSFT,GOOG,NVDA,TSLA,JPM,XOM,CVX"
```

**Step 2: Screen for breakouts**
```bash
py -3 market_screener.py --input Finance/market_data_output.json \
  --near-52w-high 0.10 --market-cap mega --output breakouts.json
```

**Step 3: Add to watchlist**
```bash
py -3 watchlist_manager.py --name "Breakouts" --create \
  --from-file breakouts.json --tags "breakout,technical"
```

**Step 4: Export for sentiment analysis**
```bash
py -3 watchlist_manager.py --name "Breakouts" --export csv \
  --output breakouts.csv

py -3 sentiment.py --input breakouts.csv
```

## Output Interpretation

**distance_from_52w_high**:
- Negative values = trading below 52W high (near breakout zone)
- -5% = stock is 5% below 52W high
- Example: AAPL at -2% means it's 2% away from breaking out

**distance_from_52w_low**:
- Positive values = trading above 52W low (recovery potential)
- +50% = stock is 50% above 52W low
- Example: Stock at +20% has recovered 20% from lows

**52w_range_pct**:
- Measures volatility: (High - Low) / Average Price
- >30% = high volatility
- <10% = low volatility/stable stock
