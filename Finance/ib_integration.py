"""Interactive Brokers integration for building sector price series.

Connects to TWS/IB Gateway, reads positions, uses yfinance to map tickers
to sectors and fetch historical close prices, then calls `sentiment.analyze`
to compute per-sector sentiment.

Prerequisites:
- TWS or IB Gateway running with API enabled (paper account on port 7497 by default)
- Install dependencies: `pip install -r requirements.txt`
"""
from __future__ import annotations
import argparse
import json
from typing import List, Dict

import pandas as pd

from ib_insync import IB, Stock

import yfinance as yf

from sentiment import analyze


def fetch_positions_symbols(ib: IB) -> List[str]:
    pos = ib.positions()
    symbols = []
    for p in pos:
        sym = None
        try:
            # p.contract may be a Stock contract
            sym = p.contract.symbol
        except Exception:
            continue
        if sym and p.position != 0:
            symbols.append(sym)
    return list(sorted(set(symbols)))


def load_positions_from_csv(path: str) -> List[str]:
    df = pd.read_csv(path)
    if 'symbol' not in df.columns:
        raise ValueError("CSV must contain a 'symbol' column")
    if 'position' in df.columns:
        df = df[df['position'] != 0]
    symbols = df['symbol'].astype(str).str.strip().tolist()
    return list(sorted(set(symbols)))


def build_sector_price_df(symbols: List[str], hist_days: int = 360) -> pd.DataFrame:
    rows = []
    for sym in symbols:
        try:
            t = yf.Ticker(sym)
            info = t.info
            sector = info.get('sector') or 'Unknown'
            hist = t.history(period=f'{hist_days}d')
            if hist.empty:
                continue
            for idx, row in hist.iterrows():
                rows.append({'date': idx, 'sector': sector, 'close': float(row['Close'])})
        except Exception:
            continue
    if not rows:
        return pd.DataFrame(columns=['date', 'sector', 'close'])
    df = pd.DataFrame(rows)
    return df


def connect_ib(ib: IB, host: str, port: int, client_id: int) -> bool:
    try:
        ib.connect(host, port, clientId=client_id)
        return True
    except Exception as exc:
        print('IB connection failed:', exc)
        return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=7497, help='Paper trading default port is 7497')
    parser.add_argument('--client-id', type=int, default=1)
    parser.add_argument('--hist-days', type=int, default=360)
    parser.add_argument('--output', default='Finance/ib_sentiment.json')
    parser.add_argument('--positions-csv', help='CSV file with symbol[,position] to use as fallback or instead of live IB positions')
    args = parser.parse_args()

    symbols: List[str] = []
    ib = IB()
    connected = False
    if args.positions_csv:
        try:
            symbols = load_positions_from_csv(args.positions_csv)
        except Exception as exc:
            print('Failed to load positions CSV:', exc)
            return
        print('Loaded symbols from CSV:', symbols)
    else:
        print(f'Connecting to IB at {args.host}:{args.port}...')
        connected = connect_ib(ib, args.host, args.port, args.client_id)
        if not connected:
            print('Could not connect to IB. Use --positions-csv to provide symbols from a file.')
            return

        symbols = fetch_positions_symbols(ib)
        if not symbols:
            print('No positions found in account. If the API is read-only, enable account data access in TWS/IB Gateway.')
            ib.disconnect()
            return
        print('Symbols from account:', symbols)

    df = build_sector_price_df(symbols, hist_days=args.hist_days)
    if df.empty:
        print('No historical data fetched for symbols.')
        ib.disconnect()
        return

    results = []
    for sector, g in df.groupby('sector'):
        g_sorted = g.sort_values('date').reset_index(drop=True)
        sentiment = analyze(g_sorted, {})
        results.append({
            'sector': sentiment.sector,
            'three_signal': sentiment.three_signal,
            'regime_model': sentiment.regime_model,
            'final_sentiment': sentiment.final_sentiment,
        })

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print('Wrote', args.output)
    if connected and ib.isConnected():
        ib.disconnect()


if __name__ == '__main__':
    main()
