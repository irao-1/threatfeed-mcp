# ThreatFeed Architecture

## System Overview

ThreatFeed is a modular threat intelligence aggregator that fetches, deduplicates, and serves security intelligence from multiple sources. It consists of three main components:

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
│  (RSS Feeds: HN, BC, Palo Alto, CISA, Reddit, etc.)        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              CORE AGGREGATOR                                 │
│  • Fetch from sources                                        │
│  • Deduplication & normalization                            │
│  • Severity scoring & categorization                        │
│  • Database persistence                                     │
└────┬───────────────┬──────────────────┬────────────────────┘
     │               │                  │
     ▼               ▼                  ▼
┌──────────────┐ ┌──────────────┐  ┌──────────────┐
│     MCP      │ │  WEB         │  │  CLI         │
│   SERVER     │ │  DASHBOARD   │  │  INTERFACE   │
│(Claude)      │ │(FastAPI)     │  │              │
└──────────────┘ └──────────────┘  └──────────────┘
```

## Component Architecture

### 1. Data Sources (`sources/rss_sources.py`)

**Responsibility**: Fetch threat intelligence from external sources.

- **RSSSource class**: Generic RSS feed handler
- **Supported sources**:
  - Bleeping Computer (primary security news)
  - Palo Alto Networks (enterprise threats)
  - HackerNews (developer/technical)
  - Reddit communities (community intelligence)
  - CISA alerts (government warnings)

**Features**:
- Parallel fetching capability
- Rate limiting and timeout handling
- Error recovery
- Parse RSS entries into normalized Threat objects

### 2. Core Models (`models.py`)

**Threat Data Model**:
```python
Threat
  ├── Identification
  │   ├── id (SHA256 hash of URL)
  │   ├── url
  │   └── title
  ├── Content
  │   ├── description
  │   ├── published_date
  │   └── source
  ├── Classification
  │   ├── severity (critical/high/medium/low/info)
  │   ├── category (cve/malware/breach/etc)
  │   ├── cves (extracted CVE IDs)
  │   └── keywords
  ├── Metadata
  │   ├── confidence_score
  │   ├── is_duplicate
  │   └── duplicate_of
```

### 3. Utilities (`utils.py`)

**Core Functions**:
- `extract_cves()`: Regex-based CVE extraction
- `score_severity()`: Keyword-based severity classification
- `categorize_threat()`: Categorization engine
- `calculate_confidence()`: Confidence scoring
- `similarity_score()`: Deduplication via text similarity

### 4. Database (`database.py`)

**ThreatDatabase Class**:
- SQLite3 backend (local, no external DB required)
- Schema with indexed fields for fast queries
- Deduplication storage
- Fetch logging

**Key Tables**:
- `threats`: Main threat storage with indices
- `fetch_log`: Historical fetch operations

### 5. Aggregator (`aggregator.py`)

**ThreatAggregator Class**:
- Orchestrates fetching, processing, and storage
- Background scheduler (APScheduler)
- Search/filter capabilities
- Statistics generation

**Modes**:
- **Fetch mode**: Single execution
- **Daemon mode**: Continuous background updates
- **CLI mode**: Interactive querying

### 6. MCP Server (`mcp_server.py`)

**Purpose**: Expose threats as Claude-accessible tools.

**Available Tools**:
- `get_recent_threats`: Last N days
- `get_critical_threats`: Critical severity only
- `search_threats`: Flexible search with filters
- `get_threat_statistics`: Summary stats
- `get_threats_by_source`: Source filtering
- `fetch_latest_threats`: Trigger manual fetch
- `get_vulnerabilities`: CVE-focused
- `get_malware_alerts`: Malware/ransomware

### 7. Web Dashboard (`dashboard.py`)

**Tech Stack**: FastAPI + Vanilla JS

**Features**:
- Real-time threat browsing
- Search/filter UI
- Statistics dashboard
- Source switching
- Manual fetch trigger
- Auto-refresh

**API Endpoints**:
- `GET /api/threats/recent`
- `GET /api/threats/critical`
- `POST /api/threats/search`
- `GET /api/statistics`
- `GET /api/sources`
- `POST /api/fetch`

## Data Flow

### Fetch Pipeline

```
1. Fetch Phase
   ├── Fetch from each source
   ├── Parse RSS entries
   └── Create Threat objects

