#!/usr/bin/env python3
"""
ThreatFeed - Main Entry Point

This is a convenience wrapper to run ThreatFeed components.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from aggregator import ThreatAggregator, main as aggregator_main


def main():
    parser = argparse.ArgumentParser(
        description="ThreatFeed - Threat Intelligence Aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show recent threats
  python main.py --recent

  # Run as daemon
  python main.py --daemon --interval 60

  # Start web dashboard
  python main.py --dashboard

  # Search threats
  python main.py --search "kubernetes" --severity high

  # Show statistics
  python main.py --stats
        """
    )

    parser.add_argument('--recent', action='store_true', help='Show recent threats')
    parser.add_argument('--critical', action='store_true', help='Show critical threats')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--daemon', action='store_true', help='Run as background daemon')
    parser.add_argument('--dashboard', action='store_true', help='Run web dashboard')
    parser.add_argument('--fetch', action='store_true', help='Fetch threats once')
    parser.add_argument('--search', type=str, help='Search for threats')
    parser.add_argument('--severity', choices=['critical', 'high', 'medium', 'low', 'info'])
    parser.add_argument('--source', type=str, help='Filter by source')
    parser.add_argument('--interval', type=int, default=60, help='Daemon interval (minutes)')
    parser.add_argument('--version', action='version', version='ThreatFeed 1.0.0')

    args = parser.parse_args()

    # If no arguments provided, show help and stats
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n" + "="*60)
        agg = ThreatAggregator()
        agg.print_stats()
        return

    # Handle dashboard separately
    if args.dashboard:
        print("Starting ThreatFeed Dashboard on http://localhost:8000")
        print("Press Ctrl+C to stop\n")
        try:
            import uvicorn
            from dashboard import app
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            print("\nDashboard stopped")
        return

    # Delegate to aggregator main
    sys.argv = [sys.argv[0]]

    if args.recent:
        sys.argv.append('--recent')
    elif args.critical:
        sys.argv.append('--critical')
    elif args.stats:
        sys.argv.append('--stats')
    elif args.daemon:
        sys.argv.append('--daemon')
        sys.argv.append('--interval')
        sys.argv.append(str(args.interval))
    elif args.fetch:
        sys.argv.append('--fetch')
    elif args.search:
        sys.argv.append('--search')
        sys.argv.append(args.search)
        if args.severity:
            sys.argv.append('--severity')
            sys.argv.append(args.severity)
        if args.source:
            sys.argv.append('--source')
            sys.argv.append(args.source)

    aggregator_main()


if __name__ == '__main__':
    main()
