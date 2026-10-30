# GitHub Push & Usage - Step by Step

## Part 1: Push Your Code to GitHub (10 minutes)

### Step 1: Copy All Files to Your Computer

All files are currently in a temporary work folder. You need to:

**Option A: Copy Everything Here** (if you want it on your Mac)
```bash
# On your Mac, create a folder for the project
mkdir ~/threatfeed-mcp
cd ~/threatfeed-mcp

# Then copy all the files from the outputs folder
# (The path from the system: /Users/aishwarya.rao/Library/Application Support/Claude-3p/local-agent-mode-sessions/f45875f2/00000000/495371cf/outputs/)
```

Or just reference them directly from where they are.

### Step 2: Initialize Git

```bash
# Go to your project folder
cd ~/threatfeed-mcp

# Initialize git repo
git init

# Add all files
git add .

# Make first commit
git commit -m "Initial commit: ThreatFeed - Threat Intelligence Aggregator with MCP/Claude integration"
```

### Step 3: Connect to Your GitHub Repo

```bash
# Replace YOUR_USERNAME with your GitHub username
# Replace YOUR_REPO with your repo name (e.g., threatfeed-mcp)

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Set main branch
git branch -M main

# Push everything to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/aishwarya-rao/threatfeed-mcp.git
git branch -M main
git push -u origin main
```

### Step 4: Verify on GitHub

1. Go to https://github.com/YOUR_USERNAME/YOUR_REPO
2. You should see all files there
3. README.md should display automatically

---

## Part 2: Use It Locally (First Time)

### Step 1: Clone from GitHub to Your Computer

```bash
# Go to home folder
cd ~

# Clone your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Go into the folder
cd YOUR_REPO
```

### Step 2: Run Setup Script (Automatic)

```bash
# Make it executable
chmod +x setup.sh

# Run it
./setup.sh
```

**This does automatically:**
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Creates database
- ✅ Fetches initial threats
- ✅ Shows statistics

### Step 3: Choose What to Run

#### Option A: Web Dashboard (Best for first time)

```bash
python src/dashboard.py
```

Then:
1. Open your browser
2. Go to: http://localhost:8000
3. See live threat feeds
4. Search and filter threats

**Dashboard Features:**
- Real-time threat browsing
- Search by keyword
- Filter by severity (critical, high, medium, low)
- Filter by category (CVE, malware, ransomware, etc.)
- Dark theme
- Auto-refresh every 5 minutes

#### Option B: Run as Background Daemon

```bash
python src/aggregator.py --daemon --interval 60 &
```

This:
- ✅ Fetches threats every hour
- ✅ Runs in background
- ✅ Stores in local database
- ✅ Keep running forever (until you stop it)

To check what's been collected:
```bash
python src/aggregator.py --stats
```

#### Option C: Use CLI Commands

```bash
# Show recent threats
python src/aggregator.py --recent

# Show only critical threats
python src/aggregator.py --critical

# Search for something
python src/aggregator.py --search "kubernetes" --severity high

# Show statistics
python src/aggregator.py --stats
```

#### Option D: Use with Claude

1. Edit file: `~/.claude/claude_desktop_config.json`

2. Add this section (if not already there):
```json
{
  "mcpServers": {
    "threatfeed": {
      "command": "python",
      "args": ["/Users/YOUR_USERNAME/threatfeed-mcp/src/mcp_server.py"]
    }
  }
}
```

3. Replace `/Users/YOUR_USERNAME` with your actual home path

4. Restart Claude Desktop

5. Now in Claude you can ask:
```
"What are the critical vulnerabilities from today?"
"Show me ransomware alerts"
"Search for Kubernetes CVEs"
"What's the threat landscape summary?"
```

---

## Part 3: Common Tasks After Setup

### Daily: Check Threats

```bash
# Option 1: Web dashboard
python src/dashboard.py

# Option 2: Command line
python src/aggregator.py --recent

# Option 3: Ask Claude
# (if you set up MCP server)
```

### Setup as Automatic Service (runs 24/7)

