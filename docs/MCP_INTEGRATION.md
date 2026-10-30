# MCP Integration Guide

## What is MCP?

MCP (Model Context Protocol) allows you to connect Claude with custom tools and data sources. ThreatFeed exposes threat intelligence as MCP tools that Claude can query.

## Setting Up MCP with Claude Desktop

### 1. Install Claude Desktop

Download from [claude.com](https://claude.com)

### 2. Locate Configuration File

The Claude Desktop configuration file is located at:

**macOS/Linux**:
```
~/.claude/claude_desktop_config.json
```

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 3. Add ThreatFeed MCP Server

Edit `claude_desktop_config.json` and add:

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

Replace `/path/to/threatfeed-mcp` with the actual path to your installation.

### 4. Restart Claude Desktop

Close and reopen Claude Desktop. The MCP server will start automatically.

## Available Tools

### 1. get_recent_threats

Get threat intelligence from the last N days.

**Parameters**:
- `days` (int, default: 7) - Days to look back
- `limit` (int, default: 20) - Maximum threats to return

**Example in Claude**:
```
"Show me the last 30 days of threats, top 50"
```

**Response**:
```json
{
  "count": 42,
  "threats": [
    {
      "title": "Critical Kubernetes Vulnerability",
      "source": "Bleeping Computer",
      "severity": "critical",
      "published_date": "2026-10-28T15:30:00",
      "cves": ["CVE-2026-1234"],
      "url": "..."
    }
  ]
}
```

### 2. get_critical_threats

Get only critical severity threats.

**Parameters**:
- `limit` (int, default: 20) - Maximum threats

**Example in Claude**:
```
"What critical vulnerabilities were reported this week?"
```

### 3. search_threats

Flexible threat search with multiple filters.

**Parameters**:
- `keywords` (string) - Search terms
- `severity` (string) - Filter: critical, high, medium, low, info
- `category` (string) - Filter: cve, malware, breach, ransomware, etc.
- `source` (string) - Specific source name
- `days` (int, default: 7) - Days to look back
- `limit` (int, default: 50) - Max results

**Example in Claude**:
```
"Find all ransomware attacks from the last 30 days"
```

**Query sent to MCP**:
```json
{
  "keywords": "ransomware",
  "category": "ransomware",
  "days": 30,
  "limit": 50
}
```

### 4. get_threat_statistics

Get overall threat database statistics.

**Parameters**: None

**Example in Claude**:
```
"What's the threat landscape summary?"
```

**Response**:
```json
{
  "total_threats": 1245,
  "threats_this_week": 142,
  "threats_this_month": 523,
  "by_severity": {
    "critical": 12,
    "high": 45,
    "medium": 98,
    "low": 234,
    "info": 856
  },
  "by_source": {
    "Bleeping Computer": 456,
    "Palo Alto": 234,
    "HackerNews": 555
  },
  "last_fetch": "2026-10-29T10:30:00"
}
```

### 5. get_threats_by_source

Get threats from a specific source.

**Parameters**:
- `source` (string) - Source name
- `limit` (int, default: 50) - Max results

**Example in Claude**:
```
"Show me the latest from Bleeping Computer"
```

### 6. fetch_latest_threats

Trigger a manual fetch of latest threats (useful for fresh data).

**Parameters**: None

**Example in Claude**:
```
"Get the latest threats right now"
```

### 7. get_vulnerabilities

Get CVE and vulnerability-specific threats.

**Parameters**:
- `days` (int, default: 7) - Days to look back
- `limit` (int, default: 20) - Max results

**Example in Claude**:
```
"Show me all vulnerabilities from this week"
```

### 8. get_malware_alerts

Get malware and ransomware alerts.

**Parameters**:
- `days` (int, default: 7) - Days to look back
- `limit` (int, default: 20) - Max results

**Example in Claude**:
```
"Any new malware or ransomware in the last 14 days?"
```

## Using ThreatFeed in Claude

### Example Conversation

**You**: "What are the top critical vulnerabilities?"

**Claude** calls: `get_critical_threats(limit=10)`

**Claude**: "There are currently 12 critical vulnerabilities. The top ones are..."

---

**You**: "Show me CVEs related to Kubernetes from the last month"

**Claude** calls: `search_threats(keywords="Kubernetes", category="cve", days=30, limit=20)`

**Claude**: "Found 5 Kubernetes-related CVEs..."

---

**You**: "Create a security briefing for today's threats"

**Claude** calls: `get_recent_threats(days=1)` and `get_threat_statistics()`

**Claude**: "Here's today's threat briefing..."

### Advanced Usage

**Threat Analysis**:
```
Analyze the threat landscape from the last 30 days.
Show me:
1. Top threats by severity
2. Most targeted areas
3. Emerging patterns
4. Recommendations
```

**Vulnerability Management**:
```
Find all CVEs affecting database systems (MySQL, PostgreSQL, MongoDB)
from the last 90 days and prioritize by severity.
```

**Security Monitoring**:
```
Check for any ransomware incidents from my critical sources
(Bleeping Computer, Palo Alto) in the last 7 days.
```

## Troubleshooting

### MCP Server Not Appearing

**Problem**: Tools not showing in Claude

**Solution**:
1. Check configuration file syntax (valid JSON)
2. Verify Python path is correct
3. Ensure dependencies installed: `pip install -r requirements.txt`
4. Restart Claude Desktop
5. Check logs: `~/.claude/logs/` (if available)

### No Data Returned

**Problem**: Queries return empty results

**Solution**:
1. Run aggregator first: `python src/aggregator.py --fetch`
2. Check database exists: `ls -la data/threats.db`
3. Verify queries: Try `--stats` to see what's in database

### Slow Response

**Problem**: Tools take too long to respond

**Solution**:
1. Reduce `limit` parameter in queries
2. Use specific filters (source, severity) instead of broad searches
3. Check system resources
4. Consider database optimization with PostgreSQL for larger datasets

## Advanced Configuration

### Custom MCP Server Port

If running as a service:

```python
if __name__ == '__main__':
    import subprocess
    subprocess.run(['python', 'src/mcp_server.py', '--port', '8001'])
```

### Environment Variables

```bash
export THREATFEED_DB_PATH=/var/lib/threatfeed/threats.db
export THREATFEED_LOG_LEVEL=DEBUG
python src/mcp_server.py
```

### Rate Limiting

Configure rate limits in your shell script:

```bash
#!/bin/bash
python /path/to/src/mcp_server.py &
SERVER_PID=$!

# Rate limit to 1 fetch per hour
sleep 3600
kill $SERVER_PID
```

## Security Best Practices

1. **Local Deployment**: Run ThreatFeed locally to keep data private
2. **No Auth Required**: MCP runs through Claude, inheriting its security
3. **Data Retention**: Configure cleanup frequency in aggregator
4. **Source Validation**: Only add trusted RSS feeds
5. **Regular Updates**: Keep threat sources current

## Integration with Other Tools

### With Security Workflows

```
Claude → ThreatFeed (threat data) → Your SIEM/EDR
```

### With Notifications

```python
# In aggregator.py, add webhook:
import requests

def notify_critical():
    critical = agg.get_critical_threats(limit=5)
    if critical:
        requests.post('https://your-slack-webhook', json={
            "text": f"Critical threats: {len(critical)}"
        })
```

### With External APIs

Extend MCP server to call other tools:

```python
def correlate_with_shodan(keyword):
    # Query Shodan API
    # Correlate with threats
    return results
```

## Performance Tips

1. **Filter Early**: Use severity/category filters instead of keyword search
2. **Limit Results**: Keep limit < 100 for faster responses
3. **Cache Results**: Claude caches tool responses automatically
4. **Schedule Fetches**: Set aggregator to hourly or daily instead of on-demand

## Next Steps

1. Start aggregator daemon: `python src/aggregator.py --daemon`
2. Test with CLI: `python src/mcp_server.py --interactive`
3. Add to Claude config
4. Query from Claude: "What threats should I know about?"
