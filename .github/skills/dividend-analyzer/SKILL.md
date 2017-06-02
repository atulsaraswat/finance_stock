---
name: dividend-analyzer
description: "Analyze dividend metrics: yield, payout ratio, coverage, history, and sustainability. Use for income investing and identifying dividend traps."
argument-hint: "Provide tickers or portfolio CSV"
user-invocable: true
---

# Dividend Analyzer

Comprehensive dividend analysis: yield, payout ratio, coverage ratios, growth history, and sustainability. Identify high-yield income plays and avoid dividend traps.

## When to Use

- Build high-dividend income portfolios
- Identify sustainable vs. risky dividends
- Screen for dividend growth candidates
- Detect dividend reduction red flags
- Compare dividend yields vs. risk
- Plan dividend reinvestment strategies
- Find ex-dividend dates for timing

## Features

- **Dividend yield**: Current and historical yields
- **Payout ratio**: Percentage of earnings paid out
- **Coverage ratios**: Earnings/cashflow available to cover dividends
- **Growth analysis**: Dividend growth history (3Y, 5Y)
- **Sustainability score**: Will dividend be maintained?
- **Safety assessment**: Risk of dividend cut
- **Sector comparison**: Dividend yields by sector
- **Tax efficiency**: Qualified vs. unqualified dividends

## Procedure

### 1. Basic Dividend Profile

```bash
py -3 dividend_analyzer.py --tickers MSFT,JPM,CVX
```

Shows:
- Current dividend yield
- Annual dividend amount
- Payout ratio
- Dividend coverage
- Safety rating

### 2. Find High-Yield Stocks

```bash
py -3 dividend_analyzer.py --tickers "JPM,BAC,GS,XOM,CVX,T,PG,JNJ" \
  --min-yield 0.03 \
  --min-coverage 1.5
```

Returns stocks with:
- Yield ≥ 3%
- Dividend covered 1.5x by earnings

### 3. Dividend Safety Analysis

```bash
py -3 dividend_analyzer.py --tickers "T,VZ,IBM" \
  --report safety --output dividend_safety.json
```

Assesses:
- Payout ratio (safe: <60% for stocks)
- Free cash flow coverage
- Dividend history (cuts/suspensions)
- Trend (growing/stable/declining)

### 4. Dividend Growth Portfolio

```bash
py -3 dividend_analyzer.py --tickers "MSFT,JNJ,PG,KO" \
  --min-growth-rate 0.05 \
  --min-yield 0.02
```

Finds:
- Dividend growth ≥5% annually
- Yield ≥2%
- Conservative payout (<60%)

### 5. Detect Dividend Traps

```bash
py -3 dividend_analyzer.py --tickers "T,VZ,IBM,C" \
  --detect-traps \
  --output dividend_traps.json
```

Identifies red flags:
- Unsustainable payout ratio (>90%)
- Declining coverage
- Recent or potential cuts

### 6. Compare Dividend Yields

```bash
py -3 dividend_analyzer.py --tickers "JNJ,PG,MMM,IBM" \
  --compare-sectors --format table
```

## Output Example

**Dividend Safety Report:**
```
╔════════════════════════════════════════════════════════════╗
║           DIVIDEND ANALYSIS - JPM (J.P. Morgan)            ║
╠════════════════════════════════════════════════════════════╣

CURRENT YIELD:         3.2%
ANNUAL DIVIDEND:       $6.00 per share
PAYOUT RATIO:          32%
DIVIDEND COVERAGE:     3.1x (by earnings)
                       2.8x (by operating cash flow)

SAFETY ASSESSMENT:     ✓ VERY SAFE
Quality Score:         92/100

DIVIDEND HISTORY:
  2023: $5.50/share  (+12%)
  2022: $4.90/share  (+13%)
  2021: $4.30/share  (+12%)
  5Y Growth Rate:     +10.2% CAGR

RED FLAGS:            None

RECOMMENDATION:       STRONG BUY (Income)
```

