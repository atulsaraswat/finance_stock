"""Growth Valuation Metrics - PEG ratio, FCF yield, revenue multiples."""
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


def fetch_growth_valuation_data(ticker: str, growth_rate: float = None, debug: bool = False) -> Dict[str, Any]:
    """Fetch growth valuation metrics from yfinance."""
    if not HAS_YFINANCE:
        return {}
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Valuation metrics
        market_cap = info.get('marketCap', 0)
        pe_ratio = info.get('trailingPE', 0)
        revenue = info.get('totalRevenue', 0)
        operating_cashflow = info.get('operatingCashflow', 0)
        free_cashflow = info.get('freeCashflow', 0)
        
        # Growth rate (use provided or estimate)
        if growth_rate is None:
            growth_rate = info.get('earningsGrowth', 0.10)  # Default 10% if not available
        
        # Calculate PEG
        peg_ratio = (pe_ratio / (growth_rate * 100)) if growth_rate and pe_ratio else 0
        
        # Calculate yields
        fcf_yield = (free_cashflow / market_cap * 100) if market_cap else 0
        revenue_multiple = (market_cap / revenue) if revenue else 0
        
        # Assessment
        if peg_ratio < 0.8:
            peg_status = "UNDERVALUED"
        elif peg_ratio < 1.2:
            peg_status = "FAIR"
        else:
            peg_status = "OVERVALUED"
        
        if debug:
            print(f"[DEBUG] Fetched growth valuation data for {ticker}")
        
        return {
            'ticker': ticker,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'revenue': revenue,
            'operating_cashflow': operating_cashflow,
            'free_cashflow': free_cashflow,
            'growth_rate': growth_rate,
            'peg_ratio': peg_ratio,
            'peg_status': peg_status,
            'fcf_yield': fcf_yield,
            'revenue_multiple': revenue_multiple,
            'sector': info.get('sector', 'Unknown')
        }
    
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error fetching {ticker}: {e}")
        return {}


def analyze_growth_valuation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze growth-adjusted valuation."""
    return {
        'ticker': data['ticker'],
        'pe_ratio': round(data['pe_ratio'], 2),
        'growth_rate': f"{data['growth_rate']*100:.1f}%",
        'peg_ratio': round(data['peg_ratio'], 2),
        'peg_status': data['peg_status'],
        'fcf_yield': round(data['fcf_yield'], 2),
        'revenue_multiple': round(data['revenue_multiple'], 2),
        'sector': data['sector']
    }


def format_growth_valuation_table(analyses: List[Dict[str, Any]]) -> str:
    """Format growth valuation analysis as table."""
    lines = []
    lines.append("┌────────────────────────────────────────────────────────────┐")
    lines.append("│ Ticker │ P/E  │ Growth │ PEG  │ Status      │ FCF Yield │")
    lines.append("├────────────────────────────────────────────────────────────┤")
    
    for analysis in analyses:
        ticker = analysis['ticker'].ljust(6)
        pe = str(analysis['pe_ratio']).rjust(5)
        growth = analysis['growth_rate'].rjust(7)
        peg = str(analysis['peg_ratio']).rjust(5)
        status = analysis['peg_status'].ljust(11)
        fcf = f"{analysis['fcf_yield']:.2f}%".rjust(9)
        
        line = f"│ {ticker} │ {pe} │ {growth} │ {peg} │ {status} │ {fcf} │"
        lines.append(line)
    
    lines.append("└────────────────────────────────────────────────────────────┘")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze growth-adjusted valuations.')
    parser.add_argument('--tickers', help='Comma-separated tickers')
    parser.add_argument('--input', help='Market data JSON file')
    parser.add_argument('--watchlist', help='Watchlist JSON file')
    parser.add_argument('--metric', default='peg', choices=['peg', 'fcf-yield', 'price-sales', 'all'])
    parser.add_argument('--growth-rates', help='Growth rates: ticker:rate AAPL:8 MSFT:10')
    parser.add_argument('--target-peg', type=float, help='Target PEG ratio')
    parser.add_argument('--max-peg', type=float, help='Maximum PEG')
    parser.add_argument('--min-fcf-yield', type=float, help='Minimum FCF yield')
    parser.add_argument('--report', default='summary', choices=['summary', 'comparison', 'growth-quality'])
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
    
    # Parse growth rates
    growth_rates = {}
    if args.growth_rates:
        for item in args.growth_rates.split():
            parts = item.split(':')
            if len(parts) == 2:
                growth_rates[parts[0]] = float(parts[1]) / 100
    
    # Fetch and analyze
    analyses = []
    for ticker in tickers:
        growth_rate = growth_rates.get(ticker)
        data = fetch_growth_valuation_data(ticker, growth_rate, args.debug)
        if data:
            analysis = analyze_growth_valuation(data)
            
            # Apply filters
            if args.max_peg and analysis['peg_ratio'] > args.max_peg:
                continue
            if args.min_fcf_yield and analysis['fcf_yield'] < args.min_fcf_yield:
                continue
            
            analyses.append(analysis)
    
    if not analyses:
        print("No results", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'table':
        output_str = format_growth_valuation_table(analyses)
    else:
        output_str = json.dumps(analyses, indent=2)
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_str)
    
    print(output_str)


if __name__ == '__main__':
    main()
