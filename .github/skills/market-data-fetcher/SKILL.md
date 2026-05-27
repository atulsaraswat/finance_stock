---
name: market-data-fetcher
description: "Fetch live NASDAQ/NYSE market data: current price, 52W high/low, market cap, face value. Use for building market analysis tools, comparing stock fundamentals, or enriching trading datasets."
argument-hint: "Provide tickers list or CSV file path"
user-invocable: true
---

# Market Data Fetcher

Fetch comprehensive live market data for NASDAQ/NYSE stocks including current market price (CMP), 52-week highs/lows, market capitalization, and face value.

## When to Use

- Building equity analysis and screening tools
- Comparing stock fundamentals across a watchlist
- Enriching trading or sentiment datasets with market data
- Validating ticker symbols and retrieving current quotes
- Creating market-wide dashboards with key metrics

## Features

- **Multiple data sources**: yfinance (primary) with Interactive Brokers fallback
- **Flexible input**: CLI comma-separated tickers or CSV file with symbol column
- **Rich metrics**: CMP, 52W high, 52W low, market cap, face value, market cap category
- **JSON output**: Saved to Finance directory by default

## Procedure

### 1. Basic Usage (CLI Tickers)

```bash
py -3 market_data.py --tickers AAPL,MSFT,TSLA
```

Output saved to `Finance/market_data_output.json`

### 2. CSV File Input

Create a CSV with at least a `symbol` column:
```csv
symbol,notes
AAPL,Technology
MSFT,Technology
XOM,Energy
```

Then run:
```bash
py -3 market_data.py --csv positions.csv
```

### 3. Custom Output Path

```bash
py -3 market_data.py --tickers AAPL,MSFT --output my_stocks.json
```

### 4. Use with IB Fallback

If IB Gateway is running on a custom port:
```bash
py -3 market_data.py --tickers AAPL,MSFT --ib-host 127.0.0.1 --ib-port 7497
```

## Output Format

JSON array with ticker data:

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
  },
  ...
]
```

**Market cap categories**: nano, micro, small, mid, large, mega

## Key Parameters

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--tickers` | str | None | Comma-separated ticker symbols (AAPL,MSFT,TSLA) |
| `--csv` | path | None | CSV file with symbol column |
| `--output` | path | Finance/market_data_output.json | JSON output file path |
| `--ib-host` | str | 127.0.0.1 | IB Gateway host (fallback) |
| `--ib-port` | int | 7497 | IB Gateway port |
| `--client-id` | int | 1 | IB client ID |
| `--debug` | flag | False | Print debug info (data sources tried, API calls) |

## Integration with Finance Scripts

Use the output to:

1. **Enrich sector_score.py**: Combine with sector analysis
   ```bash
   py -3 market_data.py --tickers AAPL,MSFT,GOOG > stocks.json
   ```

2. **Filter by market cap**: Combine with ib_integration.py positions
   ```bash
   py -3 market_data.py --csv positions.csv
   ```

## Troubleshooting

- **No data returned**: Check ticker symbols are valid NASDAQ/NYSE codes
- **yfinance fails**: Will automatically fall back to IB API if configured
- **CSV parse error**: Ensure CSV has a `symbol` column
- **IB connection refused**: Verify TWS/IB Gateway is running and API is enabled

## Script Reference

See [market_data.py](./scripts/market_data.py) for implementation details and advanced configuration.
