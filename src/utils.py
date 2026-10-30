"""Utility functions for threat analysis."""

import re
import hashlib
from datetime import datetime
from typing import List, Tuple
from html.parser import HTMLParser
from models import SeverityLevel, ThreatCategory


class HTMLStripper(HTMLParser):
    """Strip HTML tags from text."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text).strip()


def strip_html(text: str) -> str:
    """Remove HTML tags from text and clean up whitespace."""
    if not text:
        return ""
    try:
        s = HTMLStripper()
        s.feed(text)
        return s.get_data()
    except:
        return text


# CVE pattern
CVE_PATTERN = re.compile(r'CVE-\d{4}-\d{4,}', re.IGNORECASE)

# Malware patterns
MALWARE_KEYWORDS = [
    'ransomware', 'trojan', 'worm', 'virus', 'backdoor', 'spyware',
    'adware', 'botnet', 'rootkit', 'keylogger', 'malware'
]

# Severity keywords
CRITICAL_KEYWORDS = [
    'critical', 'zero-day', 'rce', 'remote code execution',
    'arbitrary code execution', 'unauthenticated', 'unpatched',
    'widespread attack', 'mass exploitation', 'exploit available',
    'worm', 'spreading'
]

HIGH_KEYWORDS = [
    'high', 'vulnerability', 'exploit', 'authenticated',
    'local', 'privilege escalation', 'information disclosure'
]

MEDIUM_KEYWORDS = [
    'medium', 'moderate', 'denial of service', 'crash'
]

LOW_KEYWORDS = [
    'low', 'minor', 'information leak'
]

# Breach keywords
BREACH_KEYWORDS = [
    'breach', 'data leak', 'hacked', 'compromised', 'stolen',
    'exfiltrated', 'ransomware attack', 'attack'
]

# APT keywords
APT_KEYWORDS = [
    'apt', 'advanced persistent threat', 'nation state', 'state-sponsored',
    'threat actor', 'group'
]


def extract_cves(text: str) -> List[str]:
    """Extract CVE IDs from text."""
    if not text:
        return []
    matches = CVE_PATTERN.findall(text.upper())
    return list(set(matches))  # Remove duplicates


def generate_id(url: str) -> str:
    """Generate unique ID from URL."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def score_severity(title: str, description: str) -> SeverityLevel:
    """Score threat severity based on content."""
    text = f"{title} {description}".lower()

    # Check critical keywords
    if any(kw in text for kw in CRITICAL_KEYWORDS):
        return SeverityLevel.CRITICAL

    # Check high keywords
    if any(kw in text for kw in HIGH_KEYWORDS):
        return SeverityLevel.HIGH

    # Check medium keywords
    if any(kw in text for kw in MEDIUM_KEYWORDS):
        return SeverityLevel.MEDIUM

    # Check low keywords
    if any(kw in text for kw in LOW_KEYWORDS):
        return SeverityLevel.LOW

    return SeverityLevel.INFO


def categorize_threat(title: str, description: str) -> ThreatCategory:
    """Categorize threat based on content."""
    text = f"{title} {description}".lower()

    # Check for CVE FIRST - highest priority
    if 'cve-' in text or 'cve ' in text or 'cve:' in text or 'php' in text and 'vulnerability' in text:
        return ThreatCategory.CVE
    if CVE_PATTERN.search(text):
        return ThreatCategory.CVE

    # Check for malware
    if any(kw in text for kw in MALWARE_KEYWORDS):
        return ThreatCategory.MALWARE

    # Check for breach
    if any(kw in text for kw in BREACH_KEYWORDS):
        return ThreatCategory.BREACH

    # Check for ransomware (more specific)
    if 'ransomware' in text:
        return ThreatCategory.RANSOMWARE

    # Check for zero-day
    if 'zero-day' in text or 'zero day' in text:
        return ThreatCategory.ZERO_DAY

    # Check for APT
    if any(kw in text for kw in APT_KEYWORDS):
        return ThreatCategory.APT

    # Check for phishing
    if 'phishing' in text or 'phish' in text:
        return ThreatCategory.PHISHING

    # Check for exploit
    if 'exploit' in text:
        return ThreatCategory.EXPLOIT

    # Default
    if 'vulnerability' in text or 'vuln' in text:
        return ThreatCategory.VULNERABILITY

    return ThreatCategory.GENERAL


def extract_keywords(text: str, limit: int = 5) -> List[str]:
    """Extract important keywords from text."""
    if not text:
        return []

    # Simple keyword extraction - split and find common security terms
    words = text.lower().split()
    security_terms = set()

    security_keywords = [
        'vulnerability', 'exploit', 'malware', 'ransomware', 'breach',
        'attack', 'threat', 'threat actor', 'apt', 'zero-day', 'worm',
        'trojan', 'backdoor', 'patch', 'cve', 'microsoft', 'apple',
        'google', 'linux', 'windows', 'ios', 'android', 'kubernetes',
        'docker', 'aws', 'azure', 'gcp', 'sql', 'mongodb', 'postgresql'
    ]

    for word in words:
        word_clean = word.strip('.,;:!?()[]')
        if word_clean in security_keywords:
            security_terms.add(word_clean)

    return list(security_terms)[:limit]


def calculate_confidence(source: str, has_cves: bool, has_products: bool) -> float:
    """Calculate confidence score for a threat."""
    score = 0.5  # Base score

    # Source reputation
    trusted_sources = ['bleeping computer', 'cisa', 'palo alto', 'nist']
    if any(src in source.lower() for src in trusted_sources):
        score += 0.2

    # Has CVE = more credible
    if has_cves:
        score += 0.15

    # Has affected products = more detailed
    if has_products:
        score += 0.15

    return min(score, 1.0)


def parse_rfc822_date(date_str: str) -> datetime:
    """Parse RFC 822 date string (used in RSS feeds)."""
    try:
        # Try common formats
        for fmt in [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S',
        ]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Fallback to now
        return datetime.utcnow()
    except:
        return datetime.utcnow()


def similarity_score(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (0.0 to 1.0)."""
    if not text1 or not text2:
        return 0.0

    # Simple word overlap
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    overlap = len(words1 & words2)
    total = len(words1 | words2)

    return overlap / total if total > 0 else 0.0
