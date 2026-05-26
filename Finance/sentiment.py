"""Market sentiment analyzer

Computes per-sector sentiment using two models:
1. The Most Reliable Way (3-Signal Confirmation)
2. The Quantitative Way (Market Regime Model)

Final sentiment rules:
- If BOTH models are bullish -> final = bullish
- If BOTH models are bearish -> final = bearish
- If disagreement -> final = neutral

Usage:
    python sentiment.py [--input prices.csv]

If no input CSV is provided, the script generates sample data.
"""
from __future__ import annotations
import argparse
import json
from dataclasses import dataclass
from typing import List, Dict, Any

import numpy as np
import pandas as pd


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window, min_periods=1).mean()


def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window, min_periods=1).mean()
    ma_down = down.rolling(window, min_periods=1).mean()
    rs = ma_up / (ma_down.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)


def macd_hist(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd = ema_fast - ema_slow
    macd_signal = ema(macd, signal)
    return macd - macd_signal


def three_signal_confirmation(df: pd.DataFrame, params: Dict[str, Any]) -> str:
    close = df['close']
    if len(close) < max(30, params.get('sma_short', 50)):
        return 'neutral'

    s1 = 'neutral'
    short_w = int(params.get('sma_short', 50))
    long_w = int(params.get('sma_long', 200))
    sma_short = sma(close, short_w).iloc[-1]
    sma_long = sma(close, long_w).iloc[-1] if len(close) >= long_w else sma(close, int(len(close) / 2)).iloc[-1]
    if sma_short > sma_long:
        s1 = 'bullish'
    elif sma_short < sma_long:
        s1 = 'bearish'

    s2 = 'neutral'
    r = rsi(close, window=int(params.get('rsi_window', 14)))
    r_latest = r.iloc[-1]
    r_bull = float(params.get('rsi_bull', 60))
    r_bear = float(params.get('rsi_bear', 40))
    if r_latest > r_bull:
        s2 = 'bullish'
    elif r_latest < r_bear:
        s2 = 'bearish'

    s3 = 'neutral'
    mh = macd_hist(close, fast=int(params.get('macd_fast', 12)), slow=int(params.get('macd_slow', 26)), signal=int(params.get('macd_signal', 9)))
    mh_latest = mh.iloc[-1]
    if mh_latest > 0:
        s3 = 'bullish'
    elif mh_latest < 0:
        s3 = 'bearish'

    signals = [s1, s2, s3]
    bullish_count = signals.count('bullish')
    bearish_count = signals.count('bearish')
    if bullish_count >= 2:
        return 'bullish'
    if bearish_count >= 2:
        return 'bearish'
    return 'neutral'


def regime_model(df: pd.DataFrame, params: Dict[str, Any]) -> str:
    close = df['close']
    min_len = int(params.get('regime_min_len', 60))
    if len(close) < min_len:
        return 'neutral'

    # Trend: slope of long SMA (configurable)
    long_w = int(params.get('regime_long_w', 200)) if len(close) >= int(params.get('regime_long_w', 200)) else max(10, int(len(close) * 0.8))
    sma_long = sma(close, long_w)
    if len(sma_long) < 10:
        return 'neutral'
    lookback = int(params.get('regime_lookback', 20))
    lookback = min(lookback, len(sma_long) - 1)
    slope = sma_long.iloc[-1] - sma_long.iloc[-1 - lookback]

    # Volatility: recent rolling std
    vol_rolling = int(params.get('vol_rolling', 60))
    vol = close.pct_change().rolling(vol_rolling, min_periods=10).std().iloc[-1]
    hist_vol = close.pct_change().rolling(vol_rolling, min_periods=10).std().dropna()
    vol_med = hist_vol.median() if not hist_vol.empty else vol

    if slope > 0 and vol <= vol_med:
        return 'bullish'
    if slope < 0 and vol >= vol_med:
        return 'bearish'
    return 'neutral'


@dataclass
class SectorSentiment:
    sector: str
    three_signal: str
    regime_model: str
    final_sentiment: str


def final_from_models(a: str, b: str) -> str:
    if a == 'bullish' and b == 'bullish':
        return 'bullish'
    if a == 'bearish' and b == 'bearish':
        return 'bearish'
    return 'neutral'


def analyze(sector_df: pd.DataFrame, params: Dict[str, Any]) -> SectorSentiment:
    ts = three_signal_confirmation(sector_df, params)
    rm = regime_model(sector_df, params)
    final = final_from_models(ts, rm)
    return SectorSentiment(sector=sector_df['sector'].iloc[0], three_signal=ts, regime_model=rm, final_sentiment=final)


def generate_sample_data(days: int = 360) -> pd.DataFrame:
    rng = pd.date_range(end=pd.Timestamp.today(), periods=days, freq='D')
    sectors = ['Technology', 'Energy', 'Financials']
    rows = []
    np.random.seed(42)
    for sector in sectors:
        price = 100.0 + np.cumsum(np.random.normal(loc=0.02 if sector == 'Technology' else -0.005, scale=1.0, size=days))
        for d, p in zip(rng, price):
            rows.append({'date': d, 'sector': sector, 'close': float(p)})
    df = pd.DataFrame(rows)
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', help='CSV file with columns date,sector,close', default=None)
    parser.add_argument('--output', help='Output JSON file', default='sentiment_output.json')
    # Three-signal params
    parser.add_argument('--sma-short', type=int, default=50)
    parser.add_argument('--sma-long', type=int, default=200)
    parser.add_argument('--rsi-window', type=int, default=14)
    parser.add_argument('--rsi-bull', type=float, default=60.0)
    parser.add_argument('--rsi-bear', type=float, default=40.0)
    parser.add_argument('--macd-fast', type=int, default=12)
    parser.add_argument('--macd-slow', type=int, default=26)
    parser.add_argument('--macd-signal', type=int, default=9)
    # Regime model params
    parser.add_argument('--regime-min-len', type=int, default=60)
    parser.add_argument('--regime-long-w', type=int, default=200)
    parser.add_argument('--regime-lookback', type=int, default=20)
    parser.add_argument('--vol-rolling', type=int, default=60)
    parser.add_argument('--debug', action='store_true', help='Include signal components in output')
    args = parser.parse_args()

    if args.input:
        df = pd.read_csv(args.input, parse_dates=['date'])
    else:
        df = generate_sample_data()

    results: List[Dict] = []
    params = {
        'sma_short': args.sma_short,
        'sma_long': args.sma_long,
        'rsi_window': args.rsi_window,
        'rsi_bull': args.rsi_bull,
        'rsi_bear': args.rsi_bear,
        'macd_fast': args.macd_fast,
        'macd_slow': args.macd_slow,
        'macd_signal': args.macd_signal,
        'regime_min_len': args.regime_min_len,
        'regime_long_w': args.regime_long_w,
        'regime_lookback': args.regime_lookback,
        'vol_rolling': args.vol_rolling,
    }

    for sector, g in df.groupby('sector'):
        g_sorted = g.sort_values('date').reset_index(drop=True)
        sentiment = analyze(g_sorted, params)
        results.append({
            'sector': sentiment.sector,
            'three_signal': sentiment.three_signal,
            'regime_model': sentiment.regime_model,
            'final_sentiment': sentiment.final_sentiment,
        })

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
