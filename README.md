# 🛡️ ThreatFeed

**Real-time threat intelligence aggregator** that monitors multiple security sources, filters for operational threats, and provides web dashboard, CLI, and optional MCP interfaces.

---

## ✨ What It Does

ThreatFeed automatically:
- 🌐 Monitors **4+ security sources** (Bleeping Computer, HackerNews, Reddit, SecurityWeek, CISA KEV)
- 🔍 **Filters noise** - removes business news, keeps security threats only
- 📊 **Scores severity** - automatically categorizes threats as critical/high/medium/low
- 💾 **Stores locally** - 100% local SQLite database, no cloud
- 📱 **3 interfaces** - web dashboard, CLI commands, MCP for Claude
- ⏰ **24/7 monitoring** - automatic hourly threat fetching

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

## 📚 Full Documentation

For detailed information:

- **Setup & Installation** → `LOCAL_DOCS/GET_ZIP_TO_DESKTOP.md`
- **All Commands** → `LOCAL_DOCS/WHAT_IS_THREATFEED.md`
- **Using Without Claude** → `LOCAL_DOCS/WITHOUT_CLAUDE.md`
- **Security Guidelines** → `LOCAL_DOCS/SECURITY_GUIDE.md`
- **Platform Support** → `LOCAL_DOCS/PLATFORM_INDEPENDENCE.md`
- **Testing Guide** → `LOCAL_DOCS/TERMINAL_TESTING_GUIDE.md`
- **Example Outputs** → `LOCAL_DOCS/EXAMPLE_OUTPUTS.md`

---

## 🛡️ Security

✅ **Safe by Design:**
- No code injection vulnerabilities
- No SQL injection
- Local storage only
- HTTPS-only feeds
- Trusted sources only

✅ **Repository Protected:**
- Branch protection enabled
- Dependabot alerts active
- Secret scanning enabled

---

## 🌍 Platform Support

- ✅ **Mac** - Fully supported
- ✅ **Linux** - Fully supported  
- ✅ **Windows** - Supported with WSL2

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

For more help, check `LOCAL_DOCS/TERMINAL_TESTING_GUIDE.md`

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🤝 Contributing

Contributions welcome! Please review security guidelines in `LOCAL_DOCS/SECURITY_GUIDE.md`

---

## 🎯 Ready to Start?

```bash
./setup.sh && python src/dashboard.py
```

Then open: **http://localhost:8000** 🚀

---

**Questions?** Check the docs in `LOCAL_DOCS/` folder
