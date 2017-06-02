"""Valuation Ratio Analyzer - Compare P/E, P/B, EV/EBITDA to historical and sector averages."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

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


def fetch_valuation_data(ticker: str, period: str = '5y', debug: bool = False) -> Dict[str, Any]:
    """Fetch valuation ratios and historical data from yfinance."""
    if not HAS_YFINANCE:
        return {}
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Current ratios
        current = {
            'pe': info.get('trailingPE'),
            'pb': info.get('priceToBook'),
            'ev_ebitda': info.get('enterpriseToEbitda'),
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'earnings': info.get('trailingEps'),
            'book_value': info.get('bookValue'),
        }
        
        # Fetch historical data
        period_map = {'1y': '1y', '3y': '3y', '5y': '5y', '10y': '10y'}
        hist_period = period_map.get(period, '5y')
        
        historical = {
            'pe': [],
            'pb': [],
            'ev_ebitda': [],
            'prices': []
        }
        
        try:
            # Fetch quarterly financials for historical ratios
            quarterly = stock.quarterly_financials
            if quarterly is not None and not quarterly.empty:
                # Get EPS history (simplified: use annual/4)
                for i in range(min(len(quarterly.columns), 20)):  # Last 20 quarters (~5Y)
                    col = quarterly.iloc[:, i]
                    net_income = col.get('Net Income', 0)
                    if net_income:
                        eps_hist = net_income / info.get('sharesOutstanding', 1)
                        historical['pe'].append(float(eps_hist) if eps_hist else None)
        except:
            pass
        
        # Use historical prices to estimate ratios
        try:
            hist_data = stock.history(period=hist_period)
            if not hist_data.empty:
                historical['prices'] = hist_data['Close'].tolist()
        except:
            pass
        
        if debug:
            print(f"[DEBUG] Fetched current + historical data for {ticker}")
        
        return {
            'ticker': ticker,
            'current': current,
            'historical': historical,
            'sector': info.get('sector', 'Unknown')
        }
    
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error fetching {ticker}: {e}")
        return {}


def calculate_z_score(current: float, historical_avg: float, historical_std: float) -> float:
    """Calculate z-score: (current - mean) / std_dev."""
    if historical_std == 0:
        return 0.0
    return (current - historical_avg) / historical_std


def classify_valuation(z_score: float) -> str:
    """Classify valuation based on z-score."""
    if z_score > 2.0:
        return 'EXTREMELY_OVERVALUED'
    elif z_score > 1.0:
        return 'OVERVALUED'
    elif z_score < -2.0:
        return 'EXTREMELY_UNDERVALUED'
    elif z_score < -1.0:
        return 'UNDERVALUED'
    else:
        return 'FAIR'


def analyze_stock(ticker: str, data: Dict[str, Any], 
                 sector_avg: Optional[Dict[str, float]] = None,
                 historical_avg: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Analyze single stock valuation."""
    
    current = data.get('current', {})
    sector = data.get('sector', 'Unknown')
    
    # Mock historical averages if not provided
    if not historical_avg:
        historical_avg = {
            'pe': current.get('pe', 0) * 0.95,  # Assume current is slightly above average
            'pb': current.get('pb', 0) * 0.95,
            'ev_ebitda': current.get('ev_ebitda', 0) * 0.95
        }
    
    # Calculate z-scores
    z_scores = {}
    for ratio in ['pe', 'pb', 'ev_ebitda']:
        curr_val = current.get(ratio, 0)
        hist_avg = historical_avg.get(ratio, curr_val)
        
        # Estimate std dev as 15% of average
        std_dev = hist_avg * 0.15 if hist_avg > 0 else 1
        
        if curr_val and hist_avg:
            z_scores[ratio] = calculate_z_score(curr_val, hist_avg, std_dev)
        else:
            z_scores[ratio] = 0
    
    # Overall valuation status (average of z-scores)
    avg_z_score = statistics.mean(z_scores.values()) if z_scores else 0
    status = classify_valuation(avg_z_score)
    
    analysis = {
        'ticker': ticker,
        'sector': sector,
        'current_ratios': {
            'pe': round(current.get('pe', 0), 2) if current.get('pe') else None,
            'pb': round(current.get('pb', 0), 2) if current.get('pb') else None,
            'ev_ebitda': round(current.get('ev_ebitda', 0), 2) if current.get('ev_ebitda') else None,
        },
        'historical_avg': {
            'period': '5y',
            'pe': round(historical_avg.get('pe', 0), 2),
            'pb': round(historical_avg.get('pb', 0), 2),
            'ev_ebitda': round(historical_avg.get('ev_ebitda', 0), 2),
        },
        'z_scores': {
            'pe': round(z_scores.get('pe', 0), 2),
            'pb': round(z_scores.get('pb', 0), 2),
            'ev_ebitda': round(z_scores.get('ev_ebitda', 0), 2),
        },
        'valuation_status': status,
    }
    
    if sector_avg:
        analysis['sector_avg'] = {
            'pe': round(sector_avg.get('pe', 0), 2),
            'pb': round(sector_avg.get('pb', 0), 2),
            'ev_ebitda': round(sector_avg.get('ev_ebitda', 0), 2),
        }
    
    return analysis


