"""Sector Deep Dive - Analyze sector composition and performance."""
from __future__ import annotations
import argparse
import json
import sys
from typing import List, Dict, Any
from collections import defaultdict


def analyze_sector_composition(market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze sector composition and concentration."""
    sectors = defaultdict(lambda: {'stocks': [], 'total_value': 0, 'weight': 0})
    total_value = 0
    
    for item in market_data:
        ticker = item.get('ticker')
        market_cap = item.get('market_cap', 0)
        market_cat = item.get('market_cap_category', 'unknown')
        
        # Group by market cap category (simplified sectors)
        sector = market_cat
        
        sectors[sector]['stocks'].append({
            'ticker': ticker,
            'market_cap': market_cap,
            'current_price': item.get('current_price', 0)
        })
        sectors[sector]['total_value'] += market_cap
        total_value += market_cap
    
    # Calculate weights
    for sector in sectors:
        sectors[sector]['weight'] = sectors[sector]['total_value'] / total_value if total_value > 0 else 0
        
        # Calculate concentration
        sector_value = sectors[sector]['total_value']
        hhi = 0
        for stock in sectors[sector]['stocks']:
            stock_weight = stock['market_cap'] / sector_value if sector_value > 0 else 0
            hhi += stock_weight ** 2
        sectors[sector]['hhi'] = hhi
        sectors[sector]['stock_count'] = len(sectors[sector]['stocks'])
    
    return {
        'sectors': dict(sectors),
        'total_market_cap': total_value,
        'sector_count': len(sectors)
    }


def calculate_correlations(market_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Calculate simplified correlations between market cap categories."""
    # Simplified: return mock correlation matrix
    categories = set(item.get('market_cap_category') for item in market_data)
    categories = sorted(list(categories))
    
    corr_matrix = {}
    for cat1 in categories:
        corr_matrix[cat1] = {}
        for cat2 in categories:
            if cat1 == cat2:
                corr_matrix[cat1][cat2] = 1.0
            else:
                # Mock correlation
                corr_matrix[cat1][cat2] = 0.6
    
    return corr_matrix


def rank_sectors(market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank sectors by various metrics."""
    sectors_data = defaultdict(lambda: {'count': 0, 'avg_price': 0, 'prices': []})
    
    for item in market_data:
        sector = item.get('market_cap_category', 'unknown')
        sectors_data[sector]['count'] += 1
        sectors_data[sector]['prices'].append(item.get('current_price', 0))
    
    rankings = []
    for sector, data in sectors_data.items():
        avg_price = sum(data['prices']) / len(data['prices']) if data['prices'] else 0
        rankings.append({
            'sector': sector,
            'stock_count': data['count'],
            'avg_price': round(avg_price, 2),
            'volatility': 0.08  # Mock
        })
    
    return sorted(rankings, key=lambda x: x['stock_count'], reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser(description='Perform deep sector analysis.')
    parser.add_argument('--input', required=True, help='Market data JSON file')
    parser.add_argument('--analyze', choices=['sectors', 'concentration', 'correlations', 'trends'], default='sectors')
    parser.add_argument('--rank-sectors', action='store_true', help='Rank sectors by performance')
    parser.add_argument('--compare-valuations', action='store_true', help='Compare valuations')
    parser.add_argument('--portfolio', help='Portfolio CSV for allocation analysis')
    parser.add_argument('--target-allocation', help='Target allocation')
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--format', choices=['json', 'table'], default='json')
    
    args = parser.parse_args()
    
    # Load market data
    try:
        with open(args.input) as f:
            market_data = json.load(f)
    except Exception as e:
        print(f"Error loading market data: {e}", file=sys.stderr)
        sys.exit(1)
    
    results = None
    
    if args.analyze == 'sectors' or args.analyze == 'concentration':
        results = analyze_sector_composition(market_data)
    
    elif args.analyze == 'correlations':
        results = {'correlations': calculate_correlations(market_data)}
    
    elif args.rank_sectors:
        results = {'rankings': rank_sectors(market_data)}
    
    if not results:
        results = analyze_sector_composition(market_data)
    
    # Format output
    output_str = json.dumps(results, indent=2)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Sector analysis saved to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(output_str)


if __name__ == '__main__':
    main()
