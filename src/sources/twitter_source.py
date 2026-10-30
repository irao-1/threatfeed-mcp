"""Twitter/X threat feed source."""

import logging
from typing import List
from datetime import datetime
from models import Threat
from utils import (
    extract_cves, generate_id, score_severity,
    categorize_threat, extract_keywords, calculate_confidence
)

logger = logging.getLogger(__name__)

# Popular security Twitter accounts to monitor
SECURITY_ACCOUNTS = [
    'Talal_Melh',           # Cybersecurity researcher
    'gcluley',              # Graham Cluley
    'SwiftOnSecurity',      # Swift on Security
    'MalwareTechBlog',      # MalwareTech
    'BleepinComputer',      # Bleeping Computer
    'DarkReading',          # Dark Reading
    'SecurityWeek',         # SecurityWeek
    'cisa_gov',             # CISA
    'FBI',                  # FBI
    'NSAGov',               # NSA
]

class TwitterSource:
    """Twitter/X threat intelligence source."""
    
    def __init__(self, api_key=None, api_secret=None):
        """Initialize with Twitter API credentials."""
        self.api_key = api_key
        self.api_secret = api_secret
        self.name = "Twitter/X"
        
    def fetch(self) -> List[Threat]:
        """Fetch threats from Twitter (requires API key)."""
        
        if not self.api_key:
            logger.warning("Twitter API key not configured - skipping")
            return []
        
        threats = []
        
        try:
            import tweepy
            
            # Authenticate
            client = tweepy.Client(bearer_token=self.api_key)
            
            # Search for security-related tweets
            query = "(vulnerability OR breach OR ransomware OR CVE OR malware OR exploit OR APT) -is:retweet"
            
            tweets = client.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'author_id'],
                expansions=['author_id'],
                user_fields=['username']
            )
            
            if not tweets.data:
                logger.info("No tweets found")
                return []
            
            # Convert tweets to threats
            for tweet in tweets.data:
                threat_id = generate_id(f"twitter-{tweet.id}")
                
                severity = score_severity(tweet.text, tweet.text)
                category = categorize_threat(tweet.text, tweet.text)
                cves = extract_cves(tweet.text)
                keywords = extract_keywords(tweet.text)
                
                threat = Threat(
                    id=threat_id,
                    title=tweet.text[:100],
                    description=tweet.text,
                    source="Twitter/X",
                    url=f"https://twitter.com/i/web/status/{tweet.id}",
                    published_date=tweet.created_at,
                    severity=severity,
                    category=category,
                    cves=cves,
                    keywords=keywords,
                    confidence_score=calculate_confidence("Twitter/X", bool(cves), False)
                )
                
                threats.append(threat)
            
            logger.info(f"Got {len(threats)} threats from Twitter")
            return threats
            
        except ImportError:
            logger.error("tweepy not installed - cannot fetch Twitter feeds")
            return []
        except Exception as e:
            logger.error(f"Error fetching Twitter: {e}")
            return []
