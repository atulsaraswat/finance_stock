"""Watchlist Manager - Create and manage stock watchlists."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


WATCHLIST_DIR = Path('Finance')


def load_watchlist(name: str) -> Optional[Dict[str, Any]]:
    """Load watchlist from file."""
    path = WATCHLIST_DIR / f'watchlist_{name}.json'
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading watchlist: {e}", file=sys.stderr)
        return None


def save_watchlist(watchlist: Dict[str, Any]) -> bool:
    """Save watchlist to file."""
    name = watchlist['name']
    path = WATCHLIST_DIR / f'watchlist_{name}.json'
    try:
        with open(path, 'w') as f:
            json.dump(watchlist, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving watchlist: {e}", file=sys.stderr)
        return False


def create_watchlist(name: str, tickers: List[str], tags: Optional[List[str]] = None, notes: str = '') -> Dict[str, Any]:
    """Create a new watchlist."""
    return {
        'name': name,
        'tickers': list(set(t.upper() for t in tickers)),
        'tags': tags or [],
        'created': datetime.utcnow().isoformat() + 'Z',
        'last_updated': datetime.utcnow().isoformat() + 'Z',
        'notes': notes,
        'history': [
            {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'action': 'create',
                'tickers': list(set(t.upper() for t in tickers))
            }
        ]
    }


def add_tickers(watchlist: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
    """Add tickers to watchlist."""
    new_tickers = list(set(watchlist['tickers'] + [t.upper() for t in tickers]))
    added = [t for t in new_tickers if t not in watchlist['tickers']]
    
    watchlist['tickers'] = new_tickers
    watchlist['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    watchlist['history'].append({
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'action': 'add',
        'tickers': added
    })
    
    return watchlist


def remove_tickers(watchlist: Dict[str, Any], tickers: List[str]) -> Dict[str, Any]:
    """Remove tickers from watchlist."""
    to_remove = set(t.upper() for t in tickers)
    removed = [t for t in watchlist['tickers'] if t in to_remove]
    
    watchlist['tickers'] = [t for t in watchlist['tickers'] if t not in to_remove]
    watchlist['last_updated'] = datetime.utcnow().isoformat() + 'Z'
    watchlist['history'].append({
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'action': 'remove',
        'tickers': removed
    })
    
    return watchlist


def main() -> None:
    parser = argparse.ArgumentParser(description='Manage stock watchlists.')
    parser.add_argument('--name', help='Watchlist name')
    parser.add_argument('--create', action='store_true', help='Create new watchlist')
    parser.add_argument('--tickers', help='Comma-separated tickers')
    parser.add_argument('--from-file', help='Load tickers from JSON file')
    parser.add_argument('--add', help='Add tickers')
    parser.add_argument('--remove', help='Remove tickers')
    parser.add_argument('--merge', nargs='+', help='Merge multiple watchlists')
    parser.add_argument('--show', action='store_true', help='Show watchlist details')
    parser.add_argument('--list-all', action='store_true', help='List all watchlists')
    parser.add_argument('--history', action='store_true', help='Show change history')
    parser.add_argument('--export', choices=['json', 'csv'], help='Export format')
    parser.add_argument('--output', help='Output file')
    parser.add_argument('--tags', help='Comma-separated tags')
    parser.add_argument('--notes', help='Notes/description')
    
    args = parser.parse_args()
    
    # List all watchlists
    if args.list_all:
        WATCHLIST_DIR.mkdir(exist_ok=True)
        watchlists = list(WATCHLIST_DIR.glob('watchlist_*.json'))
        if not watchlists:
            print("No watchlists found")
        else:
            for wl_file in sorted(watchlists):
                try:
                    with open(wl_file) as f:
                        wl = json.load(f)
                        created = wl.get('created', 'unknown')
                        count = len(wl.get('tickers', []))
                        print(f"  {wl['name']} ({count} tickers, created {created[:10]})")
                except:
                    pass
        return
    
    if not args.name and not args.merge:
        parser.print_help()
        return
    
    # Create
    if args.create:
        tickers = []
        if args.tickers:
            tickers = args.tickers.split(',')
        elif args.from_file:
            try:
                with open(args.from_file) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        tickers = [item.get('ticker', item) for item in data]
                    elif isinstance(data, dict):
                        tickers = data.get('tickers', [])
            except Exception as e:
                print(f"Error loading tickers: {e}", file=sys.stderr)
                return
        
        tags = args.tags.split(',') if args.tags else []
        watchlist = create_watchlist(args.name, tickers, tags, args.notes or '')
        
        WATCHLIST_DIR.mkdir(exist_ok=True)
        if save_watchlist(watchlist):
            print(f"Created watchlist '{args.name}' with {len(tickers)} tickers")
        return
    
    # Load existing watchlist
    watchlist = load_watchlist(args.name)
    if not watchlist:
        print(f"Watchlist '{args.name}' not found", file=sys.stderr)
        return
    
    # Show
    if args.show:
        print(json.dumps(watchlist, indent=2))
        return
    
    # History
    if args.history:
        for entry in watchlist.get('history', []):
            print(f"{entry['timestamp']}  {entry['action'].upper()}: {', '.join(entry.get('tickers', []))}")
        return
    
    # Add/Remove
    if args.add:
        watchlist = add_tickers(watchlist, args.add.split(','))
        if save_watchlist(watchlist):
            print(f"Added {len(args.add.split(','))} tickers")
    
    if args.remove:
        watchlist = remove_tickers(watchlist, args.remove.split(','))
        if save_watchlist(watchlist):
            print(f"Removed {len(args.remove.split(','))} tickers")
    
    # Export
    if args.export:
        WATCHLIST_DIR.mkdir(exist_ok=True)
        if args.export == 'json':
            output = json.dumps(watchlist, indent=2)
        else:  # csv
            lines = ['ticker']
            lines.extend(watchlist['tickers'])
            output = '\n'.join(lines)
        
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Exported to {args.output}")
            except Exception as e:
                print(f"Error exporting: {e}", file=sys.stderr)
        else:
            print(output)


if __name__ == '__main__':
    main()
