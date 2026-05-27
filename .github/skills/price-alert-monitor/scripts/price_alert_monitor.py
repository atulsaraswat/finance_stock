"""Price Alert Monitor - Monitor stocks and trigger alerts on price changes."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


ALERTS_DIR = Path('Finance')


def check_price_movements(market_data: List[Dict[str, Any]], 
                         previous_data: Dict[str, Dict[str, float]] = None) -> List[Dict[str, Any]]:
    """Check for significant price movements."""
    alerts = []
    previous_data = previous_data or {}
    
    for item in market_data:
        ticker = item['ticker']
        current_price = item['current_price']
        
        if ticker in previous_data:
            prev_price = previous_data[ticker].get('current_price', current_price)
            change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
            
            if abs(change_pct) > 2:  # Alert on >2% movement
                alerts.append({
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'ticker': ticker,
                    'alert_type': 'price_movement',
                    'previous_price': prev_price,
                    'current_price': current_price,
                    'change': current_price - prev_price,
                    'change_pct': round(change_pct, 2),
                    'message': f"{ticker}: ${prev_price:.2f} → ${current_price:.2f} ({change_pct:+.2f}%)"
                })
    
    return alerts


def check_breakouts(market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Check for 52W breakouts."""
    alerts = []
    
    for item in market_data:
        ticker = item['ticker']
        current_price = item['current_price']
        high_52w = item['52w_high']
        low_52w = item['52w_low']
        
        if current_price > high_52w * 1.01:  # Above 52W high
            alerts.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'ticker': ticker,
                'alert_type': 'breakout_up',
                'current_price': current_price,
                'level': high_52w,
                'message': f"{ticker}: Broke above 52W high ${high_52w:.2f}"
            })
        elif current_price < low_52w * 0.99:  # Below 52W low
            alerts.append({
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'ticker': ticker,
                'alert_type': 'breakout_down',
                'current_price': current_price,
                'level': low_52w,
                'message': f"{ticker}: Broke below 52W low ${low_52w:.2f}"
            })
    
    return alerts


def generate_daily_report(market_data: List[Dict[str, Any]], 
                         previous_data: Dict[str, Dict[str, float]] = None) -> Dict[str, Any]:
    """Generate daily price report."""
    previous_data = previous_data or {}
    gainers = []
    losers = []
    
    for item in market_data:
        ticker = item['ticker']
        current_price = item['current_price']
        
        if ticker in previous_data:
            prev_price = previous_data[ticker].get('current_price', current_price)
            change_pct = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
            change = current_price - prev_price
            
            if change_pct > 0:
                gainers.append({
                    'ticker': ticker,
                    'price': current_price,
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2)
                })
            elif change_pct < 0:
                losers.append({
                    'ticker': ticker,
                    'price': current_price,
                    'change': round(change, 2),
                    'change_pct': round(change_pct, 2)
                })
    
    gainers = sorted(gainers, key=lambda x: x['change_pct'], reverse=True)
    losers = sorted(losers, key=lambda x: x['change_pct'])
    
    largest_move = max(gainers + losers, key=lambda x: abs(x['change_pct'])) if gainers or losers else None
    
    return {
        'date': datetime.utcnow().date().isoformat(),
        'summary': {
            'gainers': gainers,
            'losers': losers,
            'largest_move': largest_move,
            'total_gainers': len(gainers),
            'total_losers': len(losers)
        }
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Monitor stocks for price alerts.')
    parser.add_argument('--watchlist', help='Watchlist JSON file')
    parser.add_argument('--portfolio', help='Portfolio CSV file')
    parser.add_argument('--config', help='Alert config JSON file')
    parser.add_argument('--monitor', choices=['volatility', 'concentration', 'trends', 'breakouts'], default='price')
    parser.add_argument('--report', choices=['daily', 'weekly', 'alerts'], help='Generate report')
    parser.add_argument('--threshold', type=float, default=0.02, help='Movement threshold')
    parser.add_argument('--detect-breakouts', action='store_true', help='Detect breakouts')
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--check-interval', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--log-file', help='Log file for daemon')
    parser.add_argument('--format', choices=['json', 'csv'], default='json')
    
    args = parser.parse_args()
    
    # For now, provide a simple implementation
    if args.watchlist:
        try:
            with open(args.watchlist) as f:
                watchlist_data = json.load(f)
                
                # Convert watchlist to market data format
                market_data = []
                if isinstance(watchlist_data, dict) and 'tickers' in watchlist_data:
                    # It's a watchlist, not market data
                    print("Note: Provide market_data.json for monitoring")
                    print("Watchlist contains:", watchlist_data['tickers'])
                else:
                    market_data = watchlist_data
        except Exception as e:
            print(f"Error loading watchlist: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Check breakouts if requested
    if args.detect_breakouts and market_data:
        alerts = check_breakouts(market_data)
        print(json.dumps({'alerts': alerts}, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump({'alerts': alerts}, f, indent=2)
    
    # Generate reports
    if args.report == 'daily' and market_data:
        report = generate_daily_report(market_data)
        print(json.dumps(report, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)


if __name__ == '__main__':
    main()
