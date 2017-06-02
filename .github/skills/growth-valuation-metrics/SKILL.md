---
name: growth-valuation-metrics
description: "Analyze growth-adjusted valuations: PEG ratio, FCF yield, revenue multiples. Use for valuing growth stocks fairly and identifying overpriced growth."
argument-hint: "Provide tickers and growth rates"
user-invocable: true
---

# Growth Valuation Metrics

Analyze growth-adjusted valuation metrics: PEG ratio (P/E-to-Growth), Free Cash Flow yield, Revenue multiples, and other growth-appropriate measures. Fairly value growth stocks and identify overpriced growth.

## When to Use

- Value high-growth tech stocks fairly (not just P/E)
- Compare growth stocks vs. value stocks on apples-to-apples basis
- Identify overpriced growth (high PEG)
- Find underpriced growth (low PEG)
- Analyze free cash flow yield for sustainable growth
- Screen by revenue multiples (for pre-profit companies)
- Combine growth expectations with valuation

## Features

- **PEG Ratio**: P/E divided by earnings growth rate (ideal = 1.0)
- **FCF Yield**: Free cash flow / Market cap (cash available to shareholders)
- **Price-to-Sales**: Less manipulable than P/E (pre-profit companies)
- **EV/Revenue**: Valuation per dollar of revenue
- **FCF-to-Growth**: FCF yield adjusted for growth rate
- **Dividend-Adjusted Yield**: Total yield (dividend + buybacks)
- **Revenue Growth**: Multi-year revenue growth trends
- **Quality of Growth**: Revenue growth converted to FCF

## Procedure

### 1. Find Fairly-Valued Growth (PEG = 1.0)

```bash
py -3 growth_valuation_metrics.py --tickers AAPL,MSFT,NVDA,TSLA,META \
  --metric peg \
  --target-peg 1.0
```

Returns stocks with PEG ≈ 1.0 (fairly valued for their growth).

### 2. Identify Overpriced Growth

```bash
py -3 growth_valuation_metrics.py --tickers "NVDA,TSLA,META,GOOG" \
  --metric peg \
  --max-peg 0.8
```

Finds undervalued growth (PEG <0.8 = cheap for growth rate).

### 3. Free Cash Flow Yield Analysis

```bash
py -3 growth_valuation_metrics.py --tickers AAPL,MSFT,GOOG \
  --metric fcf-yield \
  --compare-to-dividend-yield
```

Shows:
- Free cash flow yield (cash return to shareholders)
- vs. actual dividend yield
- Quality: is FCF growing faster than dividends?

### 4. Revenue Multiple Screening

```bash
# For pre-profit or high-growth companies
py -3 growth_valuation_metrics.py --tickers "TSLA,NVDA,META" \
  --metric price-to-sales \
  --max-multiple 5.0
```

Finds stocks with P/S <5.0 (reasonable for growth).

### 5. Quality of Growth Assessment

```bash
py -3 growth_valuation_metrics.py --tickers AAPL,MSFT,GOOG \
  --report growth-quality
```

Shows:
- Revenue growth rate
- Operating cash flow growth
- Free cash flow growth
- Quality: is growth being converted to cash?

### 6. Compare Growth Valuations

```bash
py -3 growth_valuation_metrics.py --tickers "AAPL,MSFT,GOOG,META,NVDA" \
  --metrics peg,fcf-yield,price-sales \
  --format table
```

Multi-metric comparison across growth stocks.

### 7. Historical PEG Analysis

```bash
py -3 growth_valuation_metrics.py --tickers AAPL \
  --metric peg --historical 5y --detect-extremes
```

Shows PEG history and when stock was most/least expensive for growth.

## Output Example

**PEG Analysis:**
```
╔────────────────────────────────────────────────────────────╗
║           PEG RATIO ANALYSIS (P/E ÷ Growth%)              ║
╠────────────────────────────────────────────────────────────╣

Ticker  P/E   Growth%  PEG     Assessment
------  ---   -------  ---     ----------------
AAPL    28.5  8%       3.56    🔴 Expensive for growth
MSFT    32.1  10%      3.21    🔴 Expensive for growth
GOOG    25.3  12%      2.11    🟠 Fairly valued
NVDA    48.2  35%      1.38    🟡 Slightly expensive
META    24.1  25%      0.96    ✓ Fairly valued
TSLA    65.3  20%      3.27    🔴 Very expensive

IDEAL TARGET: PEG = 1.0
```

**Free Cash Flow Yield Report:**
```json
{
  "ticker": "AAPL",
  "metrics": {
    "market_cap": 2890000000000,
    "operating_cash_flow": 110500000000,
    "capex": 10800000000,
    "free_cash_flow": 99700000000,
    "fcf_yield": 3.45,
    "dividend_yield": 0.52,
    "total_shareholder_yield": 3.97
  },
  "analysis": {
    "fcf_covers_dividend": "191x",
    "quality": "EXCELLENT",
    "assessment": "FCF yield (3.45%) >> dividend yield (0.52%). Company returning 191% more cash than actual dividend."
  }
}
```

