"""Core threat aggregator with scheduling."""

import logging
import argparse
import sys
from datetime import datetime
from typing import List
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from models import Threat, FetchResult, SearchQuery, Stats, SeverityLevel
from database import ThreatDatabase
from sources.rss_sources import fetch_all_threats, THREAT_SOURCES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThreatAggregator:
    """Main threat aggregator."""

    def __init__(self, db_path: str = "data/threats.db"):
        self.db = ThreatDatabase(db_path)
        self.scheduler = None

    def fetch_threats(self, days: int = 7) -> FetchResult:
        """Fetch threats from all sources."""
        logger.info(f"Starting threat fetch (last {days} days)...")

        try:
            all_threats, stats = fetch_all_threats(days=days)

            total_fetched = sum(s['fetched'] for s in stats.values())
            logger.info(f"Total threats fetched: {total_fetched}")

            new_count = 0
            duplicate_count = 0

            for threat in all_threats:
                if threat.is_duplicate:
                    duplicate_count += 1
                else:
                    if self.db.save_threat(threat):
                        new_count += 1
                    self.db.save_threat(threat)

            logger.info(f"Saved {new_count} new threats, {duplicate_count} duplicates")

            errors = [s['errors'] for s in stats.values() if s.get('errors')]
            self.db.log_fetch(
                source="aggregator",
                found=total_fetched,
                new=new_count,
                errors=errors
            )

            return FetchResult(
                source="aggregator",
                threats_found=total_fetched,
                threats_new=new_count,
                threats_duplicate=duplicate_count,
                errors=errors
            )

        except Exception as e:
            logger.error(f"Error during fetch: {e}", exc_info=True)
            return FetchResult(
                source="aggregator",
                threats_found=0,
                threats_new=0,
                threats_duplicate=0,
                errors=[str(e)]
            )

    def search(self, keywords: str = None, severity: SeverityLevel = None,
               limit: int = 50, days: int = 7) -> List[Threat]:
        """Search threats."""
        query = SearchQuery(
            keywords=keywords,
            severity=severity,
            days_back=days,
            limit=limit
        )
        return self.db.search_threats(query)

    def get_critical_threats(self, limit: int = 20) -> List[Threat]:
        """Get critical threats."""
        return self.db.get_by_severity(SeverityLevel.CRITICAL, limit=limit)

    def get_recent_threats(self, limit: int = 50, days: int = 7) -> List[Threat]:
        """Get recent threats."""
        return self.db.get_recent_threats(limit=limit, days=days)

    def get_by_source(self, source: str, limit: int = 50) -> List[Threat]:
        """Get threats from a source."""
        return self.db.get_by_source(source, limit=limit)

    def get_stats(self) -> Stats:
        """Get statistics."""
        return self.db.get_stats()

    def cleanup(self, days: int = 90):
        """Clean up old threats."""
        removed = self.db.cleanup_old_threats(days=days)
        logger.info(f"Cleaned up {removed} old duplicate threats")
        return removed

    def start_scheduler(self, interval_minutes: int = 60):
        """Start background scheduler."""
        logger.info(f"Starting scheduler (interval: {interval_minutes} minutes)")

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.fetch_threats,
            'interval',
            minutes=interval_minutes,
            next_run_time=datetime.now()
        )

        self.scheduler.add_job(
            self.cleanup,
            'cron',
            hour=2,
            minute=0
        )

        self.scheduler.start()
        logger.info("Scheduler started")

    def stop_scheduler(self):
        """Stop background scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def print_stats(self):
        """Print statistics."""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("THREAT INTELLIGENCE STATISTICS")
        print("="*60)
        print(f"Total unique threats: {stats.total_threats}")
        print(f"Threats this week: {stats.threats_this_week}")
        print(f"Threats this month: {stats.threats_this_month}")
        print(f"Last fetch: {stats.last_fetch.strftime('%Y-%m-%d %H:%M:%S')}")

        print("\nBy Severity:")
        for sev, count in sorted(stats.by_severity.items(), reverse=True):
            print(f"  {sev.upper()}: {count}")

        print("\nBy Source:")
        for src, count in sorted(stats.by_source.items(), key=lambda x: x[1], reverse=True):
            print(f"  {src}: {count}")

        print("\nBy Category:")
        for cat, count in sorted(stats.by_category.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count}")
        print("="*60 + "\n")

    def print_critical_threats(self, limit: int = 10):
        """Print critical threats."""
        threats = self.get_critical_threats(limit=limit)
        print("\n" + "="*60)
        print(f"CRITICAL THREATS (Top {limit})")
        print("="*60)

        if not threats:
            print("No critical threats found")
        else:
            for i, threat in enumerate(threats, 1):
                print(f"\n{i}. [{threat.severity.upper()}] {threat.title}")
                print(f"   Source: {threat.source}")
                print(f"   Date: {threat.published_date.strftime('%Y-%m-%d %H:%M')}")
                if threat.cves:
                    print(f"   CVEs: {', '.join(threat.cves)}")
                print(f"   {threat.url}")

        print("="*60 + "\n")

    def print_recent_threats(self, limit: int = 20, days: int = 7):
        """Print recent threats (operational only)."""
        from threat_filter import filter_operational_threats
        all_threats = self.get_recent_threats(limit=limit*3, days=days)
        threats = filter_operational_threats(all_threats)[:limit]
        print("\n" + "="*60)
        print(f"OPERATIONAL & STRATEGIC THREATS (Last {days} days, showing {min(len(threats), limit)})")
        print("="*60)

        if not threats:
            print("No operational threats found")
        else:
            for i, threat in enumerate(threats, 1):
                print(f"\n{i}. [{threat.severity.upper()}] {threat.title}")
                print(f"   Source: {threat.source} | Category: {threat.category.value}")
                print(f"   Date: {threat.published_date.strftime('%Y-%m-%d')}")

        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Threat Intelligence Aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --recent
  python main.py --fetch --days 30
  python main.py --daemon --interval 60
  python main.py --stats
        """
    )

    parser.add_argument('--init', action='store_true', help='Initialize database')
    parser.add_argument('--fetch', action='store_true', help='Fetch threats once')
    parser.add_argument('--daemon', action='store_true', help='Run as background daemon')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--critical', action='store_true', help='Show critical threats')
    parser.add_argument('--recent', action='store_true', help='Show recent threats')
    parser.add_argument('--search', type=str, help='Search for threats by keyword')
    parser.add_argument('--source', type=str, help='Filter by source')
    parser.add_argument('--severity', type=str, choices=['critical', 'high', 'medium', 'low', 'info'], help='Filter by severity')
    parser.add_argument('--db', type=str, default='data/threats.db', help='Database path')
    parser.add_argument('--interval', type=int, default=60, help='Daemon interval in minutes (default: 60)')
    parser.add_argument('--days', type=int, default=7, help='Fetch threats from last N days (default: 7)')

    args = parser.parse_args()

    agg = ThreatAggregator(db_path=args.db)

    if args.init:
        logger.info("Database initialized")
        agg.print_stats()

    elif args.fetch:
        logger.info(f"Fetching threats from last {args.days} days...")
        result = agg.fetch_threats(days=args.days)
        print(f"\n{result}")
        agg.print_stats()

    elif args.critical:
        agg.print_critical_threats()

    elif args.recent:
        agg.print_recent_threats(days=args.days)

    elif args.stats:
        agg.print_stats()

    elif args.search:
        logger.info(f"Searching for: {args.search}")
        severity = SeverityLevel(args.severity) if args.severity else None
        threats = agg.search(keywords=args.search, severity=severity, days=args.days)
        print(f"\nFound {len(threats)} threats:")
        for threat in threats:
            print(f"  [{threat.severity.upper()}] {threat.title} ({threat.source})")

    elif args.daemon:
        print("Starting Threat Aggregator Daemon...")
        print("Press Ctrl+C to stop\n")

        agg.start_scheduler(interval_minutes=args.interval)

        agg.fetch_threats(days=args.days)

        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            agg.stop_scheduler()

    else:
        agg.print_stats()
        agg.print_recent_threats(limit=10, days=args.days)


if __name__ == '__main__':
    main()
