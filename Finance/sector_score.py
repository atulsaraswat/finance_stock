"""Sector score and outlook calculator.

Computes per-sector score, tailwinds, and headwinds using price data and
existing sentiment models.

Usage:
    py -3 sector_score.py --input prices.csv --output sector_score.json

If no input is provided, the script uses sample data.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from sentiment import analyze, generate_sample_data, sma


@dataclass
class SectorOutlook:
    sector: str
    three_signal: str
    regime_model: str
    final_sentiment: str
    sector_score: int
    tailwinds: str
    headwinds: str


SECTOR_THEMES: Dict[str, Dict[str, List[str]]] = {
    'Technology': {
        'tailwinds': [
            'digital transformation',
            'AI and cloud adoption',
            'software-led business models',
        ],
        'headwinds': [
            'regulatory scrutiny',
            'cyclical semiconductor demand',
            'valuation pressure',
        ],
    },
    'Energy': {
        'tailwinds': [
            'renewables investment',
            'energy transition demand',
            'infrastructure spending',
        ],
        'headwinds': [
            'fossil fuel phase-out risk',
            'geopolitical volatility',
            'commodity-price swings',
        ],
    },
    'Financials': {
        'tailwinds': [
            'rate normalization',
            'fintech adoption',
            'credit expansion',
        ],
        'headwinds': [
            'credit stress',
            'regulatory change',
            'digital disruption',
        ],
    },
    'Healthcare': {
        'tailwinds': [
            'aging population',
            'biotech innovation',
            'healthcare digitalization',
        ],
        'headwinds': [
            'pricing pressure',
            'regulatory risk',
            'trial failures',
        ],
    },
    'Industrials': {
        'tailwinds': [
            'manufacturing automation',
            'reshoring trends',
            'capital goods demand',
        ],
        'headwinds': [
            'cyclical downturns',
            'trade tensions',
            'input cost inflation',
        ],
    },
    'Consumer Discretionary': {
        'tailwinds': [
            'consumer spending recovery',
            'e-commerce growth',
            'experiential spending',
        ],
        'headwinds': [
            'income pressure',
            'higher rates',
            'lower discretionary budgets',
        ],
    },
    'Consumer Staples': {
        'tailwinds': [
            'defensive demand',
            'branding power',
            'stable cash flow',
        ],
        'headwinds': [
            'low growth',
            'commodity cost inflation',
            'discount retail pressure',
        ],
    },
    'Utilities': {
        'tailwinds': [
            'grid modernization',
            'renewable integration',
            'stable dividend demand',
        ],
        'headwinds': [
            'rate sensitivity',
            'capital-intensity',
            'regulatory oversight',
        ],
    },
    'Materials': {
        'tailwinds': [
            'infrastructure spending',
            'resource demand',
            'recycling and reuse',
        ],
        'headwinds': [
            'commodity cyclicality',
            'trade barriers',
            'environmental regulation',
        ],
    },
    'Real Estate': {
        'tailwinds': [
            'rental income stability',
            'urbanization',
            'interest in REITs',
        ],
        'headwinds': [
            'rate sensitivity',
            'occupancy risk',
            'development oversupply',
        ],
    },
    'Communication Services': {
        'tailwinds': [
            'online advertising',
            'streaming growth',
            '5G and content delivery',
        ],
        'headwinds': [
            'ad spending cycles',
            'privacy regulation',
            'subscription fatigue',
        ],
    },
}


def describe_outlook(sector: str, final_sentiment: str) -> Tuple[str, str]:
    theme = SECTOR_THEMES.get(sector, {
        'tailwinds': ['diversification and secular growth'],
        'headwinds': ['macro uncertainty and cyclical risk'],
    })
    tailwinds = theme['tailwinds']
    headwinds = theme['headwinds']
    if final_sentiment == 'bullish':
        extra_tailwinds = 'momentum and favorable market positioning'
        extra_headwinds = 'valuation sensitivity'
    elif final_sentiment == 'bearish':
        extra_tailwinds = 'reversion potential if sentiment improves'
        extra_headwinds = 'weak secular demand and positioning risk'
    else:
        extra_tailwinds = 'balanced growth drivers with watch for catalysts'
        extra_headwinds = 'mixed macro signals and policy risk'

    return (
        '; '.join(tailwinds + [extra_tailwinds]),
        '; '.join(headwinds + [extra_headwinds]),
    )


def momentum_score(df: pd.DataFrame) -> float:
    close = df['close']
    lookback = min(60, len(close) - 1)
    if lookback < 10:
        return 0.0
    return float((close.iloc[-1] - close.iloc[-1 - lookback]) / close.iloc[-1 - lookback]) * 100


def volatility_score(df: pd.DataFrame) -> float:
    returns = df['close'].pct_change().dropna()
    if returns.empty:
        return 0.0
    return float(returns.rolling(60, min_periods=10).std().iloc[-1] * 100)


def calculate_sector_score(df: pd.DataFrame, params: Dict[str, object]) -> Dict[str, object]:
    sentiment = analyze(df, params)
    trend_pct = momentum_score(df)
    vol_pct = volatility_score(df)

    sentiment_value = 70 if sentiment.final_sentiment == 'bullish' else 50 if sentiment.final_sentiment == 'neutral' else 30
    regime_value = 70 if sentiment.regime_model == 'bullish' else 50 if sentiment.regime_model == 'neutral' else 30
    base_score = (sentiment_value + regime_value) / 2

    trend_adj = np.clip(trend_pct * 0.5, -15, 15)
    vol_adj = np.clip((10 - vol_pct) * 0.5, -10, 10)
    raw_score = base_score + trend_adj + vol_adj
    normalized = int(np.clip(raw_score, 0, 100))

    tailwinds, headwinds = describe_outlook(df['sector'].iloc[0], sentiment.final_sentiment)
    return {
        'sector': df['sector'].iloc[0],
        'three_signal': sentiment.three_signal,
        'regime_model': sentiment.regime_model,
        'final_sentiment': sentiment.final_sentiment,
        'sector_score': normalized,
        'trend_pct': round(trend_pct, 2),
        'vol_pct': round(vol_pct, 2),
        'outlook_tailwinds': tailwinds,
        'outlook_headwinds': headwinds,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Calculate sector score, tailwinds, and headwinds.')
    parser.add_argument('--input', help='CSV file with columns date,sector,close', default=None)
    parser.add_argument('--output', help='Output JSON file', default='sector_score_output.json')
    args = parser.parse_args()

    if args.input:
        df = pd.read_csv(args.input, parse_dates=['date'])
    else:
        df = generate_sample_data()

    params = {
        'sma_short': 50,
        'sma_long': 200,
        'rsi_window': 14,
        'rsi_bull': 60.0,
        'rsi_bear': 40.0,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'regime_min_len': 60,
        'regime_long_w': 200,
        'regime_lookback': 20,
        'vol_rolling': 60,
    }

    results: List[Dict[str, object]] = []
    for sector, group in df.groupby('sector'):
        group_sorted = group.sort_values('date').reset_index(drop=True)
        results.append(calculate_sector_score(group_sorted, params))

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