**Growth Quality Assessment:**
```
Revenue Growth:        +8% YoY
Operating Cash Flow:   +12% YoY
Free Cash Flow:        +15% YoY
Assessment:            ✓ EXCELLENT
Quality Score:         95/100

Interpretation: Revenue growing 8%, but FCF growing 15%.
This means operating leverage is working - company getting
more efficient at converting revenue to cash. HIGH QUALITY GROWTH.
```

## Valuation Metrics Reference

| Metric | Formula | Fair Range | Interpretation |
|--------|---------|-----------|-----------------|
| **PEG Ratio** | P/E ÷ Annual EPS Growth (%) | 0.8-1.2 | <1.0 = undervalued for growth, >1.5 = expensive |
| **FCF Yield** | Free Cash Flow / Market Cap | 5-15% | Higher = more cash returned to shareholders |
| **Price/Sales** | Market Cap / Annual Revenue | 1.0-5.0 | Lower = cheaper, useful for pre-profit |
| **EV/Revenue** | Ent. Value / Annual Revenue | 2-8x | Debt-adjusted revenue multiple |
| **Price/Book** | Stock Price / Book Value | 1-5x | Higher for growth, lower for value |
| **FCF-Adjusted P/E** | Market Cap / Free Cash Flow | Varies | Better than P/E (uses actual cash) |

## Command-Line Options

| Flag | Type | Description |
|------|------|-------------|
| `--tickers` | str | Comma-separated tickers |
| `--input` | path | Market data JSON file |
| `--watchlist` | path | Watchlist JSON file |
| `--metric` | str | peg, fcf-yield, price-sales, ev-revenue, all |
| `--metrics` | str | Compare multiple: peg,fcf-yield,price-sales |
| `--target-peg` | float | Filter by target PEG (e.g., 1.0) |
| `--max-peg` | float | Maximum PEG (find undervalued growth) |
| `--min-fcf-yield` | float | Minimum FCF yield |
| `--max-price-sales` | float | Maximum price-to-sales ratio |
| `--growth-rates` | str | Provide growth rates: ticker:rate (AAPL:8 MSFT:10) |
| `--report` | str | Type: summary, comparison, growth-quality, extremes |
| `--historical` | str | Historical period: 1y, 3y, 5y |
| `--detect-extremes` | flag | Find historically extreme valuations |
| `--compare-sectors` | flag | Compare across sectors |
| `--format` | str | Output: json, csv, table |
| `--output` | path | Save results to file |

## Growth vs. Value Framework

**Using PEG for Stock Selection:**

```
PEG < 0.7   →  Excellent value, strong buy (rare)
PEG 0.7-1.0 →  Good value, buy
PEG 1.0-1.5 →  Fair value, hold
PEG 1.5-2.0 →  Expensive, sell
PEG > 2.0   →  Very expensive, avoid (value trap risk)
```

**FCF Yield for Income-Focused Investors:**

```
FCF Yield > 10%  →  Very attractive (rare for large-cap)
FCF Yield 5-10%  →  Good, above average
FCF Yield 2-5%   →  Normal/fair
FCF Yield <2%    →  Below average, limited cash return
```

## Integration with Other Skills

**Growth vs. Value comparison:**
```bash
# 1. Analyze growth stocks with PEG
py -3 growth_valuation_metrics.py --tickers "AAPL,MSFT,GOOG,NVDA" \
  --metric peg --report comparison

# 2. Analyze value stocks with P/E + P/B
py -3 valuation_ratio_analyzer.py --tickers "JPM,CVX,XOM" \
  --compare-sectors

# 3. Compare: which looks better valued?
```

**Growth + Earnings Quality:**
```bash
# 1. Find fairly-valued growth (PEG)
py -3 growth_valuation_metrics.py --tickers "AAPL,MSFT,META" \
  --metric peg --target-peg 1.0

# 2. Confirm earnings are real cash
py -3 earnings_quality_analyzer.py --input growth_stocks.json \
  --min-quality-score 75

# 3. Create watchlist of quality growth
```

**Dividend + FCF Yield:**
```bash
# Compare dividend yield to FCF yield
py -3 growth_valuation_metrics.py --tickers "AAPL,MSFT,JPM" \
  --metric fcf-yield

py -3 dividend_analyzer.py --tickers "AAPL,MSFT,JPM" \
  --report summary
```

## Reference

See [growth_valuation_metrics.py](./scripts/growth_valuation_metrics.py) for implementation details.
