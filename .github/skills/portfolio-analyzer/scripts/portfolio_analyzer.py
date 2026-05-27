"""Portfolio Analyzer - Analyze portfolio diversification, allocation, performance."""
from __future__ import annotations
import argparse
import json
import sys
from typing import Dict, List, Any, Optional
import pandas as pd


def analyze_portfolio(portfolio_df: pd.DataFrame, market_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """Analyze portfolio allocation and performance."""
    if market_data is None:
        market_data = {}
    
    # Create lookup
    market_lookup = {item['ticker']: item for item in market_data} if isinstance(market_data, list) else market_data
    
    # Calculate current values
    portfolio_df['current_price'] = portfolio_df['ticker'].map(
        lambda x: market_lookup.get(x, {}).get('current_price', 0) if isinstance(market_lookup, dict) else 0
    )
    portfolio_df['current_value'] = portfolio_df['quantity'] * portfolio_df['current_price']
    portfolio_df['unrealized_gain'] = portfolio_df['current_value'] - (portfolio_df['quantity'] * portfolio_df['buy_price'])
    portfolio_df['unrealized_gain_pct'] = (portfolio_df['unrealized_gain'] / (portfolio_df['quantity'] * portfolio_df['buy_price'])) * 100
    
    total_value = portfolio_df['current_value'].sum()
    total_cost = (portfolio_df['quantity'] * portfolio_df['buy_price']).sum()
    total_gain = portfolio_df['unrealized_gain'].sum()
    
    portfolio_df['weight'] = (portfolio_df['current_value'] / total_value) * 100
    
    # Sector breakdown
    sectors = {}
    for _, row in portfolio_df.iterrows():
        sector = row.get('sector_override', 'Unknown')
        if sector not in sectors:
            sectors[sector] = {
                'value': 0,
                'weight': 0,
                'positions': []
            }
        sectors[sector]['value'] += row['current_value']
        sectors[sector]['positions'].append(row['ticker'])
    
    for sector in sectors:
        sectors[sector]['weight'] = (sectors[sector]['value'] / total_value) * 100
    
    return {
        'summary': {
            'total_value': float(total_value),
            'total_cost_basis': float(total_cost),
            'unrealized_gain': float(total_gain),
            'unrealized_gain_pct': float((total_gain / total_cost * 100)) if total_cost > 0 else 0,
            'num_positions': len(portfolio_df),
            'concentration': portfolio_df['weight'].max() if len(portfolio_df) > 0 else 0
        },
        'positions': portfolio_df.to_dict('records'),
        'sectors': sectors
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Analyze portfolio allocation and performance.')
    parser.add_argument('--portfolio', required=True, help='Portfolio CSV file')
    parser.add_argument('--market-data', help='Market data JSON file')
    parser.add_argument('--report', default='summary', choices=['summary', 'full', 'comparison'])
    parser.add_argument('--output-format', default='json', choices=['json', 'table'])
    parser.add_argument('--output', help='Save results to file')
    
    args = parser.parse_args()
    
    # Load portfolio
    try:
        portfolio_df = pd.read_csv(args.portfolio)
    except Exception as e:
        print(f"Error loading portfolio: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Load market data if provided
    market_data = None
    if args.market_data:
        try:
            with open(args.market_data) as f:
                market_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load market data: {e}")
    
    # Analyze
    analysis = analyze_portfolio(portfolio_df, market_data)
    
    # Format output
    if args.output_format == 'json':
        output_str = json.dumps(analysis, indent=2)
    else:
        output_str = str(analysis)
    
    # Write output
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Analysis saved to {args.output}")
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    
    print(output_str)


if __name__ == '__main__':
    main()
