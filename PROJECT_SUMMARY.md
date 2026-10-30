# ThreatFeed MCP - Project Summary

## 🎯 Project Overview

**ThreatFeed** is a production-ready threat intelligence aggregator that fetches security news and vulnerabilities from multiple sources, deduplicates them intelligently, and exposes them via three interfaces:

1. **MCP Server** - Claude integration for AI-powered threat analysis
2. **Web Dashboard** - Real-time threat browsing interface
3. **CLI Interface** - Command-line threat querying

---

## 📦 What's Included

### Core System
- ✅ Multi-source RSS feed aggregator
- ✅ Intelligent deduplication (70% similarity threshold)
- ✅ Severity scoring (keyword-based classification)
- ✅ Threat categorization (CVE, malware, breach, etc.)
- ✅ SQLite database with fast indexing
- ✅ Background scheduler (APScheduler)

### Threat Sources
- Palo Alto Networks Security Blog
- Bleeping Computer
- HackerNews (security-focused)
- Reddit communities (expandable)
- CISA Alerts (RSS)
- Extensible architecture for custom sources

### User Interfaces

**1. Web Dashboard** (`src/dashboard.py`)
- Real-time threat browsing
- Search and filter capabilities
- Severity indicators with color coding
- Live statistics dashboard
- Manual fetch trigger
- Auto-refresh every 5 minutes
- Dark theme for security work

**2. MCP Server** (`src/mcp_server.py`)
- 8 Claude-accessible tools
- Semantic search
- Severity/category filtering
- Automatic threat updates
- Confidence scoring

**3. CLI Interface** (`src/aggregator.py`)
- 10+ commands
- Interactive and batch modes
- Export-ready output
- System monitoring

### Data Processing Pipeline

```
RSS Feeds
    ↓
Parse & Normalize
    ↓
Extract CVEs (regex)
    ↓
Score Severity (keywords)
    ↓
Categorize Threat (patterns)
    ↓
Calculate Confidence
    ↓
Deduplication
    ↓
SQLite Storage
    ↓
Query via Dashboard/MCP/CLI
```

---

## 🗂️ Project Structure

```
threatfeed-mcp/
├── src/
│   ├── aggregator.py          ← Main orchestrator (CLI + scheduler)
│   ├── mcp_server.py          ← Claude integration (8 tools)
│   ├── dashboard.py           ← Web UI (FastAPI + Vanilla JS)
│   ├── models.py              ← Data models (Threat, Stats, etc)
│   ├── database.py            ← SQLite layer
│   ├── utils.py               ← Processing utilities
│   └── sources/
│       ├── __init__.py
│       └── rss_sources.py     ← RSS feed handlers
├── data/
│   └── threats.db             ← SQLite database (created)
├── tests/
│   └── test_aggregator.py     ← Unit tests
├── docs/
│   ├── ARCHITECTURE.md        ← System design
│   ├── MCP_INTEGRATION.md     ← Claude setup
│   └── DEPLOYMENT.md          ← Production deployment
├── config.yaml                ← Configuration file
├── requirements.txt           ← Python dependencies
├── setup.sh                   ← Automated setup script
├── main.py                    ← Convenient entry point
├── QUICKSTART.md              ← Quick start guide
├── CONTRIBUTING.md            ← Contribution guidelines
├── README.md                  ← Main documentation
└── LICENSE                    ← MIT License
```

---

## 🚀 Quick Start

### Setup (5 minutes)

```bash
# Clone and install
git clone <your-repo>
cd threatfeed-mcp
./setup.sh  # Automated setup

# Or manual setup:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/aggregator.py --init
python src/aggregator.py --fetch
```

### Running

```bash
# Web Dashboard (recommended for first time)
python src/dashboard.py
# Open http://localhost:8000

# Background daemon
python src/aggregator.py --daemon --interval 60

# CLI interface
python src/aggregator.py --recent
python src/aggregator.py --critical
python src/aggregator.py --stats

# With Claude
# Add to ~/.claude/claude_desktop_config.json
# Restart Claude Desktop
# Ask: "What critical vulnerabilities were reported today?"
```

---

## 📊 Database Schema

### threats table
```sql
id (TEXT PRIMARY KEY)           -- SHA256 hash of URL (first 16 chars)
title (TEXT)                    -- Article title
description (TEXT)             -- Truncated content (500 chars)
source (TEXT)                   -- Source name (indexed)
url (TEXT UNIQUE)               -- Original URL
published_date (TIMESTAMP)      -- Original publication (indexed)
fetched_date (TIMESTAMP)        -- When we fetched it (indexed)
severity (TEXT)                 -- critical/high/medium/low/info (indexed)
category (TEXT)                 -- cve/malware/breach/etc (indexed)
cves (TEXT JSON)                -- Extracted CVE IDs
affected_products (TEXT JSON)   -- Products mentioned
keywords (TEXT JSON)            -- Extracted keywords
is_duplicate (BOOLEAN)          -- Dedup flag
duplicate_of (TEXT)             -- Reference to original
confidence_score (REAL)         -- 0.0-1.0 confidence
```

### fetch_log table
```sql
source (TEXT)
fetch_date (TIMESTAMP)
threats_found (INTEGER)
threats_new (INTEGER)
errors (TEXT JSON)
```

---

## 🔧 MCP Tools Available

| Tool | Purpose | Parameters |
|------|---------|------------|
| `get_recent_threats` | Last N days | days, limit |
| `get_critical_threats` | Critical only | limit |
| `search_threats` | Flexible search | keywords, severity, category, source, days, limit |
| `get_threat_statistics` | Summary stats | - |
| `get_threats_by_source` | By source | source, limit |
| `fetch_latest_threats` | Manual trigger | - |
| `get_vulnerabilities` | CVE-focused | days, limit |
| `get_malware_alerts` | Malware/ransomware | days, limit |

