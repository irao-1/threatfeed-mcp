"""Filter for operational and strategic threats only - STRICT VERSION."""

from models import ThreatCategory, SeverityLevel

# ONLY these count as real security threats
OPERATIONAL_CATEGORIES = {
    ThreatCategory.CVE,
    ThreatCategory.VULNERABILITY,
    ThreatCategory.BREACH,
    ThreatCategory.MALWARE,
    ThreatCategory.RANSOMWARE,
    ThreatCategory.EXPLOIT,
    ThreatCategory.APT,
    ThreatCategory.ZERO_DAY,
}

# BLOCK everything else - comprehensive list
BLOCKED_KEYWORDS = {
    # Business/acquisitions
    'doorDash', 'instacart', 'acquisition', 'acquired', 'acquiring',
    'startup', 'funding', 'investment', 'ipo', 'series', 'round',
    'earnings', 'stock', 'market', 'business', 'deal',
    
    # Tech news (not security)
    'react', 'suspense', 'lazy', 'javascript', 'nodejs',
    'python release', 'new feature', 'update', 'version',
    'api', 'framework', 'library', 'development',
    
    # Non-security
    'ai model', 'gpt', 'llm', 'language model',
    'fbi letter', 'mlk', 'history', 'politics',
    'google news', 'amazon news', 'apple news',
    'microsoft news', 'meta news',
    'spacex', 'tesla', 'elon',
}

def is_operational_threat(threat):
    """Check if threat is operational/strategic, not general news."""
    
    # Must be in OPERATIONAL categories ONLY
    if threat.category not in OPERATIONAL_CATEGORIES:
        return False
    
    # Check for blocked keywords in title and description
    text = (threat.title + ' ' + threat.description).lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in text:
            return False
    
    return True


def filter_operational_threats(threats):
    """Filter list to only operational threats."""
    return [t for t in threats if is_operational_threat(t)]
