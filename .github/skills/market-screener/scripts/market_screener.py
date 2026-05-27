"""Market Screener - Filter stocks by market cap, price, performance, volatility."""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd


@dataclass
class ScreenResult:
    ticker: str
    current_price: float
    price_52w_high: float
    price_52w_low: float
    market_cap_category: str
    distance_from_52w_high: float  # percentage
    distance_from_52w_low: float   # percentage
    range_52w: float  # absolute


def calculate_distance(current: float, high: float, low: float) -> tuple:
    """Calculate distance from 52W high/low as percentage."""
    if high == 0 or low == 0:
        return 0.0, 0.0
    
    dist_high = (current - high) / high * 100
    dist_low = (current - low) / low * 100
    range_52w = high - low
    
    return dist_high, dist_low, range_52w


def apply_filters(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply screening filters to market data."""
    results = []
    
    for item in data:
        ticker = item.get('ticker')
        current_price = item.get('current_price', 0)
        price_52w_high = item.get('52w_high', 0)
        price_52w_low = item.get('52w_low', 0)
        market_cap_category = item.get('market_cap_category', '')
        
        # Market cap filter
        if 'market_cap' in filters:
            allowed_categories = filters['market_cap']
            if market_cap_category not in allowed_categories:
                continue
        
        # Price range filters
        if 'min_price' in filters and current_price < filters['min_price']:
            continue
        if 'max_price' in filters and current_price > filters['max_price']:
            continue
        
        # 52W high/low distance filters
        dist_high, dist_low, range_52w = calculate_distance(
            current_price, price_52w_high, price_52w_low
        )
        
        if 'near_52w_high' in filters:
            threshold = filters['near_52w_high']
            if dist_high > -threshold * 100:  # within X% of high
                pass
            else:
                continue
        
        if 'near_52w_low' in filters:
            threshold = filters['near_52w_low']
            if dist_low < threshold * 100:  # within X% of low
                pass
            else:
                continue
        
        # Calculate volatility (simplified: 52W range / average price)
        avg_price = (price_52w_high + price_52w_low) / 2
        volatility = range_52w / avg_price if avg_price > 0 else 0
        
        if 'volatility_min' in filters and volatility < filters['volatility_min']:
            continue
        if 'volatility_max' in filters and volatility > filters['volatility_max']:
            continue
        
        # Passed all filters
        item_copy = item.copy()
        item_copy['distance_from_52w_high'] = round(dist_high, 2)
        item_copy['distance_from_52w_low'] = round(dist_low, 2)
        item_copy['52w_range_pct'] = round(volatility * 100, 2)
        item_copy['volatility'] = round(volatility, 4)
        results.append(item_copy)
    
    return results


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return {}


def format_table(data: List[Dict[str, Any]]) -> str:
    """Format results as pretty table."""
    if not data:
        return "No results found"
    
    lines = []
    lines.append("ticker  price       52W High  52W Low  Category  From High  From Low  Vol%")
    lines.append("------  --------    --------  -------  --------  ---------  --------  ----")
    
    for item in data:
        ticker = item['ticker'].ljust(6)
        price = f"${item['current_price']:.2f}".ljust(10)
        high = f"${item['52w_high']:.2f}".ljust(9)
        low = f"${item['52w_low']:.2f}".ljust(8)
        cat = item['market_cap_category'].ljust(9)
        from_high = f"{item['distance_from_52w_high']:+.1f}%".ljust(10)
        from_low = f"{item['distance_from_52w_low']:+.1f}%".ljust(9)
        vol = f"{item['52w_range_pct']:.1f}%"
        
        line = f"{ticker} {price} {high} {low} {cat} {from_high} {from_low} {vol}"
        lines.append(line)
    
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description='Screen stocks by market cap, price, performance.')
    parser.add_argument('--input', required=True, help='Market data JSON file')
    parser.add_argument('--market-cap', help='Comma-separated market cap categories')
    parser.add_argument('--min-price', type=float, help='Minimum price')
    parser.add_argument('--max-price', type=float, help='Maximum price')
    parser.add_argument('--near-52w-high', type=float, help='Within X% of 52W high')
    parser.add_argument('--near-52w-low', type=float, help='Within X% of 52W low')
    parser.add_argument('--volatility-min', type=float, help='Minimum volatility')
    parser.add_argument('--volatility-max', type=float, help='Maximum volatility')
    parser.add_argument('--config', help='JSON config file with filters')
    parser.add_argument('--output-format', default='json', choices=['json', 'csv', 'table'])
    parser.add_argument('--output', help='Save results to file')
    
    args = parser.parse_args()
    
    # Load filters from config or CLI
    filters = {}
    if args.config:
        filters = load_config(args.config)
    else:
        if args.market_cap:
            filters['market_cap'] = args.market_cap.split(',')
        if args.min_price:
            filters['min_price'] = args.min_price
        if args.max_price:
            filters['max_price'] = args.max_price
        if args.near_52w_high:
            filters['near_52w_high'] = args.near_52w_high
        if args.near_52w_low:
            filters['near_52w_low'] = args.near_52w_low
        if args.volatility_min:
            filters['volatility_min'] = args.volatility_min
        if args.volatility_max:
            filters['volatility_max'] = args.volatility_max
    
    # Load market data
    try:
        with open(args.input) as f:
            market_data = json.load(f)
    except Exception as e:
        print(f"Error loading market data: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Apply filters
    results = apply_filters(market_data, filters)
    
    if not results:
        print("No stocks match the screening criteria", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    if args.output_format == 'json':
        output_str = json.dumps(results, indent=2)
    elif args.output_format == 'csv':
        if results:
            df = pd.DataFrame(results)
            output_str = df.to_csv(index=False)
    else:  # table
        output_str = format_table(results)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Saved {len(results)} results to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(output_str)


if __name__ == '__main__':
    main()