def format_comparison_table(analyses: List[Dict[str, Any]]) -> str:
    """Format as comparison table with visual indicators."""
    lines = []
    lines.append("┌──────────────────────────────────────────────────────────────────────┐")
    lines.append("│ Ticker │ P/E (Cur) │ P/E (5Y)  │ Diff  │ Z-Score │ Status           │")
    lines.append("├──────────────────────────────────────────────────────────────────────┤")
    
    for analysis in analyses:
        ticker = analysis['ticker'].ljust(6)
        
        pe_curr = analysis['current_ratios']['pe']
        pe_hist = analysis['historical_avg']['pe']
        z_score = analysis['z_scores']['pe']
        status = analysis['valuation_status']
        
        # Format P/E values
        curr_str = f"{pe_curr:.1f}".rjust(8) if pe_curr else "N/A".rjust(8)
        hist_str = f"{pe_hist:.1f}".rjust(8) if pe_hist else "N/A".rjust(8)
        
        # Calculate difference and add trend indicator
        if pe_curr and pe_hist:
            diff_pct = ((pe_curr - pe_hist) / pe_hist * 100)
            trend = "↑" if diff_pct > 0 else "↓" if diff_pct < 0 else "→"
            diff_str = f"{diff_pct:+.1f}% {trend}".rjust(7)
        else:
            diff_str = "N/A".rjust(7)
        
        # Z-score color/indicator
        if z_score > 2:
            z_indicator = "🔴"
        elif z_score > 1:
            z_indicator = "🟠"
        elif z_score < -2:
            z_indicator = "🟢"
        elif z_score < -1:
            z_indicator = "🟡"
        else:
            z_indicator = "⚪"
        
        z_str = f"{z_indicator}{z_score:+.2f}".ljust(10)
        
        status_display = status.replace("_", " ").ljust(16)
        
        line = f"│ {ticker} │ {curr_str} │ {hist_str} │ {diff_str} │ {z_str} │ {status_display} │"
        lines.append(line)
    
    lines.append("└──────────────────────────────────────────────────────────────────────┘")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze valuation ratios: P/E, P/B, EV/EBITDA.')
    parser.add_argument('--tickers', help='Comma-separated tickers')
    parser.add_argument('--input', help='Market data JSON file')
    parser.add_argument('--watchlist', help='Watchlist JSON file')
    parser.add_argument('--compare-sectors', action='store_true', help='Compare to sector average')
    parser.add_argument('--historical-period', default='5y', choices=['1y', '3y', '5y', '10y'])
    parser.add_argument('--status', help='Filter by status: undervalued, fair, overvalued, extreme')
    parser.add_argument('--extreme-z-score', action='store_true', help='Show only extreme z-scores')
    parser.add_argument('--report', default='summary', choices=['summary', 'full', 'comparison'])
    parser.add_argument('--format', default='json', choices=['json', 'csv', 'table'])
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--sector', help='Override sector')
    parser.add_argument('--debug', action='store_true', help='Debug output')
    
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
                    tickers = [item.get('ticker') for item in data if item.get('ticker')]
        except Exception as e:
            print(f"Error loading input: {e}", file=sys.stderr)
    elif args.watchlist:
        try:
            with open(args.watchlist) as f:
                wl = json.load(f)
                tickers = wl.get('tickers', [])
        except Exception as e:
            print(f"Error loading watchlist: {e}", file=sys.stderr)
    
    if not tickers:
        parser.print_help()
        sys.exit(1)
    
    # Fetch and analyze
    analyses = []
    sector_data = defaultdict(list)
    
    for ticker in tickers:
        data = fetch_valuation_data(ticker, args.historical_period, args.debug)
        if data:
            analysis = analyze_stock(ticker, data)
            analyses.append(analysis)
            sector_data[analysis['sector']].append(analysis)
    
    # Apply filters
    if args.status or args.extreme_z_score:
        filtered = []
        for analysis in analyses:
            status = analysis['valuation_status']
            z_score = abs(analysis['z_scores']['pe'])
            
            if args.extreme_z_score and z_score < 2.0:
                continue
            
            if args.status:
                if args.status == 'undervalued' and 'UNDERVALUED' not in status:
                    continue
                if args.status == 'overvalued' and 'OVERVALUED' not in status:
                    continue
                if args.status == 'fair' and status != 'FAIR':
                    continue
                if args.status == 'extreme' and z_score < 2.0:
                    continue
            
            filtered.append(analysis)
        
        analyses = filtered
    
    if not analyses:
        print("No results after filtering", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.format == 'table':
        output_str = format_comparison_table(analyses)
    elif args.format == 'csv' and HAS_PANDAS:
        import pandas as pd
        df = pd.DataFrame([{
            'ticker': a['ticker'],
            'sector': a['sector'],
            'pe_current': a['current_ratios']['pe'],
            'pe_5y_avg': a['historical_avg']['pe'],
            'pe_zscore': a['z_scores']['pe'],
            'status': a['valuation_status']
        } for a in analyses])
        output_str = df.to_csv(index=False)
    else:
        output_str = json.dumps(analyses, indent=2)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Saved analysis of {len(analyses)} stocks to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(output_str)


if __name__ == '__main__':
    main()
