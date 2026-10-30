# Setup ThreatFeed on Mac Desktop - Easy Way

## Problem Solved ✅

You can now:
1. ✅ Get the project as a ZIP file
2. ✅ Put it on your Desktop (easy to find)
3. ✅ Change the path to wherever you want
4. ✅ Use it from any location

---

## Step-by-Step Guide

### Step 1: Download ZIP File to Desktop

The ZIP file `threatfeed-mcp.zip` contains everything you need.

**Save it to your Desktop:**
- Look for: `threatfeed-mcp.zip`
- Save to: `~/Desktop/`

Or on Mac:
```bash
# Open Finder → Desktop
# Drag the zip file there
```

### Step 2: Extract the ZIP

**Double-click the ZIP file** and it will extract automatically, OR use Terminal:

```bash
cd ~/Desktop
unzip threatfeed-mcp.zip
# This creates folder: ~/Desktop/threatfeed-mcp
```

### Step 3: Go to the Project Folder

```bash
cd ~/Desktop/threatfeed-mcp
```

Now you can see all files with:
```bash
ls -la
```

### Step 4: Run Setup (One Command)

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Create Python environment
- ✅ Install all dependencies
- ✅ Create database
- ✅ Fetch initial threats
- ✅ Show statistics

---

## Option A: Keep on Desktop

```bash
cd ~/Desktop/threatfeed-mcp
python src/dashboard.py
```

---

## Option B: Move to Documents Folder

```bash
# Move from Desktop to Documents
mv ~/Desktop/threatfeed-mcp ~/Documents/threatfeed-mcp

# Go to it
cd ~/Documents/threatfeed-mcp

# Run setup
./setup.sh
```

---

## Option C: Move to Custom Path

```bash
# Move to any folder you want
mv ~/Desktop/threatfeed-mcp /path/to/your/folder/threatfeed-mcp

# Or create a new folder
mkdir -p ~/projects/security
mv ~/Desktop/threatfeed-mcp ~/projects/security/

# Go to it
cd ~/projects/security/threatfeed-mcp

# Run setup
./setup.sh
```

---

## Option D: Use Environment Variable (Advanced)

Set a permanent location:

```bash
# Add to ~/.bash_profile or ~/.zshrc
export THREATFEED_HOME="$HOME/projects/threatfeed-mcp"

# Then use it
cd $THREATFEED_HOME
python src/dashboard.py
```

---

## Quick Start from Desktop

### First Time Setup

```bash
# 1. Go to Desktop
cd ~/Desktop/threatfeed-mcp

# 2. Setup (automatic)
./setup.sh

# 3. Run dashboard
python src/dashboard.py

# 4. Open browser → http://localhost:8000
```

### Every Day After

```bash
# Option 1: Web dashboard
cd ~/Desktop/threatfeed-mcp
python src/dashboard.py

# Option 2: Just check recent threats
cd ~/Desktop/threatfeed-mcp
python src/aggregator.py --recent

# Option 3: Search something
cd ~/Desktop/threatfeed-mcp
python src/aggregator.py --search "kubernetes" --severity high
```

---

## Make It Super Easy with Aliases

Add these to your Mac terminal (~/.zshrc if you use zsh, ~/.bash_profile if bash):

```bash
# Add these lines to your shell config file
alias threatfeed='cd ~/Desktop/threatfeed-mcp'
alias threatfeed-dashboard='cd ~/Desktop/threatfeed-mcp && python src/dashboard.py'
alias threatfeed-recent='cd ~/Desktop/threatfeed-mcp && python src/aggregator.py --recent'
alias threatfeed-critical='cd ~/Desktop/threatfeed-mcp && python src/aggregator.py --critical'
alias threatfeed-daemon='cd ~/Desktop/threatfeed-mcp && python src/aggregator.py --daemon &'
```

Then just type:
```bash
threatfeed                   # Go to folder
threatfeed-dashboard        # Start web dashboard
threatfeed-recent           # See recent threats
threatfeed-critical         # See critical threats
threatfeed-daemon           # Run in background
```

---

## Find Your Path

On Mac, you can find where things are:

```bash
# See where you are right now
pwd

# See Desktop path
echo ~/Desktop

# See Documents path
echo ~/Documents

# See home folder
echo ~

# List what's on Desktop
ls ~/Desktop/
```

---

## GitHub Integration from Desktop

### Push to GitHub

```bash
cd ~/Desktop/threatfeed-mcp

git init
git add .
git commit -m "ThreatFeed threat intelligence aggregator"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Pull from GitHub

```bash
cd ~/Desktop
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
./setup.sh
```

---

## File Structure After Extract

After extracting ZIP to Desktop, you'll have:

```
~/Desktop/threatfeed-mcp/
├── src/                    ← Application code
│   ├── aggregator.py       
│   ├── dashboard.py        
│   ├── mcp_server.py       
│   └── ...
├── docs/                   ← Documentation
├── data/                   ← Database (created after setup)
├── setup.sh                ← Run this first
├── main.py                 
├── config.yaml             
├── requirements.txt        
├── README.md               
└── ...
```

---

## Verify It's Working

After setup, check:

```bash
cd ~/Desktop/threatfeed-mcp

# Show statistics
python src/aggregator.py --stats

# Should show:
# Total unique threats: XXX
# Threats this week: XXX
# By Severity: critical (X), high (X), ...
```

---

## Move It Anytime

You can move the whole folder anytime:

```bash
# Current location
cd ~/Desktop/threatfeed-mcp

# Move to Documents
mv ~/Desktop/threatfeed-mcp ~/Documents/

# Go to new location
cd ~/Documents/threatfeed-mcp

# Still works!
python src/dashboard.py
```

---

## Backup Your Work

```bash
# Create a backup copy on Desktop
cp ~/Desktop/threatfeed-mcp ~/Desktop/threatfeed-mcp.backup

# Or zip it for saving
cd ~/Desktop
zip -r threatfeed-mcp-backup.zip threatfeed-mcp/
```

---

## Uninstall/Clean Up

```bash
# Just delete the folder if you don't want it anymore
rm -rf ~/Desktop/threatfeed-mcp

# Or move to Trash
mv ~/Desktop/threatfeed-mcp ~/.Trash/
```

---

## Summary

✅ ZIP file → Extract to Desktop  
✅ Run `./setup.sh` once  
✅ Use `python src/dashboard.py` to start  
✅ Open http://localhost:8000  
✅ Can move folder anytime  
✅ Can push to GitHub anytime  

**That's it!** 🎉
