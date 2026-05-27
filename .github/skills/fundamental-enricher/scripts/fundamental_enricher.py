"""Fundamental Enricher - Add fundamental metrics to market data."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


def fetch_fundamentals(ticker: str) -> Dict[str, Any]:
    """Fetch fundamental data for a ticker."""
    if not HAS_YFINANCE:
        return {}
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'pe_ratio': info.get('trailingPE'),
            'eps': info.get('trailingEps'),
            'earnings_growth_1yr': info.get('earningsGrowth'),
            'dividend_yield': info.get('dividendYield'),
            'roe': info.get('returnOnEquity'),
            'roa': info.get('returnOnAssets'),
            'debt_to_equity': info.get('debtToEquity'),
            'profit_margin': info.get('profitMargins'),
            'peg_score': info.get('pegRatio'),
        }
    except Exception as e:
        return {}


def calculate_valuation_score(fundamentals: Dict[str, Any]) -> int:
    """Calculate composite valuation score (1-100)."""
    if not fundamentals:
        return 50
    
    score = 50
    
    # P/E score
    pe = fundamentals.get('pe_ratio')
    if pe and pe < 15:
        score += 15
    elif pe and pe < 25:
        score += 5
    elif pe:
        score -= 5
    
    # Dividend yield
    div = fundamentals.get('dividend_yield', 0)
    if div and div > 0.03:
        score += 10
    elif div and div > 0:
        score += 5
    
    # ROE
    roe = fundamentals.get('roe')
    if roe and roe > 0.20:
        score += 10
    elif roe and roe > 0.15:
        score += 5
    
    return min(100, max(1, score))


def enrich_data(market_data: List[Dict[str, Any]], 
                compare_sectors: bool = False,
                valuation_score: bool = False) -> List[Dict[str, Any]]:
    """Enrich market data with fundamentals."""
    enriched = []
    
    for item in market_data:
        ticker = item.get('ticker')
        fundamental = fetch_fundamentals(ticker)
        
        item['fundamental'] = fundamental
        
        if valuation_score:
            item['valuation_score'] = calculate_valuation_score(fundamental)
        
        enriched.append(item)
    
    return enriched


def main() -> None:
    parser = argparse.ArgumentParser(description='Enrich market data with fundamental metrics.')
    parser.add_argument('--input', required=True, help='Market data JSON file')
    parser.add_argument('--compare-sectors', action='store_true', help='Add sector comparisons')
    parser.add_argument('--valuation-score', action='store_true', help='Calculate valuation scores')
    parser.add_argument('--min-pe', type=float, help='Minimum P/E ratio')
    parser.add_argument('--max-pe', type=float, help='Maximum P/E ratio')
    parser.add_argument('--min-dividend-yield', type=float, help='Minimum dividend yield')
    parser.add_argument('--min-roe', type=float, help='Minimum ROE')
    parser.add_argument('--max-debt-to-equity', type=float, help='Maximum debt-to-equity')
    parser.add_argument('--output', default='Finance/market_data_enriched.json', help='Output file')
    parser.add_argument('--format', choices=['json', 'csv'], default='json')
    
    args = parser.parse_args()
    
    # Load market data
    try:
        with open(args.input) as f:
            market_data = json.load(f)
    except Exception as e:
        print(f"Error loading market data: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Enrich
    enriched = enrich_data(market_data, args.compare_sectors, args.valuation_score)
    
    # Apply filters
    if args.min_pe or args.max_pe or args.min_dividend_yield or args.min_roe or args.max_debt_to_equity:
        filtered = []
        for item in enriched:
            fund = item.get('fundamental', {})
            
            pe = fund.get('pe_ratio')
            if args.min_pe and pe and pe < args.min_pe:
                continue
            if args.max_pe and pe and pe > args.max_pe:
                continue
            
            div = fund.get('dividend_yield', 0)
            if args.min_dividend_yield and div < args.min_dividend_yield:
                continue
            
            roe = fund.get('roe')
            if args.min_roe and roe and roe < args.min_roe:
                continue
            
            de = fund.get('debt_to_equity')
            if args.max_debt_to_equity and de and de > args.max_debt_to_equity:
                continue
            
            filtered.append(item)
        
        enriched = filtered
    
    if not enriched:
        print("No data after filtering", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'json':
        output_str = json.dumps(enriched, indent=2)
    else:
        df = pd.DataFrame([{
            'ticker': item['ticker'],
            'current_price': item['current_price'],
            'pe_ratio': item.get('fundamental', {}).get('pe_ratio'),
            'dividend_yield': item.get('fundamental', {}).get('dividend_yield'),
            'roe': item.get('fundamental', {}).get('roe'),
            'valuation_score': item.get('valuation_score')
        } for item in enriched])
        output_str = df.to_csv(index=False)
    
    # Write output
    try:
        with open(args.output, 'w') as f:
            f.write(output_str)
        print(f"Saved {len(enriched)} enriched records to {args.output}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)
    
    print(output_str)


if __name__ == '__main__':
    main()