```bash
# macOS - using launchd
mkdir -p ~/Library/LaunchAgents

# Create file: ~/Library/LaunchAgents/com.threatfeed.plist
# (see docs/DEPLOYMENT.md for exact plist content)

# Or on Linux - using systemd
sudo cp threatfeed.service /etc/systemd/system/
sudo systemctl start threatfeed
sudo systemctl status threatfeed
```

### Customize Sources

Edit `config.yaml` to:
- Add new RSS feeds
- Change update frequency
- Adjust retention (how long to keep old threats)
- Enable/disable sources

### Export Data

```bash
# Export to JSON
sqlite3 data/threats.db \
  "SELECT json_object('id', id, 'title', title, 'severity', severity) FROM threats" \
  > threats.json

# Or use Python to export
python -c "
from src.database import ThreatDatabase
db = ThreatDatabase()
threats = db.get_recent_threats(limit=100)
for t in threats:
    print(f'{t.severity}: {t.title}')
"
```

---

## Part 4: Update Code from GitHub

If you make changes locally and want to push them:

```bash
# Make your changes
# ... edit files ...

# Check what changed
git status

# Add changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push
```

To pull latest changes from GitHub:

```bash
git pull origin main
```

---

## Part 5: Troubleshooting

### "Setup.sh doesn't work"

```bash
# Make sure it's executable
chmod +x setup.sh

# Run it with bash explicitly
bash setup.sh

# If still fails, do manual setup:
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/aggregator.py --init
python src/aggregator.py --fetch
```

### "Port 8000 already in use"

```bash
# Use different port
python src/dashboard.py --port 8001
# Then open http://localhost:8001
```

### "No threats showing"

```bash
# Force a fresh fetch
python src/aggregator.py --fetch

# Check database
python src/aggregator.py --stats

# If still empty, check internet connection
```

### "Claude not seeing MCP tools"

```bash
# 1. Check config file is valid JSON
cat ~/.claude/claude_desktop_config.json | python -m json.tool

# 2. Verify path is correct
ls /Users/YOUR_USERNAME/threatfeed-mcp/src/mcp_server.py

# 3. Restart Claude Desktop completely
# 4. Test locally first
python src/mcp_server.py --interactive
# Type: get_recent_threats
```

---

## Quick Commands Reference

```bash
# Setup
./setup.sh

# Run web dashboard
python src/dashboard.py

# Run daemon (background)
python src/aggregator.py --daemon --interval 60 &

# Check what threats we have
python src/aggregator.py --stats

# See recent threats
python src/aggregator.py --recent

# Search threats
python src/aggregator.py --search "CVE"

# Update from GitHub
git pull origin main

# Push your changes to GitHub
git add . && git commit -m "message" && git push
```

---

## The Complete Flow

```
1. Push Code to GitHub
   git push -u origin main

2. Clone to Your Computer
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git

3. Run Setup
   ./setup.sh

4. Choose Interface
   ├─ Web Dashboard: python src/dashboard.py
   ├─ CLI: python src/aggregator.py --recent
   ├─ Claude: (after MCP setup)
   └─ Daemon: python src/aggregator.py --daemon &

5. Keep Using It
   ├─ Add new threats (automatic hourly)
   ├─ Browse/search threats
   ├─ Get threat briefings
   └─ Integrate with your workflow
```

---

## Start Now!

### First time? Do this:

```bash
# 1. Clone from GitHub
git clone https://github.com/YOUR_USERNAME/threatfeed-mcp.git
cd threatfeed-mcp

# 2. Setup (takes ~2-3 minutes)
./setup.sh

# 3. Run dashboard
python src/dashboard.py

# 4. Open browser
# Visit: http://localhost:8000
```

### Then explore:

- 🌐 Web interface at localhost:8000
- 💻 CLI with `python src/aggregator.py --recent`
- 🧠 Claude integration after MCP setup

**That's it! You're monitoring threats now.** 🛡️

---

## Need Help?

- 📖 **QUICKSTART.md** - Quick setup guide
- 📊 **PROJECT_SUMMARY.md** - Full feature list
- 🏗️ **docs/ARCHITECTURE.md** - How it works
- 🚀 **docs/DEPLOYMENT.md** - Advanced setup
- 🧠 **docs/MCP_INTEGRATION.md** - Claude setup
