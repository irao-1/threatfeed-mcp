"""Web dashboard for threat intelligence."""

import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from aggregator import ThreatAggregator
from threat_filter import filter_operational_threats
from models import SeverityLevel, ThreatCategory, SearchQuery

# Initialize FastAPI app
app = FastAPI(title="ThreatFeed Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize aggregator
agg = ThreatAggregator()


# Pydantic models for API
class SearchRequest(BaseModel):
    keywords: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    source: Optional[str] = None
    days: int = 7
    limit: int = 25
    page: int = 1


class ThreatResponse(BaseModel):
    id: str
    title: str
    description: str
    source: str
    url: str
    published_date: str
    severity: str
    category: str
    cves: List[str]
    keywords: List[str]


# API Routes
@app.get("/api/threats/recent")
async def get_recent_threats(days: int = 7, limit: int = 25, page: int = 1, source: Optional[str] = None):
    """Get recent threats with pagination and source filter (operational only)."""
    all_threats = agg.get_recent_threats(limit=limit*4, days=days)
    threats = filter_operational_threats(all_threats)

    # Filter by source if provided
    if source:
        threats = [t for t in threats if t.source == source]

    # Calculate pagination
    offset = (page - 1) * limit
    paginated_threats = threats[offset:offset + limit]

    return {
        "count": len(paginated_threats),
        "total": len(threats),
        "page": page,
        "limit": limit,
        "pages": (len(threats) + limit - 1) // limit if threats else 1,
        "threats": [t.to_dict() for t in paginated_threats]
    }


@app.get("/api/threats/critical")
async def get_critical_threats(limit: int = 25, page: int = 1, source: Optional[str] = None):
    """Get critical threats with pagination and source filter (operational only)."""
    all_threats = agg.get_critical_threats(limit=limit*4)
    threats = filter_operational_threats(all_threats)

    # Filter by source if provided
    if source:
        threats = [t for t in threats if t.source == source]

    # Calculate pagination
    offset = (page - 1) * limit
    paginated_threats = threats[offset:offset + limit]

    return {
        "count": len(paginated_threats),
        "total": len(threats),
        "page": page,
        "limit": limit,
        "pages": (len(threats) + limit - 1) // limit if threats else 1,
        "threats": [t.to_dict() for t in paginated_threats]
    }


@app.post("/api/threats/search")
async def search_threats(request: SearchRequest):
    """Search threats."""
    try:
        severity = SeverityLevel(request.severity) if request.severity else None
        category = ThreatCategory(request.category) if request.category else None

        query = SearchQuery(
            keywords=request.keywords,
            severity=severity,
            category=category,
            source=request.source,
            days_back=int(request.days),
            limit=request.limit
        )

        all_threats = agg.db.search_threats(query)
        threats = filter_operational_threats(all_threats)
        return {
            "count": len(threats),
            "threats": [t.to_dict() for t in threats]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """Get threat statistics."""
    stats = agg.get_stats()
    return {
        "total_threats": stats.total_threats,
        "threats_this_week": stats.threats_this_week,
        "threats_this_month": stats.threats_this_month,
        "by_severity": stats.by_severity,
        "by_category": stats.by_category,
        "by_source": stats.by_source,
        "last_fetch": stats.last_fetch.isoformat()
    }


@app.get("/api/sources")
async def get_sources():
    """Get all threat sources."""
    stats = agg.get_stats()
    return {
        "sources": list(stats.by_source.keys())
    }


@app.get("/api/threats/{threat_id}")
async def get_threat(threat_id: str):
    """Get a specific threat."""
    threat = agg.db.get_threat(threat_id)
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat.to_dict()


@app.post("/api/fetch")
async def trigger_fetch():
    """Trigger a manual fetch."""
    result = agg.fetch_threats()
    return {
        "source": result.source,
        "threats_found": result.threats_found,
        "threats_new": result.threats_new,
        "threats_duplicate": result.threats_duplicate,
        "errors": result.errors
    }


# Health check
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# HTML Dashboard
@app.get("/", response_class=HTMLResponse)
async def index():
    """Main dashboard page."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ThreatFeed Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: #0a0e27;
            color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
        }

        header {
            background: #1a1f3a;
            border-bottom: 2px solid #ff4757;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }

        h1 {
            color: #ff4757;
            font-size: 28px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: #1a1f3a;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }

        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #ff4757;
            margin: 10px 0;
        }

        .stat-label {
            color: #a0a0a0;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .controls {
            background: #1a1f3a;
            border: 1px solid #2a3f5f;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }

        input, select, button {
            background: #0a0e27;
            border: 1px solid #2a3f5f;
            color: #e0e0e0;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #ff4757;
            box-shadow: 0 0 5px rgba(255, 71, 87, 0.3);
        }

        button {
            background: #ff4757;
            color: white;
            border: none;
            font-weight: 600;
            cursor: pointer;
        }

        button:hover {
            background: #ff6b7a;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 71, 87, 0.3);
        }

        .threats-container {
            display: grid;
            gap: 15px;
        }

        .threat-item {
            background: #1a1f3a;
            border-left: 4px solid;
            border-radius: 4px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .threat-item:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
        }

        .threat-item.critical {
            border-left-color: #ff4757;
            background: rgba(255, 71, 87, 0.05);
        }

        .threat-item.high {
            border-left-color: #ffa502;
            background: rgba(255, 165, 2, 0.05);
        }

        .threat-item.medium {
            border-left-color: #ffd93d;
            background: rgba(255, 217, 61, 0.05);
        }

        .threat-item.low {
            border-left-color: #6bcf7f;
            background: rgba(107, 207, 127, 0.05);
        }

        .threat-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
            gap: 15px;
        }

        .threat-title {
            font-size: 16px;
            font-weight: 600;
            color: #fff;
            flex: 1;
        }

        .threat-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .severity-critical {
            background: rgba(255, 71, 87, 0.3);
            color: #ff4757;
        }

        .severity-high {
            background: rgba(255, 165, 2, 0.3);
            color: #ffa502;
        }

        .severity-medium {
            background: rgba(255, 217, 61, 0.3);
            color: #ffd93d;
        }

        .severity-low {
            background: rgba(107, 207, 127, 0.3);
            color: #6bcf7f;
        }

        .threat-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
            flex-wrap: wrap;
            font-size: 13px;
            color: #a0a0a0;
        }

        .threat-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .threat-description {
            font-size: 14px;
            color: #c0c0c0;
            margin-bottom: 10px;
            line-height: 1.5;
        }

        .threat-cves {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }

        .cve-tag {
            background: #2a3f5f;
            color: #6bcf7f;
            padding: 4px 10px;
            border-radius: 3px;
            font-size: 12px;
            font-family: monospace;
        }

        .threat-url {
            display: inline-block;
            color: #4a9eff;
            text-decoration: none;
            font-size: 13px;
            word-break: break-all;
        }

        .threat-url:hover {
            text-decoration: underline;
        }

        .loading {
            text-align: center;
            color: #a0a0a0;
            padding: 40px;
        }

        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #2a3f5f;
            border-top-color: #ff4757;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .no-data {
            text-align: center;
            color: #a0a0a0;
            padding: 40px;
            font-style: italic;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #2a3f5f;
        }

        .tab-btn {
            background: none;
            border: none;
            color: #a0a0a0;
            padding: 10px 20px;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s;
        }

        .tab-btn.active {
            color: #ff4757;
            border-bottom-color: #ff4757;
        }

        .tab-btn:hover {
            color: #e0e0e0;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        footer {
            text-align: center;
            color: #666;
            padding: 20px;
            border-top: 1px solid #2a3f5f;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <header>
        <h1>🛡️ ThreatFeed Intelligence Dashboard</h1>
    </header>

    <div class="container">
        <div class="stats-grid" id="statsGrid">
            <div class="loading"><div class="spinner"></div></div>
        </div>

        <div class="controls">
            <input type="text" id="searchInput" placeholder="Search threats...">
            <select id="severityFilter">
                <option value="">All Severities</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
            </select>
            <select id="categoryFilter">
                <option value="">All Categories</option>
                <option value="cve">CVE</option>
                <option value="malware">Malware</option>
                <option value="breach">Breach</option>
                <option value="ransomware">Ransomware</option>
            </select>
            <select id="sourceFilter">
                <option value="">All Sources</option>
            </select>
            <select id="daysFilter">
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
            </select>
            <button onclick="search()">Search</button>
            <button onclick="fetchLatest()">🔄 Fetch Latest</button>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('recent')">Recent Threats</button>
            <button class="tab-btn" onclick="switchTab('critical')">Critical Only</button>
        </div>

        <div id="recentTab" class="tab-content active">
            <div id="threatsContainer" class="threats-container">
                <div class="loading"><div class="spinner"></div></div>
            </div>
            <div id="paginationRecent" style="display:none; margin-top:20px; text-align:center; color:#a0a0a0;">
                <button onclick="previousPage('recent')" style="margin-right:10px;">← Previous</button>
                <span id="pageInfoRecent">Page 1</span>
                <button onclick="nextPage('recent')" style="margin-left:10px;">Next →</button>
            </div>
        </div>

        <div id="criticalTab" class="tab-content">
            <div id="criticalContainer" class="threats-container">
                <div class="loading"><div class="spinner"></div></div>
            </div>
            <div id="paginationCritical" style="display:none; margin-top:20px; text-align:center; color:#a0a0a0;">
                <button onclick="previousPage('critical')" style="margin-right:10px;">← Previous</button>
                <span id="pageInfoCritical">Page 1</span>
                <button onclick="nextPage('critical')" style="margin-left:10px;">Next →</button>
            </div>
        </div>
    </div>

    <footer>
        ThreatFeed v1.0 | Last updated: <span id="lastUpdate">-</span>
    </footer>

    <script>
        // Pagination state
        let currentPage = { recent: 1, critical: 1 };
        let totalPages = { recent: 1, critical: 1 };

        // Load statistics and sources
        async function loadStats() {
            try {
                const response = await fetch('/api/statistics');
                const data = await response.json();

                document.getElementById('statsGrid').innerHTML = `
                    <div class="stat-card">
                        <div class="stat-label">Total Threats</div>
                        <div class="stat-value">${data.total_threats}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">This Week</div>
                        <div class="stat-value">${data.threats_this_week}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">This Month</div>
                        <div class="stat-value">${data.threats_this_month}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Critical</div>
                        <div class="stat-value">${data.by_severity.critical || 0}</div>
                    </div>
                `;

                document.getElementById('lastUpdate').innerText = new Date(data.last_fetch).toLocaleString();

                // Load sources for filter
                const sourcesResponse = await fetch('/api/sources');
                const sourcesData = await sourcesResponse.json();
                const sourceSelect = document.getElementById('sourceFilter');
                sourcesData.sources.forEach(source => {
                    const option = document.createElement('option');
                    option.value = source;
                    option.textContent = source;
                    sourceSelect.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Load recent threats
        async function loadRecent() {
            try {
                const days = document.getElementById('daysFilter').value || 7;
                const source = document.getElementById('sourceFilter').value;
                let url = `/api/threats/recent?days=${days}&limit=25&page=${currentPage.recent}`;
                if (source) url += `&source=${encodeURIComponent(source)}`;

                const response = await fetch(url);
                const data = await response.json();
                displayThreats(data.threats, 'threatsContainer');

                totalPages.recent = data.pages || 1;
                updatePagination('recent');
            } catch (error) {
                console.error('Error loading recent threats:', error);
                document.getElementById('threatsContainer').innerHTML = '<div class="no-data">Error loading threats</div>';
            }
        }

        // Load critical threats
        async function loadCritical() {
            try {
                const source = document.getElementById('sourceFilter').value;
                let url = `/api/threats/critical?limit=25&page=${currentPage.critical}`;
                if (source) url += `&source=${encodeURIComponent(source)}`;

                const response = await fetch(url);
                const data = await response.json();
                displayThreats(data.threats, 'criticalContainer');

                totalPages.critical = data.pages || 1;
                updatePagination('critical');
            } catch (error) {
                console.error('Error loading critical threats:', error);
                document.getElementById('criticalContainer').innerHTML = '<div class="no-data">Error loading threats</div>';
            }
        }

        // Display threats
        function displayThreats(threats, containerId) {
            const container = document.getElementById(containerId);

            if (!threats || threats.length === 0) {
                container.innerHTML = '<div class="no-data">No threats found</div>';
                return;
            }

            container.innerHTML = threats.map(threat => `
                <div class="threat-item ${threat.severity}">
                    <div class="threat-header">
                        <div class="threat-title">${escapeHtml(threat.title)}</div>
                        <span class="threat-badge severity-${threat.severity}">${threat.severity}</span>
                    </div>
                    <div class="threat-meta">
                        <span>📍 ${escapeHtml(threat.source)}</span>
                        <span>📂 ${threat.category}</span>
                        <span>🕐 ${formatDate(threat.published_date)}</span>
                    </div>
                    ${threat.cves.length > 0 ? `
                        <div class="threat-cves">
                            ${threat.cves.map(cve => `<span class="cve-tag">${cve}</span>`).join('')}
                        </div>
                    ` : ''}
                    <div class="threat-description">${escapeHtml(threat.description)}</div>
                    <a href="${threat.url}" target="_blank" class="threat-url">Read more →</a>
                </div>
            `).join('');
        }

        // Search
        async function search() {
            const keywords = document.getElementById('searchInput').value;
            const severity = document.getElementById('severityFilter').value;
            const category = document.getElementById('categoryFilter').value;
            const days = document.getElementById('daysFilter').value;

            document.getElementById('threatsContainer').innerHTML = '<div class="loading"><div class="spinner"></div></div>';

            try {
                const response = await fetch('/api/threats/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        keywords: keywords || null,
                        severity: severity || null,
                        category: category || null,
                        days: parseInt(days) || 7,
                        limit: 50
                    })
                });
                const data = await response.json();
                displayThreats(data.threats, 'threatsContainer');
            } catch (error) {
                console.error('Error searching:', error);
                document.getElementById('threatsContainer').innerHTML = '<div class="no-data">Error searching threats</div>';
            }
        }

        // Fetch latest
        async function fetchLatest() {
            try {
                const button = event.target;
                button.disabled = true;
                button.innerText = '⏳ Fetching...';

                await fetch('/api/fetch', { method: 'POST' });

                button.innerText = '✓ Done!';
                setTimeout(() => {
                    button.disabled = false;
                    button.innerText = '🔄 Fetch Latest';
                    loadStats();
                    loadRecent();
                    loadCritical();
                }, 1000);
            } catch (error) {
                console.error('Error fetching:', error);
            }
        }

        // Switch tabs
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            document.getElementById(tabName + 'Tab').classList.add('active');
            event.target.classList.add('active');

            if (tabName === 'recent') loadRecent();
            if (tabName === 'critical') loadCritical();
        }

        // Helpers
        function escapeHtml(text) {
            const map = {
                '&': '&amp;', '<': '&lt;', '>': '&gt;',
                '"': '&quot;', "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        function formatDate(dateStr) {
            const date = new Date(dateStr);
            const now = new Date();
            const diff = now - date;
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (hours < 24) return `${hours}h ago`;
            if (days < 7) return `${days}d ago`;
            return date.toLocaleDateString();
        }

        // Pagination helpers
        function updatePagination(tab) {
            const pageInfo = document.getElementById(`pageInfo${tab.charAt(0).toUpperCase() + tab.slice(1)}`);
            const pagination = document.getElementById(`pagination${tab.charAt(0).toUpperCase() + tab.slice(1)}`);

            pageInfo.textContent = `Page ${currentPage[tab]} of ${totalPages[tab]}`;
            pagination.style.display = totalPages[tab] > 1 ? 'block' : 'none';
        }

        function nextPage(tab) {
            if (currentPage[tab] < totalPages[tab]) {
                currentPage[tab]++;
                if (tab === 'recent') loadRecent();
                else loadCritical();
            }
        }

        function previousPage(tab) {
            if (currentPage[tab] > 1) {
                currentPage[tab]--;
                if (tab === 'recent') loadRecent();
                else loadCritical();
            }
        }

        // Reset pagination when filters change
        document.getElementById('sourceFilter').addEventListener('change', () => {
            currentPage.recent = 1;
            currentPage.critical = 1;
            loadRecent();
            loadCritical();
        });

        document.getElementById('daysFilter').addEventListener('change', () => {
            currentPage.recent = 1;
            loadRecent();
        });

        // Initial load
        loadStats();
        loadRecent();
        loadCritical();

        // Auto-refresh every 5 minutes
        setInterval(loadStats, 300000);
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
