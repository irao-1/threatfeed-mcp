# Quick Start Guide

## 5-Minute Setup

### 1. Install

```bash
# Clone and enter
git clone https://github.com/yourusername/threatfeed-mcp.git
cd threatfeed-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize

```bash
# Create database and fetch initial threats
python src/aggregator.py --init
python src/aggregator.py --fetch
```

### 3. Start Dashboard

```bash
python src/dashboard.py
```

Open `http://localhost:8000` in your browser.

---

## Common Tasks

### View Threats from CLI

```bash
# Show statistics
python src/aggregator.py --stats

# Show critical threats
python src/aggregator.py --critical

# Show recent threats
python src/aggregator.py --recent

# Search
python src/aggregator.py --search "kubernetes" --severity high
```

### Run Continuous Aggregation

```bash
# Run in background with hourly updates
python src/aggregator.py --daemon --interval 60
```

To stop: `Ctrl+C`

### Use with Claude

1. Add to `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "threatfeed": {
      "command": "python",
      "args": ["/path/to/threatfeed-mcp/src/mcp_server.py"]
    }
  }
}
```

2. Restart Claude Desktop

3. Ask in Claude:
```
"What critical vulnerabilities were reported today?"
"Show me ransomware alerts from this week"
"Search for Kubernetes CVEs"
```

---

## Architecture

```
┌─ Sources (RSS Feeds)
  └─ Aggregator (Fetch & Process)
     └─ Database (SQLite)
        ├─ CLI Interface
        ├─ Web Dashboard (port 8000)
        └─ MCP Server (Claude Integration)
```

---

## What Each Component Does

| Component | Purpose | Access |
|-----------|---------|--------|
| **Aggregator** | Fetches and processes threats | CLI / Daemon |
| **Database** | Stores threats locally | SQLite file |
| **Dashboard** | Web UI for browsing | http://localhost:8000 |
| **MCP Server** | Claude integration | Claude Desktop |
| **CLI** | Command-line interface | Terminal |

---

## File Structure

```
threatfeed-mcp/
├── src/
│   ├── aggregator.py       # Main aggregator
│   ├── mcp_server.py       # Claude integration
│   ├── dashboard.py        # Web UI
│   ├── models.py           # Data models
│   ├── database.py         # Database layer
│   ├── utils.py            # Utilities
│   └── sources/
│       ├── __init__.py
│       └── rss_sources.py  # RSS feed handlers
├── data/
│   └── threats.db          # SQLite database (created)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── MCP_INTEGRATION.md
│   └── DEPLOYMENT.md
├── config.yaml             # Configuration
├── requirements.txt        # Dependencies
├── README.md
└── LICENSE
```

---

## Data Flow

1. **Aggregator** fetches from RSS feeds
2. **Utils** extract CVEs, score severity, categorize
3. **Database** stores with deduplication
4. **Dashboard/MCP/CLI** query the database

---

## Key Features

✅ **Multi-source aggregation** (HN, Bleeping Computer, Palo Alto, etc.)
✅ **Automatic deduplication** (70% similarity threshold)
✅ **Smart severity scoring** (keyword-based)
✅ **Web dashboard** (real-time threat browsing)
✅ **Claude integration** (MCP server)
✅ **CLI interface** (for power users)
✅ **Scheduled fetching** (hourly/daily)
✅ **Local storage** (no cloud required)

---

## Troubleshooting

### "No data"
```bash
python src/aggregator.py --fetch
python src/aggregator.py --stats
```

### Port already in use
```bash
python src/dashboard.py --port 8001
```

### MCP not showing in Claude
- Check `~/.claude/claude_desktop_config.json` is valid JSON
- Restart Claude Desktop
- Verify Python path: `which python`

### High memory usage
```bash
# Cleanup old data
python -c "from src.database import ThreatDatabase; ThreatDatabase().cleanup_old_threats(30)"
```

---

## Next Steps

1. **Customize sources**: Edit `config.yaml`
2. **Add notifications**: Configure Slack/email in `config.yaml`
3. **Deploy to server**: See `docs/DEPLOYMENT.md`
4. **Integrate with SIEM**: Extend MCP server with custom tools
5. **Scale up**: Switch to PostgreSQL backend

---

## Getting Help

- 📖 [Full Documentation](docs/)
- 🐛 [Issues](https://github.com/yourusername/threatfeed-mcp/issues)
- 💬 [Discussions](https://github.com/yourusername/threatfeed-mcp/discussions)

---

**Ready to monitor threats?** Start with:

```bash
python src/aggregator.py --fetch && python src/dashboard.py
```

Then open http://localhost:8000 🚀
