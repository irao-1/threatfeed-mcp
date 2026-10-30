# 🛡️ ThreatAtlas

> **Showcase Project** — Reference implementation of a real-time threat intelligence aggregator

**Real-time threat intelligence aggregator** that monitors multiple security sources, filters for operational threats, and provides web dashboard, CLI, and optional MCP interfaces.

[![Status: Showcase](https://img.shields.io/badge/Status-Showcase%20Project-blue?style=flat-square)](CONTRIBUTING.md)
[![Security: Reviewed](https://img.shields.io/badge/Security-Reviewed-green?style=flat-square)](SECURITY.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## ✨ What It Does

ThreatAtlas automatically:
- 🌐 Monitors **7 security sources** (Bleeping Computer, HackerNews, Reddit, SecurityWeek, Unit42, Palo Alto Blog, CISA KEV)
- 🔍 **Smart filtering** - focuses on CVEs, breaches, malware, APTs, and zero-days. Blocks announcements and product news
- 📊 **Severity scoring** - categorizes threats as critical/high/medium/low automatically
- 🏷️ **Threat tags** - highlights CVEs, threat actors, and affected packages for quick scanning
- 💾 **100% local** - SQLite database, zero cloud dependencies
- 📱 **Dashboard + CLI** - web interface and command-line tools
- ⏰ **Always watching** - automatic hourly threat fetching

---

## 🚀 Quick Start

```bash
# Setup (one time)
./setup.sh

# Start web dashboard
python src/dashboard.py
```

Then open: **http://localhost:8000**

---

## 📋 Common Commands

```bash
# View statistics
python src/aggregator.py --stats

# See critical threats
python src/aggregator.py --critical

# Search threats
python src/aggregator.py --search "threat_name" --severity high

# Run web dashboard
python src/dashboard.py

# Run background monitoring (hourly updates)
python src/aggregator.py --daemon --interval 60 &
```

---

## 🔌 Use With Claude (Optional)

Add to `~/.claude/claude_desktop_config.json`:

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

Then ask Claude: *"What are this week's critical CVEs?"*

---

## 🛠️ Configuration

Edit `config.yaml` to customize:
- Database location
- Update interval
- Threat categories
- Dashboard settings

---

## 📦 Requirements

- Python 3.9+
- pip (Python package manager)

Dependencies auto-installed by `setup.sh`

---

## 💬 Features You Get

✅ Web dashboard (real-time browsing)
✅ CLI interface (15+ commands)
✅ Search & filter (by keyword, severity, source, date)
✅ Automatic updates (hourly)
✅ Background daemon (24/7 monitoring)
✅ Local database (SQLite)
✅ Data export (JSON/CSV)
✅ Claude integration (optional MCP)

---

## 🐛 Troubleshooting

**Port 8000 already in use?**
```bash
python src/dashboard.py --port 8001
```

**Missing dependencies?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Database issues?**
```bash
rm data/threats.db
python src/aggregator.py --fetch
```


## 👤 Credits

<sub>🔧 **Conceived, designed, and developed by Ais**

🤖 Claude AI was used as a development assistant for architecture discussions, implementation guidance, debugging, and documentation. Final design decisions, code review, and project direction remained with the author.</sub>

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤖 Built with Claude

This project was developed using [Claude](https://claude.ai) AI. The architecture, filtering logic, dashboard design, and security implementation were all designed and built with AI assistance.

For technical details, security information, and contribution guidelines, see [SECURITY.md](SECURITY.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 🎯 Ready to Start?

```bash
./setup.sh && python src/dashboard.py
```

Then open: **http://localhost:8000** 🚀

---
