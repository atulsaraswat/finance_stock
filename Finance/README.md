# Market Sentiment Analyzer

This repository contains `sentiment.py`, a small Python script that computes per-sector market sentiment using two models:

- The Most Reliable Way (3-Signal Confirmation)
- The Quantitative Way (Market Regime Model)

Final sentiment rules:

- If BOTH models are bullish → final sentiment = bullish
- If BOTH models are bearish → final sentiment = bearish
- If models disagree → final sentiment = neutral

Quick start:

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run (generates sample data if no CSV provided):

```bash
python sentiment.py
```

To analyze your CSV (columns: `date,sector,close`):

```bash
python sentiment.py --input prices.csv --output results.json
```

Interactive Brokers integration:

```bash
py -3 ib_integration.py --output ib_sentiment.json
```

If the IB API is not available or you prefer an offline fallback, supply positions via CSV with columns `symbol` and optional `position`:

```bash
py -3 ib_integration.py --positions-csv positions.csv --output ib_sentiment.json
```

Sector score and outlook calculator:

```bash
py -3 sector_score.py --input prices.csv --output sector_score.json
```

If no input file is provided, the script uses generated sample data.