2. Analysis Phase
   ├── Extract CVEs (regex)
   ├── Score severity (keywords)
   ├── Categorize (pattern matching)
   ├── Calculate confidence
   └── Extract keywords

3. Deduplication Phase
   ├── Check exact ID match
   ├── Check URL uniqueness
   └── Check content similarity

4. Storage Phase
   ├── Save to SQLite
   ├── Log fetch operation
   └── Return statistics
```

## Severity Scoring Algorithm

**Critical** (highest priority):
- Keywords: zero-day, RCE, remote code execution, exploit available
- Conditions: Unauthenticated + widespread

**High**:
- Keywords: vulnerability, privilege escalation, authenticated
- Conditions: Network accessible

**Medium**:
- Keywords: denial of service, crash, information leak

**Low**:
- Keywords: local only, minor

**Info** (default):
- General announcements

## Deduplication Strategy

1. **Exact match**: URL hash uniqueness
2. **Similarity check**: Compare with recent threats
3. **Threshold**: 70% text overlap = duplicate

Benefits:
- Reduces noise
- Preserves original reference
- Allows duplicate tracking

## Performance Considerations

### Database Indexing
- Source, severity, category, published_date, fetched_date
- Enables fast filtering and sorting

### Query Optimization
- Exclude duplicates by default
- Limit result sets (default: 50)
- Optimize for recent trends

### Memory Management
- Stream RSS parsing (not loading entire feed into memory)
- Limit stored description length (500 chars)
- Regular cleanup of old duplicates (90+ days)

## Extensibility

### Adding New Sources

```python
from models import Threat
from sources.rss_sources import RSSSource

class CustomSource(RSSSource):
    def __init__(self):
        super().__init__(
            name="Custom Source",
            url="https://example.com/feed"
        )
    
    def _parse_entry(self, entry):
        # Custom parsing logic
        return threat_object
```

### Adding New Tools to MCP

```python
def new_tool(**kwargs):
    # Implementation
    return MCPToolResponse(success=True, data={...})

TOOLS["new_tool"] = {
    "description": "Tool description",
    "parameters": {...},
    "handler": new_tool
}
```

## Deployment Architecture

### Local Development
```
aggregator.py ──┬─→ SQLite (data/threats.db)
                ├─→ mcp_server.py (stdio mode)
                └─→ dashboard.py (http://localhost:8000)
```

### Production (Cloud)
```
aggregator.py (systemd service)
    ├─→ PostgreSQL (managed database)
    ├─→ mcp_server.py (systemd service)
    ├─→ dashboard.py (gunicorn/nginx)
    └─→ nginx (reverse proxy)
```

## Security Considerations

1. **Data Source Validation**: Verify HTTPS and SSL certificates
2. **Rate Limiting**: Respect source rate limits
3. **Local Storage**: All data stored locally by default
4. **No Auth Required**: Self-contained, runs locally
5. **Input Sanitization**: Escape HTML in dashboard
6. **Content Security**: Validate before indexing

## Monitoring & Observability

**Logging**: Python logging to stdout/files
**Metrics**: Fetch statistics per source
**Health**: `/api/health` endpoint
**Alerting**: Integration points for webhooks

## Future Enhancements

1. GraphQL API
2. Machine learning severity classification
3. Threat correlation engine
4. Slack/email notifications
5. PostgreSQL backend option
6. Docker containerization
7. Kubernetes deployment
8. Advanced analytics dashboard
