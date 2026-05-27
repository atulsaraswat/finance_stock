---
name: portfolio-analyzer
description: "Analyze portfolio holdings: diversification, sector allocation, performance tracking, risk metrics. Use for portfolio health checks, rebalancing decisions, or comparative analysis."
argument-hint: "Provide positions file (CSV with ticker, quantity, buy_price)"
user-invocable: true
---

# Portfolio Analyzer

Analyze your portfolio holdings for diversification, sector allocation, cost basis, unrealized gains, and risk concentration. Track performance and make rebalancing decisions.

## When to Use

- Review portfolio diversification across sectors and market caps
- Calculate weighted average costs and unrealized P&L
- Monitor concentration risk (overweight positions)
- Plan rebalancing based on target allocations
- Compare portfolio composition to benchmarks
- Track performance against market cap categories

## Features

- **Diversification metrics**: Sector allocation, market cap mix, position concentration
- **Performance tracking**: Cost basis, current value, unrealized gains/losses
- **Risk analysis**: Concentration ratios, portfolio beta estimation
- **Rebalancing guidance**: Target allocations vs. actual
- **Multiple analysis views**: Overview, sector breakdown, position detail

## Procedure

### 1. Create Portfolio CSV

Create `portfolio.csv`:
```csv
ticker,quantity,buy_price,buy_date,sector_override
AAPL,100,150.00,2025-01-15,Technology
MSFT,50,300.00,2025-02-20,Technology
XOM,75,105.00,2025-03-10,Energy
JPM,200,160.00,2025-01-01,Financials
VTI,500,225.00,2024-12-01,
```

### 2. Basic Portfolio Analysis

```bash
py -3 portfolio_analyzer.py --portfolio portfolio.csv
```

Output shows:
- Total portfolio value (at current prices)
- Allocation by sector and market cap
- Position sizes and concentration
- Unrealized gains/losses

### 3. Detailed Performance Report

```bash
py -3 portfolio_analyzer.py --portfolio portfolio.csv --report full
```

Includes:
- Per-position cost basis and P&L
- Sector performance comparison
- Risk concentration analysis
- Rebalancing recommendations

### 4. Compare to Benchmark

```bash
py -3 portfolio_analyzer.py --portfolio portfolio.csv \
  --benchmark "60% stocks / 40% bonds" --report comparison
```

### 5. Export Analysis

```bash
py -3 portfolio_analyzer.py --portfolio portfolio.csv \
  --output Finance/portfolio_analysis.json \
  --format csv  # or json
```

## Output Examples

**Console Summary:**
```
╔═══════════════════════════════════════════╗
║        PORTFOLIO ANALYSIS SUMMARY         ║
╠═══════════════════════════════════════════╣
║ Total Value        $145,230.50            ║
║ Total Cost Basis   $127,500.00            ║
║ Unrealized Gain    $17,730.50 (+13.9%)   ║
║ Positions          5                      ║
║ Concentration      AAPL: 28.5%            ║
╚═══════════════════════════════════════════╝

SECTOR ALLOCATION:
  Technology     40.2% (AAPL 28.5%, MSFT 11.7%)
  Financials     22.1% (JPM 22.1%)
  Energy         16.8% (XOM 16.8%)
  Other          20.9%

MARKET CAP MIX:
  Mega-cap       51.2%
  Large-cap      18.3%
  Mid-cap         7.5%
  Small-cap       3.2%
  Diversified     19.8%
```

**JSON Export:**
```json
{
  "summary": {
    "total_value": 145230.50,
    "total_cost_basis": 127500.00,
    "unrealized_gain": 17730.50,
    "unrealized_gain_pct": 13.9,
    "num_positions": 5
  },
  "positions": [
    {
      "ticker": "AAPL",
      "quantity": 100,
      "buy_price": 150.00,
      "current_price": 189.45,
      "cost_basis": 15000.00,
      "current_value": 18945.00,
      "unrealized_gain": 3945.00,
      "unrealized_gain_pct": 26.3,
      "portfolio_weight": 28.5,
      "sector": "Technology"
    }
  ],
  "sectors": {
    "Technology": { "weight": 40.2, "value": 58432.50 },
    "Financials": { "weight": 22.1, "value": 32079.00 }
  }
}
```

## Required CSV Columns

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| ticker | string | ✓ | Stock symbol |
| quantity | number | ✓ | Number of shares |
| buy_price | number | ✓ | Purchase price per share |
| buy_date | date | ✗ | Purchase date (YYYY-MM-DD) |
| sector_override | string | ✗ | Manual sector if not auto-detected |

## Command-Line Options

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--portfolio` | path | Required | CSV file with positions |
| `--report` | str | summary | Report type: summary, full, comparison |
| `--benchmark` | str | None | Benchmark description for comparison |
| `--rebalance-target` | str | None | JSON with target allocations |
| `--output` | path | stdout | Save results to file |
| `--format` | str | json | Output format: json, csv, table |
| `--market-data` | path | None | Use custom market_data.json instead of live fetch |

## Integration with Other Skills

**Step 1: Fetch market data**
```bash
py -3 market_data.py --csv portfolio.csv
```

**Step 2: Analyze portfolio**
```bash
py -3 portfolio_analyzer.py --portfolio portfolio.csv
```

**Step 3: Screen by criteria**
```bash
py -3 portfolio_analyzer.py --portfolio portfolio.csv \
  --report full > portfolio_snapshot.json
```

## Reference

See [portfolio_analyzer.py](./scripts/portfolio_analyzer.py) for implementation details.
