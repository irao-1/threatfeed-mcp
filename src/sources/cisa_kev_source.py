"""CISA Known Exploited Vulnerabilities (KEV) Catalog source."""

import requests
import logging
from typing import List
from datetime import datetime
from models import Threat, ThreatCategory, SeverityLevel
from utils import extract_cves, generate_id, extract_keywords

logger = logging.getLogger(__name__)


class CISAKEVSource:
    """CISA Known Exploited Vulnerabilities - daily updated."""
    
    def __init__(self):
        self.name = "CISA KEV"
        self.url = 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
    
    def fetch(self) -> List[Threat]:
        """Fetch CISA KEV vulnerabilities."""
        threats = []
        
        try:
            logger.info(f"Fetching CISA KEV: {self.url}")
            
            response = requests.get(self.url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # CISA KEV format: vulnerabilities array
            for vuln in data.get('vulnerabilities', []):
                threat = self._parse_kev(vuln)
                if threat:
                    threats.append(threat)
            
            logger.info(f"Got {len(threats)} known exploited vulnerabilities from CISA")
            return threats
            
        except Exception as e:
            logger.error(f"Error fetching CISA KEV: {e}")
            return []
    
    def _parse_kev(self, vuln: dict) -> Threat:
        """Parse CISA KEV vulnerability."""
        try:
            cve_id = vuln.get('cveID', '')
            vendor = vuln.get('vendor', 'Unknown')
            product = vuln.get('product', 'Unknown')
            description = vuln.get('description', 'No description')
            date_added = vuln.get('dateAdded', '')
            
            if not cve_id:
                return None
            
            # Parse date
            pub_date = datetime.utcnow()
            try:
                if date_added:
                    pub_date = datetime.strptime(date_added, '%Y-%m-%d')
            except:
                pass
            
            title = f"[EXPLOITED] {cve_id}: {product} ({vendor})"
            full_desc = f"{description}\n\nStatus: KNOWN EXPLOITED VULNERABILITY\nVendor: {vendor}\nProduct: {product}\nDate Added: {date_added}"
            
            threat_id = generate_id(cve_id)
            
            return Threat(
                id=threat_id,
                title=title,
                description=full_desc,
                source=self.name,
                url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                published_date=pub_date,
                severity=SeverityLevel.CRITICAL,  # All KEV are critical (actively exploited)
                category=ThreatCategory.CVE,
                cves=[cve_id],
                keywords=[vendor.lower(), product.lower(), 'exploited', 'known'],
                confidence_score=0.99  # CISA data is highly reliable
            )
            
        except Exception as e:
            logger.debug(f"Error parsing CISA KEV: {e}")
            return None
