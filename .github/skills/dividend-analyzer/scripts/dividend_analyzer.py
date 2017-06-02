"""Dividend Analyzer - Analyze dividend metrics, yield, coverage, sustainability."""
from __future__ import annotations
import argparse
import json
import sys
from typing import Dict, List, Any

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


def fetch_dividend_data(ticker: str, debug: bool = False) -> Dict[str, Any]:
    """Fetch dividend data from yfinance."""
    if not HAS_YFINANCE:
        return {}
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Dividend metrics
        dividend_rate = info.get('dividendRate', 0)
        dividend_yield = info.get('dividendYield', 0)
        payout_ratio = info.get('payoutRatio', 0)
        trailing_eps = info.get('trailingEps', 0)
        operating_cashflow = info.get('operatingCashflow', 0)
        free_cashflow = info.get('freeCashflow', 0)
        
        # Calculate coverage
        dividend_total = dividend_rate if dividend_rate else 0
        earnings_coverage = (trailing_eps / dividend_rate * 100) if dividend_rate and trailing_eps else 0
        fcf_coverage = (free_cashflow / (dividend_total * info.get('sharesOutstanding', 1))) if dividend_rate and free_cashflow else 0
        
        # Safety assessment
        safety_score = 70
        if payout_ratio and payout_ratio > 0.9:
            safety_score = 20
        elif payout_ratio and payout_ratio > 0.7:
            safety_score = 50
        elif payout_ratio and payout_ratio < 0.5:
            safety_score = 90
        
        traps = []
        if payout_ratio and payout_ratio > 0.9:
            traps.append('UNSUSTAINABLE_PAYOUT')
        if dividend_yield and dividend_yield > 0.08:
            traps.append('SUSPICIOUSLY_HIGH_YIELD')
        
        if debug:
            print(f"[DEBUG] Fetched dividend data for {ticker}")
        
        return {
            'ticker': ticker,
            'dividend_rate': dividend_rate,
            'dividend_yield': dividend_yield,
            'payout_ratio': payout_ratio,
            'trailing_eps': trailing_eps,
            'earnings_coverage': earnings_coverage,
            'fcf_coverage': fcf_coverage,
            'safety_score': safety_score,
            'dividend_traps': traps,
            'sector': info.get('sector', 'Unknown')
        }
    
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error fetching {ticker}: {e}")
        return {}


def analyze_dividend(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze dividend quality and safety."""
    safety = data.get('safety_score', 50)
    
    if safety >= 80:
        status = "VERY SAFE"
    elif safety >= 60:
        status = "SAFE"
    elif safety >= 40:
        status = "CAUTION"
    else:
        status = "RISKY"
    
    return {
        'ticker': data['ticker'],
        'yield': round(data['dividend_yield'] * 100, 2) if data['dividend_yield'] else 0,
        'payout_ratio': round(data['payout_ratio'] * 100, 1) if data['payout_ratio'] else 0,
        'earnings_coverage': round(data['earnings_coverage'], 2),
        'fcf_coverage': round(data['fcf_coverage'], 2),
        'safety_score': safety,
        'safety_status': status,
        'dividend_traps': data['dividend_traps']
    }


def format_dividend_table(analyses: List[Dict[str, Any]]) -> str:
    """Format dividend analysis as table."""
    lines = []
    lines.append("┌───────────────────────────────────────────────────────┐")
    lines.append("│ Ticker │ Yield │ Payout │ Coverage │ Score │ Status  │")
    lines.append("├───────────────────────────────────────────────────────┤")
    
    for analysis in analyses:
        ticker = analysis['ticker'].ljust(6)
        yield_str = f"{analysis['yield']:.2f}%".rjust(6)
        payout = f"{analysis['payout_ratio']:.0f}%".rjust(7)
        coverage = f"{analysis['earnings_coverage']:.1f}x".rjust(8)
        score = str(analysis['safety_score']).rjust(5)
        status = analysis['safety_status'].ljust(7)
        
        line = f"│ {ticker} │ {yield_str} │ {payout} │ {coverage} │ {score} │ {status} │"
        lines.append(line)
    
    lines.append("└───────────────────────────────────────────────────────┘")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze dividend metrics.')
    parser.add_argument('--tickers', help='Comma-separated tickers')
    parser.add_argument('--portfolio', help='Portfolio CSV file')
    parser.add_argument('--watchlist', help='Watchlist JSON file')
    parser.add_argument('--min-yield', type=float, help='Minimum dividend yield')
    parser.add_argument('--max-yield', type=float, help='Maximum dividend yield')
    parser.add_argument('--min-coverage', type=float, help='Minimum dividend coverage')
    parser.add_argument('--detect-traps', action='store_true', help='Detect dividend traps')
    parser.add_argument('--report', default='summary', choices=['summary', 'safety', 'growth', 'traps'])
    parser.add_argument('--format', default='json', choices=['json', 'csv', 'table'])
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    # Parse tickers
    tickers = []
    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(',')]
    
    if not tickers:
        parser.print_help()
        sys.exit(1)
    
    # Fetch and analyze
    analyses = []
    for ticker in tickers:
        data = fetch_dividend_data(ticker, args.debug)
        if data:
            analysis = analyze_dividend(data)
            
            # Apply filters
            if args.min_yield and analysis['yield'] < args.min_yield * 100:
                continue
            if args.max_yield and analysis['yield'] > args.max_yield * 100:
                continue
            if args.min_coverage and analysis['earnings_coverage'] < args.min_coverage:
                continue
            if args.detect_traps and not analysis['dividend_traps']:
                continue
            
            analyses.append(analysis)
    
    if not analyses:
        print("No results", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'table':
        output_str = format_dividend_table(analyses)
    else:
        output_str = json.dumps(analyses, indent=2)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_str)
    
    print(output_str)


if __name__ == '__main__':
    main()
