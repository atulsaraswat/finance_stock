# Valuation Ratio Analyzer - Deep Dive Guide

## Key Concepts

### Why These Three Ratios?

**P/E Ratio (Price-to-Earnings)**
- Most commonly used valuation metric
- Lower = cheaper relative to earnings
- Useful for comparing within same industry
- Sensitive to earnings quality and accounting methods

**P/B Ratio (Price-to-Book)**
- Compares price to shareholder equity
- Useful for asset-heavy industries (banks, insurance, manufacturing)
- <1.0 = trading below book value (potential value)
- Less affected by accounting earnings manipulation

**EV/EBITDA (Enterprise Value to EBITDA)**
- Capital-structure neutral (includes debt)
- Best for cross-company comparisons with different capital structures
- Uses operational earnings (EBITDA = Earnings Before Interest, Tax, Depreciation, Amortization)
- Common in M&A and debt analysis

## Workflow Examples

### Example 1: Find Mean Reversion Candidates

Stocks trading far above/below their historical average often revert:

```bash
# Find extremely overvalued stocks (potential shorts)
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,NVDA,TSLA,GOOG" \
  --extreme-z-score --status overvalued

# Find extremely undervalued stocks (potential buys)
py -3 valuation_ratio_analyzer.py --tickers "JPM,BAC,XOM,CVX,IBM" \
  --extreme-z-score --status undervalued
```

**Interpretation:**
- Z-score > 2.0 or < -2.0 = extreme deviation
- Often signal mean reversion opportunity
- But check WHY the ratio is extreme (good/bad news)

### Example 2: Value Investing Screen

Find stocks undervalued relative to sector:

```bash
# 1. Get market data
py -3 market_data.py --tickers "JPM,BAC,GS,MS,WFC"

# 2. Analyze valuations vs sector
py -3 valuation_ratio_analyzer.py --input Finance/market_data_output.json \
  --compare-sectors --status undervalued

# 3. Create watchlist
py -3 watchlist_manager.py --name "UndervaluedFinance" --create \
  --from-file analysis_output.json --tags "value,finance"
```

### Example 3: Compare to Historical Average

Track if stock is reverting to mean:

```bash
# Get current valuations
py -3 valuation_ratio_analyzer.py --tickers AAPL --report full

# Output shows:
# - Current P/E: 28.5
# - 5Y Average P/E: 25.3
# - Z-score: +1.2 (overvalued but not extreme)
# - Status: FAIR VALUE
```

**Interpretation:**
- If z-score = +1.2, stock is 1.2 standard deviations above mean
- Good sign of reversion if: company fundamentals haven't changed dramatically
- Bad if: company fundamentally improved (higher earnings now justify higher PE)

### Example 4: Sector Rotation

Identify cheap vs. expensive sectors:

```bash
# Compare tech mega-caps
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,GOOG,META,NVDA" \
  --compare-sectors --format table

# Compare financials
py -3 valuation_ratio_analyzer.py --tickers "JPM,BAC,GS,MS" \
  --compare-sectors --format table
```

**Output interpretation:**
- Which sector has lower P/E relative to 5Y average?
- Which sector is cheaper than peers?
- Consider rotating into undervalued sectors

## Integration Workflows

### Workflow A: Market Data → Valuation → Watchlist → Monitor

```bash
# 1. Fetch current market data
py -3 market_data.py --tickers "AAPL,MSFT,GOOG,JPM,XOM,CVX"

# 2. Analyze valuations
py -3 valuation_ratio_analyzer.py --input Finance/market_data_output.json \
  --compare-sectors --report full --output valuation_report.json

# 3. Filter for undervalued
py -3 valuation_ratio_analyzer.py --input Finance/market_data_output.json \
  --status undervalued --output undervalued_candidates.json

# 4. Create watchlist
py -3 watchlist_manager.py --name "Undervalued" --create \
  --from-file undervalued_candidates.json

# 5. Monitor daily
py -3 price_alert_monitor.py --watchlist Finance/watchlist_Undervalued.json \
  --report daily --output daily_monitor.json
```

### Workflow B: Fundamental Analysis → Valuation Extremes

```bash
# 1. Enrich with fundamentals
py -3 fundamental_enricher.py --input Finance/market_data_output.json \
  --valuation-score

# 2. Find valuation extremes
py -3 valuation_ratio_analyzer.py --input enriched.json \
  --extreme-z-score --format table

# 3. Screen for high z-scores
py -3 market_screener.py --input Finance/market_data_output.json \
  --market-cap mega --output mega_stocks.json

# 4. Analyze valuations of mega-cap extremes
py -3 valuation_ratio_analyzer.py --input mega_stocks.json \
  --compare-sectors --extreme-z-score
```

