"""RSS feed sources for threat intelligence."""

import feedparser
import logging
from typing import List
from datetime import datetime
from models import Threat
from utils import (
    extract_cves, generate_id, score_severity,
    categorize_threat, extract_keywords, calculate_confidence,
    parse_rfc822_date, similarity_score
)
from .cisa_kev_source import CISAKEVSource

logger = logging.getLogger(__name__)


class RSSSource:
    """Base RSS feed source."""

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def fetch(self) -> List[Threat]:
        """Fetch threats from RSS feed."""
        threats = []
        try:
            logger.info(f"Fetching from {self.name}: {self.url}")
            feed = feedparser.parse(self.url)

            if feed.bozo:
                logger.warning(f"Feed parsing warning for {self.name}: {feed.bozo_exception}")

            for entry in feed.entries[:20]:
                threat = self._parse_entry(entry)
                if threat:
                    threats.append(threat)

            logger.info(f"Got {len(threats)} threats from {self.name}")
        except Exception as e:
            logger.error(f"Error fetching from {self.name}: {e}")

        return threats

    def _parse_entry(self, entry) -> Threat:
        """Parse RSS entry into Threat object."""
        title = entry.get('title', 'No title')
        summary = entry.get('summary', '') or entry.get('description', '')
        link = entry.get('link', '')

        if not link:
            return None

        threat_id = generate_id(link)

        pub_date = datetime.utcnow()
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            pub_date = datetime(*entry.published_parsed[:6])
        elif entry.get('published'):
            pub_date = parse_rfc822_date(entry.get('published'))

        cves = extract_cves(f"{title} {summary}")
        keywords = extract_keywords(f"{title} {summary}")
        severity = score_severity(title, summary)
        category = categorize_threat(title, summary)
        confidence = calculate_confidence(
            self.name,
            bool(cves),
            'affected' in summary.lower()
        )

        return Threat(
            id=threat_id,
            title=title,
            description=summary[:500],
            source=self.name,
            url=link,
            published_date=pub_date,
            severity=severity,
            category=category,
            cves=cves,
            keywords=keywords,
            confidence_score=confidence
        )


# Define all threat sources
THREAT_SOURCES = {
    'bleeping_computer': RSSSource(
        'Bleeping Computer',
        'https://www.bleepingcomputer.com/feed/'
    ),
    'hackernews': RSSSource(
        'HackerNews',
        'https://news.ycombinator.com/rss'
    ),
    'reddit_netsec': RSSSource(
        'Reddit r/netsec',
        'https://www.reddit.com/r/netsec/.rss'
    ),
    'securityweek': RSSSource(
        'SecurityWeek',
        'https://www.securityweek.com/feed/'
    ),
    'cisa_kev': CISAKEVSource(),
}


def get_all_sources() -> dict:
    """Get all configured sources."""
    return THREAT_SOURCES


def fetch_all_threats(dedup_threshold: float = 0.7, days: int = 7) -> tuple:
    """Fetch from all sources and deduplicate.
    
    Args:
        dedup_threshold: Similarity threshold for deduplication (0-1)
        days: Only fetch threats from last N days
    """
    all_threats = []
    stats = {}

    from datetime import timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    for source_name, source in THREAT_SOURCES.items():
        try:
            threats = source.fetch()
            # Filter by date
            filtered_threats = [t for t in threats if t.published_date > cutoff_date]
            stats[source.name] = {
                'fetched': len(filtered_threats),
                'errors': None
            }
            all_threats.extend(filtered_threats)
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
            stats[source.name] = {
                'fetched': 0,
                'errors': str(e)
            }

    # Deduplication
    unique_threats = []
    seen_ids = set()

    for threat in sorted(all_threats, key=lambda t: t.published_date, reverse=True):
        if threat.id in seen_ids:
            threat.is_duplicate = True
            continue

        is_similar = False
        for existing in unique_threats[-5:]:
            if similarity_score(threat.title, existing.title) > dedup_threshold:
                threat.is_duplicate = True
                threat.duplicate_of = existing.id
                is_similar = True
                break

        if not is_similar:
            seen_ids.add(threat.id)
            unique_threats.append(threat)

    return unique_threats, stats
