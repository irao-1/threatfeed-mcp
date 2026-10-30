# Deployment Guide

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/threatfeed-mcp.git
cd threatfeed-mcp
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

```bash
python src/aggregator.py --init
```

### 5. Fetch Initial Data

```bash
python src/aggregator.py --fetch
```

### 6. View Statistics

```bash
python src/aggregator.py --stats
```

## Running Components

### Command-Line Interface

**Show recent threats**:
```bash
python src/aggregator.py --recent
```

**Show critical threats**:
```bash
python src/aggregator.py --critical
```

**Search for threats**:
```bash
python src/aggregator.py --search "kubernetes" --severity high
```

**View statistics**:
```bash
python src/aggregator.py --stats
```

### Background Daemon

Run with hourly updates:
```bash
python src/aggregator.py --daemon --interval 60
```

This will:
- Fetch threats every hour
- Store in local SQLite database
- Keep running in background
- Auto-cleanup old duplicates daily at 2 AM

To run in persistent background (Linux/macOS):
```bash
nohup python src/aggregator.py --daemon > threatfeed.log 2>&1 &
```

### Web Dashboard

```bash
python src/dashboard.py
```

Then open: `http://localhost:8000`

Features:
- Real-time threat browsing
- Search and filter
- Statistics dashboard
- Manual fetch trigger
- Auto-refresh every 5 minutes

### MCP Server (Claude Integration)

Test in interactive mode:
```bash
python src/mcp_server.py --interactive
```

Commands:
- `get_recent_threats days=7 limit=20`
- `get_critical_threats limit=10`
- `search_threats keywords=CVE severity=high`
- `get_threat_statistics`

For use with Claude Desktop, add to `~/.claude/claude_desktop_config.json`:

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

## Production Deployment

### Linux Systemd Service

Create `/etc/systemd/system/threatfeed.service`:

```ini
[Unit]
Description=ThreatFeed Aggregator
After=network.target

[Service]
Type=simple
User=threatfeed
WorkingDirectory=/opt/threatfeed-mcp
Environment="PATH=/opt/threatfeed-mcp/venv/bin"
ExecStart=/opt/threatfeed-mcp/venv/bin/python src/aggregator.py --daemon --interval 60
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable threatfeed
sudo systemctl start threatfeed
```

Check status:
```bash
sudo systemctl status threatfeed
```

### Dashboard Service

Create `/etc/systemd/system/threatfeed-dashboard.service`:

```ini
[Unit]
Description=ThreatFeed Dashboard
After=network.target threatfeed.service
Requires=threatfeed.service

[Service]
Type=simple
User=threatfeed
WorkingDirectory=/opt/threatfeed-mcp
Environment="PATH=/opt/threatfeed-mcp/venv/bin"
ExecStart=/opt/threatfeed-mcp/venv/bin/python src/dashboard.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/threatfeed`:

```nginx
server {
    listen 80;
    server_name threatfeed.example.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/threatfeed /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### PostgreSQL Backend (Optional)

For large-scale deployments, replace SQLite:

1. Create PostgreSQL database:
```bash
createdb threatfeed
```

2. Update `database.py` to use SQLAlchemy:
```python
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/threatfeed')
```

3. Create tables (add migration system)

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

EXPOSE 8000

CMD ["python", "src/dashboard.py"]
```

Build and run:
```bash
docker build -t threatfeed:latest .
docker run -d -p 8000:8000 -v threatfeed_data:/app/data threatfeed:latest
```

Docker Compose (`docker-compose.yml`):

```yaml
version: '3.8'

services:
  threatfeed:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONUNBUFFERED=1
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=threatfeed
      - POSTGRES_USER=threatfeed
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run: `docker-compose up -d`

## Monitoring & Logging

### Application Logs

Set logging level in `aggregator.py`:
```python
logging.basicConfig(level=logging.DEBUG)
```

View logs:
```bash
tail -f threatfeed.log
```

### Health Checks

```bash
curl http://localhost:8000/api/health
```

Response: `{"status": "ok"}`

### System Monitoring

Monitor disk usage:
```bash
du -sh data/
```

Monitor process:
```bash
ps aux | grep threatfeed
```

### Alerting

Add to systemd service to alert on failure:
```ini
OnFailure=send-email@%n.service
```

## Backup & Recovery

### Database Backup

SQLite:
```bash
cp data/threats.db data/threats.db.backup
```

PostgreSQL:
```bash
pg_dump threatfeed > backup.sql
```

### Schedule Regular Backups

Create `/etc/cron.daily/threatfeed-backup`:

```bash
#!/bin/bash
BACKUP_DIR="/backups/threatfeed"
mkdir -p $BACKUP_DIR
cp /opt/threatfeed-mcp/data/threats.db $BACKUP_DIR/threats.db.$(date +%Y%m%d)
find $BACKUP_DIR -name "*.db.*" -mtime +30 -delete
```

## Performance Tuning

### Database Optimization

Add indices for common queries:
```sql
CREATE INDEX idx_severity_date 
  ON threats(severity, published_date DESC);
```

### Query Optimization

Limit query scope:
```python
# Instead of:
threats = agg.search_threats(keywords="*", limit=10000)

# Use:
threats = agg.search_threats(
    keywords="CVE",
    severity="critical",
    limit=50
)
```

### Resource Allocation

Monitor memory usage:
```bash
watch -n 1 'free -h'
```

Optimize fetch frequency:
- Hourly: Good for active monitoring
- Daily: Good for routine checks
- Weekly: Good for long-term trends

## Troubleshooting

### No Data in Database

```bash
# Check database exists
ls -la data/threats.db

# Verify data
sqlite3 data/threats.db "SELECT COUNT(*) FROM threats;"

# Re-run fetch
python src/aggregator.py --fetch --db data/threats.db
```

### High Memory Usage

```bash
# Reduce retained threats
python -c "from database import ThreatDatabase; db = ThreatDatabase(); db.cleanup_old_threats(days=30)"

# Reduce fetch limit in sources/rss_sources.py
```

### Slow Dashboard

```bash
# Check database statistics
python src/aggregator.py --stats

# Optimize queries
# Reduce results per page in dashboard.py
# Add pagination
```

### MCP Server Won't Connect

```bash
# Test server directly
python src/mcp_server.py --interactive

# Check Claude config JSON syntax
cat ~/.claude/claude_desktop_config.json | python -m json.tool

# Verify Python path
which python
```

## Security Hardening

### File Permissions

```bash
chmod 600 data/threats.db
chmod 755 src/
```

### Network Security

- Run dashboard behind reverse proxy (Nginx)
- Use HTTPS with Let's Encrypt
- Restrict API access by IP if needed

### Data Privacy

- Keep database local by default
- Don't expose raw URLs in logs
- Consider encryption at rest

## Updating ThreatFeed

```bash
cd /opt/threatfeed-mcp
git pull origin main
pip install -r requirements.txt
sudo systemctl restart threatfeed threatfeed-dashboard
```

## Next Steps

1. Choose deployment model (local/cloud)
2. Set up systemd services
3. Configure reverse proxy (optional)
4. Set up monitoring
5. Enable regular backups
6. Test disaster recovery