---

## 🎯 Key Features

### Severity Scoring
- **Critical**: Zero-day, RCE, exploit available, spreading
- **High**: Vulnerability, privilege escalation, authenticated
- **Medium**: DoS, crash, information leak
- **Low**: Local only, minor issue
- **Info**: General announcements

### Deduplication
- Exact URL matching
- Content similarity (70% threshold)
- Preserves original references
- Allows duplicate tracking

### Performance
- Indexed database queries (source, severity, category, date)
- Limited result sets (default 50)
- Streamed RSS parsing
- Auto-cleanup of old duplicates (90+ days)

### Security
- Local data storage (no cloud)
- No authentication required
- Input sanitization in dashboard
- HTTPS-ready (reverse proxy compatible)

---

## 📈 Statistics & Monitoring

```bash
# View database statistics
python src/aggregator.py --stats

# Output:
# Total unique threats: 1,245
# Threats this week: 142
# Threats this month: 523
# By Severity: critical (12), high (45), medium (98), low (234), info (856)
# By Source: Bleeping Computer (456), Palo Alto (234), HackerNews (555)
# By Category: CVE (234), malware (45), breach (12), ...
```

---

## 🔄 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   DATA SOURCES                          │
│  (RSS: HN, BC, Palo Alto, CISA, Reddit, etc.)         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              CORE AGGREGATOR                            │
│  ├─ Fetch from sources                                 │
│  ├─ Extract CVEs (regex)                               │
│  ├─ Score severity (keywords)                          │
│  ├─ Categorize threat (patterns)                       │
│  ├─ Calculate confidence                               │
│  └─ Deduplicate & store                                │
└────┬────────────────┬──────────────┬────────────────────┘
     │                │              │
     ▼                ▼              ▼
  ┌─────────┐    ┌─────────┐    ┌──────────┐
  │   CLI   │    │   WEB   │    │   MCP    │
  │Interface│    │Dashboard│    │ Server   │
  │         │    │(Port    │    │(Claude)  │
  │Commands │    │ 8000)   │    │          │
  └─────────┘    └─────────┘    └──────────┘

         ↓            ↓            ↓
     ┌──────────────────────────────────────┐
     │    SQLite Database (Local Storage)    │
     │   ~ 1,000-10,000 threats retained    │
     └──────────────────────────────────────┘
```

---

## 📝 Configuration

Edit `config.yaml` to customize:
- Fetch interval (default: hourly)
- Data retention (default: 90 days)
- Severity keywords
- RSS sources
- Dashboard settings
- MCP server settings
- Notifications (Slack, email)

---

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Test specific module
pytest tests/test_aggregator.py::TestCVEExtraction

# With coverage
pytest --cov=src tests/
```

Test coverage includes:
- CVE extraction
- Severity scoring
- Threat categorization
- Similarity scoring
- Database operations
- Data models

---

## 🚀 Deployment Options

### Local Development
```bash
python src/aggregator.py --daemon &
python src/dashboard.py &
```

### Linux Server (systemd)
```bash
sudo systemctl start threatfeed
sudo systemctl start threatfeed-dashboard
```

### Docker
```bash
docker-compose up -d
```

### Cloud (AWS/GCP/Azure)
- EC2/Compute Engine instance
- CloudSQL/RDS for PostgreSQL
- Load balancer + reverse proxy
- CloudWatch/Stackdriver monitoring

---

## 🔐 Security Considerations

1. **Data Privacy**: All stored locally by default
2. **Source Validation**: HTTPS and SSL verification
3. **Rate Limiting**: Respects source rate limits
4. **Input Sanitization**: HTML escape in dashboard
5. **No External Dependencies**: Data stays private
6. **Simple Deployment**: Single Python app, no microservices

---

## 📚 Documentation

- **README.md** - Main documentation
- **QUICKSTART.md** - 5-minute setup
- **docs/ARCHITECTURE.md** - System design
- **docs/MCP_INTEGRATION.md** - Claude setup
- **docs/DEPLOYMENT.md** - Production deployment
- **CONTRIBUTING.md** - How to contribute

---

## 🛣️ Roadmap

**Phase 1** (Complete):
- ✅ Core aggregator
- ✅ MCP server
- ✅ Web dashboard
- ✅ CLI interface

**Phase 2** (Next):
- [ ] PostgreSQL support
- [ ] GraphQL API
- [ ] Slack/email notifications
- [ ] Advanced analytics

**Phase 3** (Future):
- [ ] Machine learning severity classification
- [ ] Threat correlation engine
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Multi-user support

---

## 📦 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| requests | HTTP requests | 2.31.0 |
| feedparser | RSS parsing | 6.0.10 |
| beautifulsoup4 | HTML parsing | 4.12.2 |
| fastapi | Web framework | 0.104.1 |
| uvicorn | ASGI server | 0.24.0 |
| APScheduler | Task scheduling | 3.10.4 |
| sqlalchemy | ORM (optional) | 2.0.23 |

Total size: ~50MB with dependencies

---

## 💬 Support & Contribution

- 📖 [Full Documentation](docs/)
- 🐛 [GitHub Issues](https://github.com/yourusername/threatfeed-mcp/issues)
- 💭 [GitHub Discussions](https://github.com/yourusername/threatfeed-mcp/discussions)
- 🤝 [Contribute](CONTRIBUTING.md)

---

## 📄 License

MIT License - See LICENSE file

Free to use, modify, and distribute. Perfect for security teams, SOCs, and threat researchers.

---

## 🎉 Ready to Use

**Start monitoring threats right now:**

```bash
./setup.sh
python src/dashboard.py
```

Then open `http://localhost:8000` 🚀

**Questions?** Check the docs or open a discussion!
