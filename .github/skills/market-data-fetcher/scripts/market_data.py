"""
Live Market Data Fetcher for NASDAQ/NYSE

Fetches current price (CMP), 52-week high/low, market cap, and face value for stocks.
Primary: yfinance | Fallback: Interactive Brokers API

Usage:
    py -3 market_data.py --tickers AAPL,MSFT,TSLA
    py -3 market_data.py --csv positions.csv --output my_output.json
    py -3 market_data.py --tickers AAPL,MSFT --ib-host 127.0.0.1 --ib-port 7497
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

import pandas as pd

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    from ib_insync import IB, Stock
    HAS_IB = True
except ImportError:
    HAS_IB = False


@dataclass
class MarketData:
    ticker: str
    currency: str
    current_price: float
    price_52w_high: float
    price_52w_low: float
    market_cap: Optional[int]
    market_cap_category: str
    face_value: float
    currency_symbol: str
    source: str  # 'yfinance' or 'ib_api'


def categorize_market_cap(market_cap: Optional[float]) -> str:
    """Categorize market cap in billions."""
    if market_cap is None:
        return 'unknown'
    
    # Market cap in billions
    cap_b = market_cap / 1e9
    
    if cap_b < 0.3:
        return 'nano'
    elif cap_b < 2:
        return 'micro'
    elif cap_b < 10:
        return 'small'
    elif cap_b < 100:
        return 'mid'
    elif cap_b < 200:
        return 'large'
    else:
        return 'mega'


def fetch_from_yfinance(tickers: List[str], debug: bool = False) -> List[MarketData]:
    """Fetch market data from yfinance."""
    if not HAS_YFINANCE:
        if debug:
            print('[DEBUG] yfinance not installed')
        return []
    
    results = []
    for ticker in tickers:
        try:
            if debug:
                print(f'[DEBUG] Fetching {ticker} from yfinance...')
            
            stock = yf.Ticker(ticker)
            
            # Get historical data for 52-week high/low
            hist = stock.history(period='1y')
            if hist.empty:
                if debug:
                    print(f'[DEBUG] No historical data for {ticker}')
                continue
            
            # Get current info
            info = stock.info
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            price_52w_high = hist['High'].max() if 'High' in hist else None
            price_52w_low = hist['Low'].min() if 'Low' in hist else None
            market_cap = info.get('marketCap')
            currency = info.get('currency', 'USD')
            face_value = info.get('parValue', 0.0) or 0.0
            
            # Currency symbol mapping
            currency_symbols = {
                'USD': '$', 'EUR': '€', 'GBP': '£', 
                'JPY': '¥', 'INR': '₹', 'CAD': 'C$'
            }
            currency_symbol = currency_symbols.get(currency, currency)
            
            if current_price is None:
                current_price = hist['Close'].iloc[-1]
            
            if price_52w_high is None or price_52w_low is None:
                if debug:
                    print(f'[DEBUG] Incomplete price data for {ticker}')
                continue
            
            data = MarketData(
                ticker=ticker,
                currency=currency,
                current_price=float(current_price),
                price_52w_high=float(price_52w_high),
                price_52w_low=float(price_52w_low),
                market_cap=int(market_cap) if market_cap else None,
                market_cap_category=categorize_market_cap(market_cap),
                face_value=float(face_value),
                currency_symbol=currency_symbol,
                source='yfinance'
            )
            results.append(data)
            
        except Exception as e:
            if debug:
                print(f'[DEBUG] Error fetching {ticker} from yfinance: {e}')
            continue
    
    return results


def fetch_from_ib_api(tickers: List[str], host: str = '127.0.0.1', 
                      port: int = 7497, client_id: int = 1, debug: bool = False) -> List[MarketData]:
    """Fetch market data from Interactive Brokers API."""
    if not HAS_IB:
        if debug:
            print('[DEBUG] ib_insync not installed')
        return []
    
    ib = IB()
    try:
        if debug:
            print(f'[DEBUG] Connecting to IB at {host}:{port}...')
        ib.connect(host, port, clientId=client_id)
    except Exception as e:
        if debug:
            print(f'[DEBUG] IB connection failed: {e}')
        return []
    
    results = []
    try:
        for ticker in tickers:
            try:
                if debug:
                    print(f'[DEBUG] Fetching {ticker} from IB API...')
                
                contract = Stock(ticker, 'SMART', 'USD')
                ib.qualifyContracts(contract)
                
                # Request market data
                ticker_data = ib.reqMktData(contract, '', False, False)
                ib.sleep(0.1)  # Wait for data
                
                if ticker_data is None:
                    if debug:
                        print(f'[DEBUG] No data returned for {ticker}')
                    continue
                
                # Extract data
                current_price = ticker_data.last or ticker_data.close
                market_cap = None  # IB API doesn't directly provide market cap
                
                data = MarketData(
                    ticker=ticker,
                    currency='USD',
                    current_price=float(current_price) if current_price else 0.0,
                    price_52w_high=ticker_data.high52week or 0.0,
                    price_52w_low=ticker_data.low52week or 0.0,
                    market_cap=market_cap,
                    market_cap_category=categorize_market_cap(market_cap),
                    face_value=0.0,
                    currency_symbol='$',
                    source='ib_api'
                )
                results.append(data)
                
                ib.cancelMktData(contract)
                
            except Exception as e:
                if debug:
                    print(f'[DEBUG] Error fetching {ticker} from IB: {e}')
                continue
    finally:
        ib.disconnect()
    
    return results


def parse_tickers_from_cli(ticker_str: str) -> List[str]:
    """Parse comma-separated ticker list."""
    return [t.strip().upper() for t in ticker_str.split(',') if t.strip()]


def parse_tickers_from_csv(csv_path: str) -> List[str]:
    """Parse tickers from CSV file (requires 'symbol' column)."""
    try:
        df = pd.read_csv(csv_path)
        if 'symbol' not in df.columns:
            raise ValueError("CSV must contain a 'symbol' column")
        return df['symbol'].astype(str).str.strip().str.upper().tolist()
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        return []


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Fetch live market data: CMP, 52W high/low, market cap, face value'
    )
    parser.add_argument('--tickers', help='Comma-separated tickers (e.g., AAPL,MSFT,TSLA)', default=None)
    parser.add_argument('--csv', help='CSV file with symbol column', default=None)
    parser.add_argument('--output', help='Output JSON file', default='Finance/market_data_output.json')
    parser.add_argument('--ib-host', default='127.0.0.1', help='IB Gateway host')
    parser.add_argument('--ib-port', type=int, default=7497, help='IB Gateway port')
    parser.add_argument('--client-id', type=int, default=1, help='IB client ID')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = []
    if args.tickers:
        tickers = parse_tickers_from_cli(args.tickers)
    elif args.csv:
        tickers = parse_tickers_from_csv(args.csv)
    else:
        parser.print_help()
        print("\nError: Provide --tickers or --csv", file=sys.stderr)
        sys.exit(1)
    
    if not tickers:
        print("No valid tickers provided", file=sys.stderr)
        sys.exit(1)
    
    if args.debug:
        print(f'[DEBUG] Tickers to fetch: {tickers}')
    
    # Fetch data: try yfinance first, then IB fallback
    results = fetch_from_yfinance(tickers, debug=args.debug)
    
    # If some tickers failed with yfinance, try IB for those
    fetched_tickers = {r.ticker for r in results}
    missing_tickers = [t for t in tickers if t not in fetched_tickers]
    
    if missing_tickers and HAS_IB:
        if args.debug:
            print(f'[DEBUG] Trying IB API for missing tickers: {missing_tickers}')
        ib_results = fetch_from_ib_api(
            missing_tickers, 
            host=args.ib_host, 
            port=args.ib_port, 
            client_id=args.client_id,
            debug=args.debug
        )
        results.extend(ib_results)
    
    if not results:
        print("No market data retrieved", file=sys.stderr)
        sys.exit(1)
    
    # Prepare output
    output_data = [
        {
            'ticker': r.ticker,
            'currency': r.currency,
            'current_price': r.current_price,
            '52w_high': r.price_52w_high,
            '52w_low': r.price_52w_low,
            'market_cap': r.market_cap,
            'market_cap_category': r.market_cap_category,
            'face_value': r.face_value,
            'currency_symbol': r.currency_symbol,
            'source': r.source,
        }
        for r in results
    ]
    
    # Write output
    try:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Saved {len(output_data)} records to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print to stdout
    print(json.dumps(output_data, indent=2))


if __name__ == '__main__':
    main()
