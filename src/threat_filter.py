"""Filter for operational and strategic threats only - WITH SAFETY VALVES."""

from models import ThreatCategory, SeverityLevel

# TRUSTED SECURITY SOURCES - More lenient filtering (dedicated security sites)
TRUSTED_SOURCES = {
    'Unit42_Research',
    'Bleeping Computer',
    'The Hacker News',
    'CISA KEV',
    'SecurityWeek',
}

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
    ThreatCategory.PHISHING,
    ThreatCategory.GENERAL,  # Include general threats from trusted sources
}

# SAFETY VALVES - FORCE RETENTION of critical threat indicators
CRITICAL_KEYWORDS = {
    # Active Exploitation & Critical Indicators
    'active exploitation', 'exploited in the wild', 'cisa kev',
    'zero-day', '0-day', 'n-day',
    'unauthenticated rce', 'remote code execution', 'rce',
    'authentication bypass', 'privilege escalation', 'priv esc',
    'ransomware', 'extortion', 'mass scanning', 'data exfiltration',
    'worm', 'spreading', 'unpatched', 'widespread attack',

    # Evasion & Tradecraft
    'edr killer', 'byovd', 'bring your own vulnerable driver',
    'dll sideloading', 'stealer', 'botnet', 'c2', 'c&c',
    'command and control', 'lateral movement', 'persistence',
    'defense evasion', 'apt', 'advanced persistent threat',
    'threat actor', 'nation state', 'state-sponsored',

    # Edge & Network Security Products
    'fortigate', 'fortimail', 'fortisiem', 'fortisandbox', 'fortinet',
    'cisco catalyst', 'cisco ios', 'sd-wan', 'ios xr', 'secure email',
    'cisco fmc', 'cisco firepower',
    'citrix netscaler', 'citrix',
    'pan-os', 'palo alto', 'paloalto', 'palo networks',
    'ivanti connect secure', 'ivanti', 'pulse connect secure',
    'sonicwall sma', 'sonicwall', 'dell sonicwall',
    'check point', 'checkpoint',
    'f5 big-ip', 'f5', 'big-ip',

    # Enterprise Platforms & Identity
    'microsoft exchange', 'exchange server', 'sharepoint', 'outlook',
    'windows', 'active directory', 'microsoft sql', 'mssql',
    'vmware vcenter', 'vcenter', 'esxi', 'vmware',
    'veeam', 'backup',
    'splunk', 'elastic', 'elasticsearch', 'kibana',
    'servicenow', 'service now',
    'atlassian', 'jira', 'confluence', 'bitbucket',
    'sap', 'sap hana', 'oracle',

    # Supply-Chain & Ecosystem
    'npm', 'pypi', 'nuget', 'maven', 'ruby gems',
    'github actions', 'github', 'gitlab ci', 'jenkins',
    'ci/cd', 'cicd', 'devops', 'container',
    'docker', 'kubernetes', 'k8s',
    'supply chain', 'supply-chain', 'compromised',
    'credential leak', 'credentials leaked', 'api key',
    'build pipeline', 'pipeline poisoning', 'package compromise',
    'open source', 'dependency', 'vulnerable dependency',
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

    # Marketing/Press releases
    'announcement', 'magic quadrant', 'gartner', 'leader', 'named a',
    'press release', 'announces', 'marketplace', 'openai marketplace',
    'product launch', 'new product', 'new service',
    'partnership', 'partners with', 'integrates with',
    'prisma', 'continuous ai defense', 'ai defense', 'cortex xdr',
    'gartner magic quadrant', 'recognized as a leader',
    'privileged access management', 'pam', 'award',
    'eighth consecutive', 'positioned furthest',
    'products and services', 'introducing', 'managed agentic',
    'reinventing', 'evolves its',

    # Non-security
    'ai model', 'gpt', 'llm', 'language model',
    'fbi letter', 'mlk', 'history', 'politics',
    'google news', 'amazon news', 'apple news',
    'microsoft news', 'meta news',
    'spacex', 'tesla', 'elon',
}

def is_operational_threat(threat):
    """Check if threat is operational/strategic, not general news.

    Safety Valves: Critical threat indicators ALWAYS retained for triage,
    detection engineering, threat hunting, or security bulletins.

    Trusted sources get lenient filtering since they don't publish random news.
    """
    text = (threat.title + ' ' + threat.description).lower()
    url = threat.url.lower() if threat.url else ""
    is_trusted_source = threat.source in TRUSTED_SOURCES

    # FIRST: Check URL categories to exclude (products, announcements)
    # For non-trusted sources, block /news/ category pages
    # For trusted sources, only block specific product/announcement categories
    if is_trusted_source:
        # Trusted sources: only block specific categories
        blocked_url_patterns_trusted = [
            'products-and-services',
            'announcements',
            'press-releases',
            '/category/announcement/',
            '/category/partners/',
            '/category/products-and-services/',
            '/category/customer-spotlight/',
        ]
        for pattern in blocked_url_patterns_trusted:
            if pattern in url:
                return False
    else:
        # Non-trusted sources: block broader patterns including /news/
        blocked_url_patterns = [
            'products-and-services',
            'announcements',
            'press-releases',
            'news',
            '/news/',
            '/company/',
            '/careers/',
            '/category/announcement/',
            '/category/partners/',
            '/category/products-and-services/',
            '/category/customer-spotlight/',
        ]
        for pattern in blocked_url_patterns:
            if pattern in url:
                return False

    # SECOND: CRITICAL KEYWORDS always pass (universal safety valve)
    for keyword in CRITICAL_KEYWORDS:
        if keyword.lower() in text:
            return True

    # THIRD: Monitored products always pass (universal safety valve)
    monitored_products = {'fortigate', 'cisco', 'citrix', 'pan-os', 'palo alto',
                         'ivanti', 'sonicwall', 'check point', 'f5',
                         'microsoft', 'vmware', 'veeam', 'splunk', 'servicenow'}
    for product in monitored_products:
        if product.lower() in text:
            return True

    # TRUSTED SOURCES: Accept operational content without keyword filtering
    if is_trusted_source:
        # Accept if in operational categories (don't check BLOCKED_KEYWORDS!)
        if threat.category in OPERATIONAL_CATEGORIES:
            return True
        # For GENERAL from trusted: only if has security keywords
        if threat.category == ThreatCategory.GENERAL:
            security_terms = ['cve', 'vulnerability', 'exploit', 'malware', 'breach',
                            'ransomware', 'attack', 'threat', 'compromised', 'exposed',
                            'vulnerable', 'patch', 'fix', 'mitigation', 'detection']
            if any(term in text for term in security_terms):
                return True
        return False

    # NON-TRUSTED SOURCES: Strict filtering - check BLOCKED_KEYWORDS first
    for keyword in BLOCKED_KEYWORDS:
        if keyword.lower() in text:
            return False

    # Must be in operational categories
    if threat.category not in OPERATIONAL_CATEGORIES:
        return False

    # For general category: must have security keywords
    if threat.category == ThreatCategory.GENERAL:
        security_terms = ['cve', 'vulnerability', 'exploit', 'malware', 'breach',
                         'ransomware', 'attack', 'threat', 'compromised', 'exposed',
                         'vulnerable', 'patch', 'fix', 'mitigation', 'detection',
                         'security', 'hack', 'rce', 'exploit', 'vulnerability']
        if not any(term in text for term in security_terms):
            return False

    return True


def filter_operational_threats(threats):
    """Filter list to only operational threats."""
    return [t for t in threats if is_operational_threat(t)]
