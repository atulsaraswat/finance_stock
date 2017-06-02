"""Earnings Quality Analyzer - Compare net income to operating cash flow, detect red flags."""
from __future__ import annotations
import argparse
import json
import sys
from typing import Dict, List, Any, Optional

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def fetch_earnings_quality_data(ticker: str, debug: bool = False) -> Dict[str, Any]:
    """Fetch earnings quality metrics from yfinance."""
    if not HAS_YFINANCE:
        return {}
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Current metrics
        net_income = info.get('netIncome', 0)
        operating_cashflow = info.get('operatingCashflow', 0)
        free_cashflow = info.get('freeCashflow', 0)
        
        # Calculate quality metrics
        conversion_ratio = (operating_cashflow / net_income * 100) if net_income else 0
        
        # Quality score (mock calculation for demonstration)
        quality_score = 50
        if conversion_ratio > 80 and conversion_ratio < 120:
            quality_score = 85
        elif conversion_ratio > 0:
            quality_score = max(10, min(100, 50 + (100 - conversion_ratio) / 2))
        
        red_flags = []
        
        # Check for divergence
        if net_income > 0 and operating_cashflow < net_income * 0.5:
            red_flags.append({
                'flag': 'EARNINGS_VS_CASHFLOW_DIVERGENCE',
                'severity': 'CRITICAL',
                'message': f'Operating cash flow only {conversion_ratio:.0f}% of net income'
            })
        
        # Check for negative cash flow
        if operating_cashflow < 0 and net_income > 0:
            red_flags.append({
                'flag': 'NEGATIVE_OPERATING_CASHFLOW',
                'severity': 'CRITICAL',
                'message': 'Negative operating cash flow while reporting profits'
            })
        
        if debug:
            print(f"[DEBUG] Fetched earnings quality data for {ticker}")
        
        return {
            'ticker': ticker,
            'net_income': net_income,
            'operating_cashflow': operating_cashflow,
            'free_cashflow': free_cashflow,
            'conversion_ratio': conversion_ratio,
            'quality_score': quality_score,
            'red_flags': red_flags,
            'sector': info.get('sector', 'Unknown')
        }
    
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error fetching {ticker}: {e}")
        return {}


def analyze_earnings_quality(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze earnings quality."""
    conversion = data.get('conversion_ratio', 0)
    quality = data.get('quality_score', 50)
    red_flags = data.get('red_flags', [])
    
    # Assessment
    if quality >= 80:
        assessment = "EXCELLENT"
    elif quality >= 70:
        assessment = "VERY GOOD"
    elif quality >= 50:
        assessment = "FAIR"
    elif quality >= 30:
        assessment = "POOR"
    else:
        assessment = "RED FLAG"
    
    return {
        'ticker': data['ticker'],
        'net_income': round(data['net_income'] / 1e9, 1),  # Convert to billions
        'operating_cashflow': round(data['operating_cashflow'] / 1e9, 1),
        'free_cashflow': round(data['free_cashflow'] / 1e9, 1),
        'conversion_ratio': round(conversion, 1),
        'quality_score': quality,
        'assessment': assessment,
        'red_flags': red_flags
    }


def format_quality_table(analyses: List[Dict[str, Any]]) -> str:
    """Format quality analysis as table."""
    lines = []
    lines.append("┌──────────────────────────────────────────────────────────┐")
    lines.append("│ Ticker │ NI ($B) │ OCF ($B) │ Conv.  │ Score │ Status   │")
    lines.append("├──────────────────────────────────────────────────────────┤")
    
    for analysis in analyses:
        ticker = analysis['ticker'].ljust(6)
        ni = str(analysis['net_income']).rjust(7)
        ocf = str(analysis['operating_cashflow']).rjust(8)
        conv = f"{analysis['conversion_ratio']:.0f}%".rjust(7)
        score = str(analysis['quality_score']).rjust(5)
        status = analysis['assessment'].ljust(8)
        
        line = f"│ {ticker} │ {ni} │ {ocf} │ {conv} │ {score} │ {status} │"
        lines.append(line)
    
    lines.append("└──────────────────────────────────────────────────────────┘")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze earnings quality.')
    parser.add_argument('--tickers', help='Comma-separated tickers')
    parser.add_argument('--input', help='Market data JSON file')
    parser.add_argument('--watchlist', help='Watchlist JSON file')
    parser.add_argument('--detect-red-flags', action='store_true', help='Highlight red flags')
    parser.add_argument('--min-quality-score', type=int, help='Minimum quality score')
    parser.add_argument('--period', default='5y', choices=['1y', '3y', '5y'])
    parser.add_argument('--report', default='summary', choices=['summary', 'detailed', 'trend', 'red-flags'])
    parser.add_argument('--compare-sectors', action='store_true')
    parser.add_argument('--format', default='json', choices=['json', 'csv', 'table'])
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = []
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
    elif args.input:
        try:
            with open(args.input) as f:
                data = json.load(f)
                if isinstance(data, list):
                    tickers = [item.get('ticker') for item in data]
        except Exception as e:
            print(f"Error loading input: {e}", file=sys.stderr)
    
    if not tickers:
        parser.print_help()
        sys.exit(1)
    
    # Fetch and analyze
    analyses = []
    for ticker in tickers:
        data = fetch_earnings_quality_data(ticker, args.debug)
        if data:
            analysis = analyze_earnings_quality(data)
            analyses.append(analysis)
    
    # Apply filters
    if args.min_quality_score:
        analyses = [a for a in analyses if a['quality_score'] >= args.min_quality_score]
    
    if not analyses:
        print("No results", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'table':
        output_str = format_quality_table(analyses)
    else:
        output_str = json.dumps(analyses, indent=2)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_str)
    
    print(output_str)


if __name__ == '__main__':
    main()
