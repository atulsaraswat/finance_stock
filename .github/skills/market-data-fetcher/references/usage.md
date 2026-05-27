# Market Data Fetcher - Detailed Reference

## Installation

All dependencies are in Finance/requirements.txt. Ensure you have:

```bash
pip install yfinance pandas ib_insync
```

- **yfinance**: Primary source for live NASDAQ/NYSE data (required)
- **pandas**: CSV parsing  
- **ib_insync**: Optional, for IB Gateway fallback

## Examples

### Example 1: Fetch a Single Ticker

```bash
py -3 market_data.py --tickers AAPL
```

Output:
```json
[
  {
    "ticker": "AAPL",
    "currency": "USD",
    "current_price": 189.45,
    "52w_high": 199.62,
    "52w_low": 124.17,
    "market_cap": 2890000000000,
    "market_cap_category": "mega",
    "face_value": 0.00000625,
    "currency_symbol": "$",
    "source": "yfinance"
  }
]
```

### Example 2: Multiple Tickers (CLI)

```bash
py -3 market_data.py --tickers "AAPL,MSFT,TSLA,JPM,XOM"
```

### Example 3: CSV Input (Watchlist)

Create `watchlist.csv`:
```csv
symbol,sector,position_size
AAPL,Technology,100
MSFT,Technology,50
XOM,Energy,200
JPM,Financials,75
```

Run:
```bash
py -3 market_data.py --csv watchlist.csv
```

Uses only the `symbol` column; other columns are ignored.

### Example 4: Custom Output Location

```bash
py -3 market_data.py --tickers AAPL,MSFT --output custom/analysis_2026_05_26.json
```

### Example 5: With IB Gateway Running

If TWS/IB Gateway is running on a non-standard port:

```bash
py -3 market_data.py --tickers GOOG --ib-port 7497 --ib-host 127.0.0.1
```

### Example 6: Debug Mode

```bash
py -3 market_data.py --tickers AAPL,INVALID_TICKER --debug
```

Output shows which data source was tried, API calls, and failures.

## Output Fields Explanation

| Field | Source | Description |
|-------|--------|-------------|
| `ticker` | Input | Stock symbol (NASDAQ/NYSE) |
| `currency` | yfinance | ISO currency code (USD, EUR, etc.) |
| `current_price` | yfinance | Last trade price (CMP) |
| `52w_high` | yfinance | 52-week high from historical data |
| `52w_low` | yfinance | 52-week low from historical data |
| `market_cap` | yfinance | Market capitalization in USD |
| `market_cap_category` | Calculated | Category: nano, micro, small, mid, large, mega |
| `face_value` | yfinance | Par/face value per share |
| `currency_symbol` | Calculated | Symbol representation ($ € £ ¥ ₹ C$) |
| `source` | Script | Data source: 'yfinance' or 'ib_api' |

## Market Cap Categories

Based on market cap in USD billions:

| Category | Range |
|----------|-------|
| nano | < $0.3B |
| micro | $0.3B - $2B |
| small | $2B - $10B |
| mid | $10B - $100B |
| large | $100B - $200B |
| mega | > $200B |

## Fallback Logic

The script uses a two-stage approach:

1. **Primary**: Fetch all tickers from yfinance
   - Covers NASDAQ/NYSE stocks
   - Has market cap and fundamental data
   - Fastest for US equities

2. **Fallback** (if yfinance fails for some tickers):
   - Retries failed tickers via Interactive Brokers API
   - Requires TWS or IB Gateway running
   - Limited fields (52W high/low but no market cap)

## Integration with Existing Finance Scripts

### Combine with sector_score.py

```bash
# Get market data for tech stocks
py -3 market_data.py --tickers "AAPL,MSFT,GOOG,NVDA" --output tech_stocks.json

# Then analyze sector trends
py -3 sector_score.py --input prices.csv
```

### Combine with ib_integration.py

If using positions from IB:

```bash
# Extract ticker symbols
# Then fetch market data
py -3 market_data.py --csv positions.csv
```

### Combine with sentiment.py

```bash
# First get market data with current prices
py -3 market_data.py --csv watchlist.csv

# Then compute sentiment for those sectors
py -3 sentiment.py --input prices.csv
```

## Troubleshooting

### Error: "No module named yfinance"
```bash
pip install yfinance
```

### Error: "CSV must contain a 'symbol' column"
Ensure your CSV header includes `symbol`:
```csv
symbol,sector,position
AAPL,Tech,100
```

### Error: "No valid tickers provided"
- Check ticker format (should be uppercase, comma-separated)
- Verify CSV file path is correct
- Ensure at least one ticker is valid

### Result: Some tickers have `"market_cap": null`
- Data may be unavailable for penny stocks or OTC symbols
- Check that ticker is on NASDAQ or NYSE
- Try again later (data may be updating)

### Result: `"source": "ib_api"` for all tickers
- yfinance may be experiencing issues
- Ensure yfinance is installed and working: `python -c "import yfinance; print(yfinance.__version__)"`
- IB Gateway is being used as fallback

### Performance: Script takes 30+ seconds
- Normal for 10+ tickers with yfinance
- Each ticker requires fetching 1-year historical data
- Consider batch processing in groups of 5-10

## Data Accuracy Notes

- **52W High/Low**: Based on last 365 days of daily closes
- **Market Cap**: Calculated as price × shares outstanding (from company filings)
- **Face Value**: Par value per share (often $0 or very small for US stocks)
- **Currency**: Detected from stock country; almost always USD for NASDAQ/NYSE

## Advanced: Using with Python Scripts

```python
import json

with open('Finance/market_data_output.json') as f:
    data = json.load(f)

# Filter mega-cap stocks
mega_caps = [s for s in data if s['market_cap_category'] == 'mega']

# Sort by 52-week performance
performance = [
    {
        'ticker': s['ticker'],
        'range': s['52w_high'] - s['52w_low'],
        'current_price': s['current_price']
    }
    for s in data
]
```
