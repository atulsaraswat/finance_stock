---
name: earnings-quality-analyzer
description: "Assess earnings quality: compare net income to operating cash flow, check for one-time items, analyze working capital changes. Use for detecting accounting manipulation and validating earnings sustainability."
argument-hint: "Provide tickers or market data file"
user-invocable: true
---

# Earnings Quality Analyzer

Assess the quality and sustainability of reported earnings. Compare net income to operating cash flow, identify one-time items, analyze working capital changes, and detect potential accounting red flags.

## When to Use

- Validate if earnings are backed by real cash flow
- Detect accounting gimmicks or unsustainable earnings
- Identify one-time items inflating reported profits
- Screen for cash conversion quality
- Evaluate sustainability of dividend payments
- Compare earnings quality across peers
- Identify value traps with fake earnings

## Features

- **Cash flow quality score**: How much earnings convert to operating cash flow
- **One-time item detection**: Identify non-recurring gains/losses
- **Working capital analysis**: Track cash tied up in operations
- **Quality ratio**: Operating cash flow / Net Income
- **Accruals analysis**: High accruals = lower quality earnings
- **Cash conversion trend**: Multi-year cash flow trends
- **Sustainability assessment**: Will these earnings last?
- **Peer comparison**: Quality rankings within sector

## Procedure

### 1. Basic Quality Check

```bash
py -3 earnings_quality_analyzer.py --tickers AAPL,MSFT,GOOG
```

Shows for each stock:
- Net income vs. operating cash flow
- Cash conversion ratio (CFO / NI)
- Quality score (0-100)
- Red flag warnings

### 2. Quality vs. Reported P/E

```bash
# Compare reported P/E to cash-basis P/E
py -3 earnings_quality_analyzer.py --tickers AAPL,MSFT \
  --compare-to-cash-earnings
```

Output:
- Reported P/E
- P/E based on operating cash flow
- Quality adjustment (high quality = lower apparent cost)

### 3. Detect Accounting Red Flags

```bash
py -3 earnings_quality_analyzer.py --tickers "AAPL,MSFT,TSLA,ENRON" \
  --detect-red-flags \
  --output quality_red_flags.json
```

Flags:
- Earnings >> cash flow (possible manipulation)
- Growing accruals (may indicate channel stuffing)
- Working capital deterioration
- Rising receivables (sales quality issue)
- Inventory buildup (demand problem)

### 4. Multi-Year Quality Trend

```bash
py -3 earnings_quality_analyzer.py --tickers AAPL \
  --period 5y --report trend
```

Shows year-over-year:
- Net income growth
- Operating cash flow growth
- Divergence (quality trend)

### 5. Screen for High-Quality Stocks

```bash
py -3 earnings_quality_analyzer.py --tickers "AAPL,MSFT,GOOG,NVDA,JPM,XOM" \
  --min-quality-score 75 \
  --output high_quality.json
```

Returns only stocks with 75+ quality score.

### 6. Compare Quality Within Sector

```bash
py -3 earnings_quality_analyzer.py --tickers "AAPL,MSFT,META,GOOG" \
  --compare-sectors --format table
```

## Output Example

**Quality Scorecard:**
```
Ticker  Net Income  Operating CFO  Conversion  Quality  Assessment
------  ----------  -------  -----  ----------  -------  -----------
AAPL    $94.7B      $110.5B  117%   92/100      ✓ Excellent
MSFT    $72.4B      $74.2B   103%   88/100      ✓ Very Good
TSLA    $12.6B      $1.3B    10%    18/100      ✗ Red Flag
ENRON   $979M       -$464M   -47%   5/100       ✗ CRITICAL
```

**Red Flags Report:**
```json
{
  "ticker": "TSLA",
  "quality_score": 18,
  "red_flags": [
    {
      "flag": "EARNINGS_VS_CASHFLOW_DIVERGENCE",
      "severity": "CRITICAL",
      "message": "Net income $12.6B but operating cash flow only $1.3B (10% conversion)",
      "implication": "Earnings quality highly questionable"
    },
    {
      "flag": "RISING_ACCRUALS",
      "severity": "HIGH",
      "message": "Accruals increased 40% YoY, now 28% of earnings",
      "implication": "Growing gap between earnings and cash may indicate sustainability risk"
    }
  ]
}
```

**Quality Metrics:**

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| Cash Conversion | Operating CFO / Net Income | >100% = excellent, >80% = good, <50% = poor |
| Accruals Ratio | (ΔWC + D&A) / Total Assets | Lower = higher quality |
| Free Cash Flow | Operating CFO - CapEx | Real cash available to shareholders |
| Days Sales Outstanding | Receivables / (Revenue/365) | Rising = quality concern |
| Days Inventory Outstanding | Inventory / (COGS/365) | Rising = demand weakness |

## Command-Line Options

| Flag | Type | Description |
|------|------|-------------|
| `--tickers` | str | Comma-separated tickers |
| `--input` | path | Market data JSON file |
| `--watchlist` | path | Watchlist JSON file |
| `--compare-to-cash-earnings` | flag | Compare P/E ratios (reported vs. cash basis) |
| `--detect-red-flags` | flag | Identify accounting red flags |
| `--min-quality-score` | int | Filter by minimum quality score (0-100) |
| `--period` | str | Historical period: 1y, 3y, 5y |
| `--report` | str | Type: summary, detailed, trend, red-flags |
| `--compare-sectors` | flag | Compare quality within sector |
| `--format` | str | Output: json, csv, table |
| `--output` | path | Save results to file |

## Red Flag Checklist

🚨 **Critical Red Flags** (potential fraud):
- [ ] Earnings >> Operating Cash Flow (>2x divergence)
- [ ] Negative or declining operating cash flow with rising profits
- [ ] Large one-time gains inflating earnings
- [ ] Frequent accounting changes
- [ ] Related party transactions

⚠️ **Warning Signs** (quality concerns):
- [ ] Growing accruals (>20% of earnings)
- [ ] Rising receivables (days sales outstanding increasing)
- [ ] Inventory buildup (days inventory outstanding rising)
- [ ] Working capital deterioration
- [ ] Declining free cash flow despite profit growth

✓ **Quality Indicators** (sustainable earnings):
- [ ] Operating CFO > Net Income (natural working capital cycle)
- [ ] Stable or declining accruals
- [ ] Operating cash flow growing with earnings
- [ ] Free cash flow positive and growing
- [ ] Consistent quality year-over-year

## Integration with Other Skills

**Combine with valuation-ratio-analyzer:**
```bash
# 1. Find undervalued stocks
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,TSLA" \
  --status undervalued

# 2. Check earnings quality
py -3 earnings_quality_analyzer.py --tickers "AAPL,MSFT,TSLA" \
  --detect-red-flags

# 3. If high quality + undervalued = strong buy signal
```

**Combine with fundamental-enricher:**
```bash
# 1. Enrich market data
py -3 fundamental_enricher.py --input Finance/market_data_output.json

# 2. Analyze earnings quality
py -3 earnings_quality_analyzer.py --input enriched.json \
  --report detailed
```

**Build watchlist of high-quality, cheap stocks:**
```bash
# 1. Screen for value
py -3 valuation_ratio_analyzer.py --status undervalued \
  --output undervalued.json

# 2. Filter by earnings quality
py -3 earnings_quality_analyzer.py --input undervalued.json \
  --min-quality-score 75 --output quality_value.json

# 3. Create watchlist
py -3 watchlist_manager.py --name "QualityValue" --create \
  --from-file quality_value.json
```

## Reference

See [earnings_quality_analyzer.py](./scripts/earnings_quality_analyzer.py) for implementation details.
