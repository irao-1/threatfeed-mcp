"""Custom threat intelligence source."""

import requests
from typing import List
from datetime import datetime
from models import Threat
from utils import generate_id, score_severity, categorize_threat, extract_keywords

class CustomSource:
    """Template for custom threat sources."""
    
    def __init__(self, name: str, api_url: str, api_key: str = None):
        self.name = name
        self.api_url = api_url
        self.api_key = api_key
    
    def fetch(self) -> List[Threat]:
        """Fetch threats from custom API."""
        threats = []
        
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse your custom API response here
            for item in data.get('alerts', []):
                threat = Threat(
                    id=generate_id(item.get('url', item.get('id'))),
                    title=item.get('title', 'No title'),
                    description=item.get('description', ''),
                    source=self.name,
                    url=item.get('url', ''),
                    published_date=datetime.fromisoformat(item.get('date', datetime.utcnow().isoformat())),
                    severity=score_severity(item.get('title', ''), item.get('description', '')),
                    category=categorize_threat(item.get('title', ''), item.get('description', '')),
                    keywords=extract_keywords(item.get('title', ''))
                )
                threats.append(threat)
            
            print(f"Got {len(threats)} threats from {self.name}")
            return threats
            
        except Exception as e:
            print(f"Error fetching from {self.name}: {e}")
            return []
