---
name: fundamental-enricher
description: "Enrich market data with fundamental metrics: P/E ratio, dividend yield, EPS, debt-to-equity, ROE. Use for fundamental analysis and screened result enrichment."
argument-hint: "Provide market data JSON file to enrich"
user-invocable: true
---

# Fundamental Enricher

Enrich your market data with fundamental metrics: P/E ratio, dividend yield, earnings per share, debt-to-equity, ROE, and other key ratios. Useful for fundamental screening and value analysis.

## When to Use

- Add fundamental metrics to market_data_fetcher output
- Screen stocks by P/E, dividend yield, or other ratios
- Prepare data for fundamental vs. technical analysis
- Build value stock filters
- Compare valuation metrics across sectors
- Combine with technicals for holistic screening

## Features

- **Fundamental metrics**: P/E, EPS, dividend yield, debt ratios
- **Quality metrics**: ROE, ROA, profit margin, asset turnover
- **Growth metrics**: EPS growth, revenue growth, earnings forecast
- **Valuation scores**: Simple PEG score, value ranking
- **Sector comparisons**: How stock valuations compare to sector average
- **Data deduplication**: Smart merging with existing market data

## Procedure

### 1. Basic Enrichment (Add Fundamentals to Market Data)

```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json
```

Output: `Finance/market_data_enriched.json` with fundamentals added.

### 2. Enrichment with Sector Comparison

```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --compare-sectors
```

Adds sector-relative metrics for each stock.

### 3. Create Valuation Score

```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --valuation-score --output enriched_with_scores.json
```

Generates composite valuation score (1-100) for ranking.

### 4. Focus on Dividend Stocks

```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --min-dividend-yield 0.03 --output dividend_stocks.json
```

Returns only stocks with 3%+ dividend yield.

### 5. Value Stock Filter

```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --max-pe 15 --min-roe 0.15 --output value_stocks.json
```

Finds stocks with P/E < 15 and ROE > 15%.

### 6. Export Enhanced Data for Further Analysis

```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --format csv --output Finance/fundamentals.csv
```

## Output Example

**Enhanced JSON:**
```json
[
  {
    "ticker": "AAPL",
    "current_price": 189.45,
    "52w_high": 199.62,
    "52w_low": 124.17,
    "market_cap": 2890000000000,
    "fundamental": {
      "pe_ratio": 28.5,
      "eps": 6.63,
      "earnings_growth_1yr": 0.12,
      "dividend_yield": 0.005,
      "roe": 0.82,
      "roa": 0.14,
      "debt_to_equity": 1.33,
      "profit_margin": 0.26,
      "peg_score": 2.37,
      "valuation_score": 65
    },
    "sector_comparison": {
      "sector": "Technology",
      "sector_avg_pe": 32.1,
      "pe_percentile": 25,
      "sector_avg_dividend_yield": 0.008,
      "dividend_percentile": 30
    }
  }
]
```

**CSV Export:**
```csv
ticker,current_price,pe_ratio,eps,dividend_yield,roe,debt_to_equity,valuation_score
AAPL,189.45,28.5,6.63,0.005,0.82,1.33,65
MSFT,417.90,32.1,13.04,0.008,0.35,0.92,58
JPM,160.25,9.8,16.32,0.024,0.98,1.08,82
```

## Filtering Options

| Flag | Type | Description |
|------|------|-------------|
| `--min-pe` | float | Minimum P/E ratio |
| `--max-pe` | float | Maximum P/E ratio |
| `--min-dividend-yield` | float | Minimum dividend yield (0.05 = 5%) |
| `--min-roe` | float | Minimum ROE (0.15 = 15%) |
| `--max-debt-to-equity` | float | Maximum debt-to-equity ratio |
| `--min-eps-growth` | float | Minimum 1Y EPS growth |
| `--compare-sectors` | flag | Add sector comparison metrics |
| `--valuation-score` | flag | Calculate composite valuation score |
| `--format` | str | Output format: json, csv |
| `--output` | path | Save enriched data |

## Command Reference

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--input` | path | Required | Market data JSON file |
| `--output` | path | Finance/market_data_enriched.json | Output file |
| `--format` | str | json | Output format |
| `--include-missing` | flag | False | Include stocks with missing data |
| `--cache-dir` | path | ./.yfinance_cache | Cache fundamental data |

## Integration with Other Skills

**Market data → Enrich → Screen:**
```bash
# 1. Fetch market data
py -3 market_data.py --tickers "AAPL,MSFT,JPM,XOM,CVX"

# 2. Enrich with fundamentals
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --compare-sectors --valuation-score

# 3. Screen by value metrics
py -3 market_screener.py --input Finance/market_data_enriched.json \
  --min-pe 20 --max-pe 35 --min-roe 0.15
```

**Dividend Analysis:**
```bash
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --min-dividend-yield 0.03 --output dividend_candidates.json

# Then build watchlist
py -3 watchlist_manager.py --name "Dividend" --create \
  --from-file dividend_candidates.json
```

**Compare to Portfolio:**
```bash
# Get fundamentals for your portfolio
py -3 portfolio_analyzer.py --portfolio portfolio.csv \
  --market-data Finance/market_data_enriched.json
```

## Fundamental Metrics Explained

| Metric | Calculation | Interpretation |
|--------|-------------|-----------------|
| P/E Ratio | Stock Price / EPS | Lower = potentially undervalued |
| EPS | Net Income / Shares Outstanding | Higher = more profitable per share |
| Dividend Yield | Annual Dividend / Stock Price | Higher = more income for investors |
| ROE | Net Income / Shareholder Equity | Higher = better capital efficiency |
| ROA | Net Income / Total Assets | Higher = better asset utilization |
| Debt/Equity | Total Debt / Total Equity | Lower = less financial risk |
| PEG Score | P/E Ratio / Earnings Growth Rate | <1 = potentially undervalued growth |
| Profit Margin | Net Income / Revenue | Higher = more efficient operations |

## Reference

See [fundamental_enricher.py](./scripts/fundamental_enricher.py) for implementation details.