### Workflow C: Sector Allocation Rebalancing

```bash
# 1. Analyze each sector's valuation
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,GOOG" \
  --compare-sectors --output tech_valuations.json

py -3 valuation_ratio_analyzer.py --tickers "JPM,BAC,GS" \
  --compare-sectors --output finance_valuations.json

py -3 valuation_ratio_analyzer.py --tickers "XOM,CVX,MPC" \
  --compare-sectors --output energy_valuations.json

# 2. Compare which sectors are cheapest
# 3. Consider sector rotation into cheaper sectors
```

## Interpreting Z-Scores

### Statistical Interpretation

```
Z-Score Distribution (Normal Distribution):
- 68% of values fall within ±1 std dev
- 95% fall within ±2 std dev
- 99.7% fall within ±3 std dev

For Valuation:
- Z = 0: Trading at 5Y average (fair)
- Z = +1: 84th percentile (above average, but normal)
- Z = +2: 97th percentile (EXTREMELY OVERVALUED)
- Z = -1: 16th percentile (below average, but normal)
- Z = -2: 3rd percentile (EXTREMELY UNDERVALUED)
```

### Action Points

| Z-Score | Interpretation | Action |
|---------|----------------|--------|
| > 2.0 | Extremely overvalued | Sell/reduce, check for value trap |
| 1.0 to 2.0 | Overvalued | Hold/sell, monitor for reversal |
| -0.5 to 0.5 | Fair value | Hold, normal range |
| -1.0 to -0.5 | Undervalued | Buy/add, good entry |
| < -2.0 | Extremely undervalued | Strong buy, but check why |

## Common Pitfalls

### Pitfall 1: Ignoring the "Why"

Just because a stock has Z > 2.0 doesn't mean it's overvalued:
- Company may have improved fundamentals (justified higher multiple)
- Growth acceleration may warrant premium
- Example: NVIDIA's high P/E was justified by AI revolution

**Solution**: Combine with fundamental analysis. Check:
- Is earnings growing faster? (justifies higher P/E)
- Has company market position changed?
- Industry tailwinds/headwinds?

### Pitfall 2: Using Stale Historical Averages

5-year average is useful but can be obsolete:
- Company may have fundamentally changed
- Industry structure may have shifted
- Secular growth/decline factors

**Solution**: Review the composition of historical average:
- Is it trended up or down?
- Recent sub-period vs. full 5Y?
- Look at 3-year average too for recent trends

### Pitfall 3: Sector Comparison Issues

Sector categorization matters:
- GICS sectors are broad (e.g., "Technology" includes chip makers and cloud software)
- Different businesses have different P/E norms
- Compare to peer group, not just sector average

**Solution**: Manual review of true peers:
- Use --sector flag to narrow to specific sub-industry
- Compare to direct competitors, not whole sector
- Consider size (mega-cap vs. small-cap) comparisons

### Pitfall 4: Accounting Quality

High P/E could mean:
- Expensive (true)
- Earnings quality issues (aggressive accounting)
- Non-recurring items inflating apparent profits

**Check**:
- Cash earnings vs. reported earnings
- Free cash flow vs. net income
- One-time items in recent quarters

## Advanced Topics

### Mean Reversion Strategy

When stock P/E is 2+ std dev from mean:

```bash
# Find mean reversion candidates
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT,JPM" \
  --extreme-z-score --status overvalued --output mean_reversion.json

# Historical success rate ~60-70% revert within 12-24 months
# But size of reversion varies widely
```

### Pairs Trading

Compare two similar companies' valuations:

```bash
# Compare Tech mega-caps
py -3 valuation_ratio_analyzer.py --tickers "AAPL,MSFT" \
  --compare-sectors --report full

# If AAPL P/E = +1.5 std dev, MSFT P/E = -0.5 std dev
# Potential: Short AAPL, Long MSFT (bet on mean convergence)
```

### Sector Rotation

Use valuation metrics to guide allocation:

```bash
# Get valuations for sector leaders
# Compare Z-scores across sectors
# Rotate into sectors with lowest Z-scores (cheapest)
# Rotate out of highest Z-scores (most expensive)
```