**Dividend Trap Detection:**
```json
{
  "ticker": "C",
  "yield": 5.2,
  "safety_score": 28,
  "traps_detected": [
    {
      "trap": "UNSUSTAINABLE_PAYOUT",
      "severity": "CRITICAL",
      "payout_ratio": 95,
      "message": "Paying out 95% of earnings as dividend - very little room for growth"
    },
    {
      "trap": "DECLINING_COVERAGE",
      "severity": "HIGH",
      "coverage_trend": "declining 3Y",
      "message": "Dividend coverage has fallen from 2.5x to 1.1x"
    },
    {
      "trap": "HISTORY_OF_CUTS",
      "severity": "CRITICAL",
      "last_cut": "2020",
      "message": "Dividend suspended during financial crisis, may happen again"
    }
  ],
  "recommendation": "AVOID - High dividend cut risk"
}
```

## Dividend Metrics Reference

| Metric | Formula | Safe Range | Interpretation |
|--------|---------|------------|-----------------|
| Dividend Yield | Annual Div / Stock Price | 2-5% | Current income as % of price |
| Payout Ratio | Dividend / Earnings | <60% | Lower = safer, more room for growth |
| Coverage Ratio | Earnings / Dividend | >1.5x | How many times dividend is covered by earnings |
| FCF Coverage | Operating Cash Flow / Dividend | >1.5x | Cash available to pay dividend |
| Dividend Growth | YoY change in dividend | >5% | Dividend raising pace |
| Yield on Cost | Original Dividend / Orig Price | Varies | Income return for long-term holders |

## Command-Line Options

| Flag | Type | Description |
|------|------|-------------|
| `--tickers` | str | Comma-separated tickers |
| `--portfolio` | path | Portfolio CSV file |
| `--watchlist` | path | Watchlist JSON file |
| `--min-yield` | float | Minimum dividend yield (0.03 = 3%) |
| `--max-yield` | float | Maximum yield (screen for traps) |
| `--min-coverage` | float | Minimum dividend coverage ratio |
| `--min-growth-rate` | float | Minimum dividend growth rate |
| `--detect-traps` | flag | Identify dividend trap red flags |
| `--report` | str | Type: summary, safety, growth, traps |
| `--compare-sectors` | flag | Compare yields by sector |
| `--format` | str | Output: json, csv, table |
| `--output` | path | Save results to file |
| `--ex-dividend-dates` | flag | Show upcoming ex-dividend dates |

## Dividend Safety Checklist

✓ **Safe Dividend Characteristics:**
- [ ] Payout ratio <60% (room for growth)
- [ ] Dividend coverage >2.0x
- [ ] Free cash flow coverage >1.5x
- [ ] Stable/growing earnings
- [ ] Consistent dividend history
- [ ] Dividend growth at/above inflation

⚠️ **Caution Signs:**
- [ ] Payout ratio 60-80% (some concern)
- [ ] Coverage ratio 1.0-1.5x (tight)
- [ ] Declining coverage trend
- [ ] Yield significantly above sector average
- [ ] Recent dividend cuts or suspensions

🚨 **Dividend Traps (Avoid):**
- [ ] Payout ratio >90% (unsustainable)
- [ ] Coverage <1.0x (cutting dividend incoming)
- [ ] Yield >>sector average (may signal trouble)
- [ ] Declining or negative earnings
- [ ] History of dividend cuts
- [ ] Negative free cash flow

## Integration with Other Skills

**Income portfolio screening:**
```bash
# 1. Find high-yield stocks
py -3 dividend_analyzer.py --tickers "JPM,CVX,XOM,PG,JNJ" \
  --min-yield 0.03 --detect-traps

# 2. Confirm earnings quality
py -3 earnings_quality_analyzer.py --tickers "JPM,CVX,XOM" \
  --min-quality-score 75

# 3. Create income watchlist
py -3 watchlist_manager.py --name "HighDividend" --create \
  --from-file high_yield_safe.json
```

**Dividend income tracking:**
```bash
# Track portfolio dividend income
py -3 dividend_analyzer.py --portfolio portfolio.csv \
  --report growth --output dividend_forecast.json
```

**Compare to valuation:**
```bash
# Find cheap, safe dividend stocks
py -3 valuation_ratio_analyzer.py --status undervalued
py -3 dividend_analyzer.py --min-coverage 2.0 \
  --detect-traps
# Combine results for value + income
```

## Reference

See [dividend_analyzer.py](./scripts/dividend_analyzer.py) for implementation details.
