# ThreatFeed MCP - Threat Intelligence Aggregator

A comprehensive threat intelligence aggregator that fetches security news and vulnerabilities from multiple sources (Palo Alto, HackerNews, Bleeping Computer, Twitter, Reddit), aggregates them intelligently, and exposes them via an MCP Server for Claude integration, plus a web dashboard for browsing.

## Features

✅ **Multi-Source Aggregation**
- Palo Alto Security Blog
- HackerNews (security-focused)
- Bleeping Computer
- Twitter/X (security accounts)
- Reddit (r/cybersecurity, r/netsec)
- CISA Alerts

✅ **Smart Processing**
- Automatic deduplication across sources
- Severity scoring based on keywords
- Threat categorization (CVE, malware, breach, etc.)
- Caching to avoid duplicate processing

✅ **MCP Server Integration**
- Query threats directly from Claude
- Semantic search across aggregated feeds
- Filter by severity, source, or category
- Real-time threat summaries

✅ **Web Dashboard**
- Visual threat feed browser
- Real-time updates
- Search and filter capabilities
- Dark theme optimized for security work

✅ **Easy Deployment**
- Single Python app with no external dependencies (except requests)
- Runs locally or on any server
- Automatic scheduled updates
- SQLite database (no DB setup needed)

## Quick Start

### Prerequisites
- Python 3.9+
- Git

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/threatfeed-mcp.git
cd threatfeed-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and run first fetch
python src/aggregator.py --init
```

### Run the Aggregator

```bash
# Fetch threats (runs once)
python src/aggregator.py --fetch

# Run with background scheduler (runs indefinitely, fetches every hour)
python src/aggregator.py --daemon

# Run the MCP Server
python src/mcp_server.py

# Run the web dashboard
python src/dashboard.py  # Visit http://localhost:8000
```

## Project Structure

```
threatfeed-mcp/
├── src/
│   ├── aggregator.py          # Core threat aggregator
│   ├── mcp_server.py          # MCP Server implementation
│   ├── dashboard.py           # Web dashboard (FastAPI)
│   ├── sources/               # Feed source scrapers
│   │   ├── rss_sources.py     # RSS feed handlers
│   │   ├── twitter.py         # Twitter/X integration
│   │   └── custom.py          # Custom scrapers
│   ├── models.py              # Data models
│   ├── database.py            # SQLite interactions
│   └── utils.py               # Utilities
├── docs/
│   ├── ARCHITECTURE.md        # System design
│   ├── MCP_INTEGRATION.md     # Claude MCP setup
│   └── DEPLOYMENT.md          # Production deployment
├── tests/
│   ├── test_aggregator.py
│   └── test_sources.py
├── requirements.txt           # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

## Usage Examples

### As an MCP Server (Claude Integration)

Install in Claude by adding to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "threatfeed": {
      "command": "python",
      "args": ["/path/to/src/mcp_server.py"]
    }
  }
}
```

Then in Claude:
```
"What are the top 5 critical vulnerabilities from this week?"
"Show me threats related to Kubernetes"
"Any ransomware alerts from Bleeping Computer today?"
```

### Via Python API

```python
from aggregator import ThreatAggregator

agg = ThreatAggregator()
threats = agg.search("CVE", severity="critical", limit=10)
for threat in threats:
    print(f"{threat.title} - {threat.source} - {threat.severity}")
```

### Web Dashboard

Open `http://localhost:8000` to browse and filter threats in real-time.

## Configuration

Edit `config.yaml` to customize:
- Fetch frequency (default: hourly)
- Data retention (default: 30 days)
- Severity thresholds
- Source preferences
- MCP server port

## Data Privacy

- **Local Storage**: By default, all data is stored locally in `data/threats.db`
- **No External Calls**: Except to fetch from configured sources
- **No Tracking**: Zero analytics or telemetry

## API Reference

See [docs/API.md](docs/API.md) for complete API documentation.

## Contributing

Contributions welcome! Please:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-source`)
3. Commit changes (`git commit -m 'Add support for new threat source'`)
4. Push and open a Pull Request

## Roadmap

- [ ] SQLAlchemy ORM integration
- [ ] PostgreSQL support
- [ ] Slack/email notifications
- [ ] Threat correlation engine
- [ ] Machine learning severity classification
- [ ] GraphQL API
- [ ] Docker compose setup
- [ ] GitHub Actions for automated testing

## License

MIT License - see [LICENSE](LICENSE) file

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issues](https://github.com/yourusername/threatfeed-mcp/issues)
- 💬 Discussions

## Security

⚠️ This tool is for security research and monitoring. Use responsibly and respect rate limits of all data sources.

Last updated: 2026-10-29
