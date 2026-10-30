"""Data models for threat intelligence."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SeverityLevel(str, Enum):
    """Severity levels for threats."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ThreatCategory(str, Enum):
    """Categories of threats."""
    CVE = "cve"
    VULNERABILITY = "vulnerability"
    MALWARE = "malware"
    BREACH = "breach"
    RANSOMWARE = "ransomware"
    ZERO_DAY = "zero_day"
    EXPLOIT = "exploit"
    PHISHING = "phishing"
    APT = "apt"
    GENERAL = "general"


@dataclass
class Threat:
    """Represents a single threat article/alert."""

    id: str  # Unique ID (hash of URL)
    title: str
    description: str
    source: str  # Source name (e.g., "Bleeping Computer", "HackerNews")
    url: str
    published_date: datetime
    fetched_date: datetime = field(default_factory=datetime.utcnow)

    severity: SeverityLevel = SeverityLevel.INFO
    category: ThreatCategory = ThreatCategory.GENERAL

    # Extracted data
    cves: List[str] = field(default_factory=list)  # CVE IDs mentioned
    affected_products: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # Metadata
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    confidence_score: float = 0.0  # 0.0 to 1.0

    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "url": self.url,
            "published_date": self.published_date.isoformat(),
            "fetched_date": self.fetched_date.isoformat(),
            "severity": self.severity.value,
            "category": self.category.value,
            "cves": self.cves,
            "affected_products": self.affected_products,
            "keywords": self.keywords,
            "confidence_score": self.confidence_score,
        }

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} ({self.source})"


@dataclass
class FetchResult:
    """Result of a fetch operation."""

    source: str
    threats_found: int
    threats_new: int
    threats_duplicate: int
    errors: List[str] = field(default_factory=list)
    fetch_time_seconds: float = 0.0

    def __str__(self):
        return (
            f"{self.source}: {self.threats_found} found, "
            f"{self.threats_new} new, {self.threats_duplicate} duplicate"
        )


@dataclass
class SearchQuery:
    """Query for searching threats."""

    keywords: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    category: Optional[ThreatCategory] = None
    source: Optional[str] = None
    days_back: int = 7
    limit: int = 50
    offset: int = 0


@dataclass
class Stats:
    """Statistics about the threat database."""

    total_threats: int
    by_severity: dict  # {severity: count}
    by_category: dict  # {category: count}
    by_source: dict    # {source: count}
    last_fetch: datetime
    threats_this_week: int
    threats_this_month: int
