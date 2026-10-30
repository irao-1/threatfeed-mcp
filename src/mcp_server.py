"""MCP Server for Threat Intelligence integration with Claude."""

import json
import logging
from datetime import datetime
from typing import Any
import sys

from aggregator import ThreatAggregator
from models import SeverityLevel, ThreatCategory, SearchQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize aggregator
agg = ThreatAggregator()


class MCPToolResponse:
    """Response wrapper for MCP tools."""

    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

    def to_dict(self):
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }

    def to_json(self):
        return json.dumps(self.to_dict(), default=str, indent=2)


# Tool implementations
def get_recent_threats(days: int = 7, limit: int = 20) -> MCPToolResponse:
    """Get recent threats from the aggregator."""
    try:
        threats = agg.get_recent_threats(limit=limit, days=days)
        data = [t.to_dict() for t in threats]
        return MCPToolResponse(
            success=True,
            data={
                "count": len(data),
                "threats": data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_recent_threats: {e}")
        return MCPToolResponse(success=False, error=str(e))


def get_critical_threats(limit: int = 20) -> MCPToolResponse:
    """Get critical severity threats."""
    try:
        threats = agg.get_critical_threats(limit=limit)
        data = [t.to_dict() for t in threats]
        return MCPToolResponse(
            success=True,
            data={
                "count": len(data),
                "threats": data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_critical_threats: {e}")
        return MCPToolResponse(success=False, error=str(e))


def search_threats(
    keywords: str = None,
    severity: str = None,
    category: str = None,
    source: str = None,
    days: int = 7,
    limit: int = 50
) -> MCPToolResponse:
    """Search threats with flexible filters."""
    try:
        severity_enum = SeverityLevel(severity) if severity else None
        category_enum = ThreatCategory(category) if category else None

        query = SearchQuery(
            keywords=keywords,
            severity=severity_enum,
            category=category_enum,
            source=source,
            days_back=days,
            limit=limit
        )

        threats = agg.db.search_threats(query)
        data = [t.to_dict() for t in threats]

        return MCPToolResponse(
            success=True,
            data={
                "query": {
                    "keywords": keywords,
                    "severity": severity,
                    "category": category,
                    "source": source,
                    "days_back": days,
                    "limit": limit
                },
                "count": len(data),
                "threats": data
            }
        )
    except Exception as e:
        logger.error(f"Error in search_threats: {e}")
        return MCPToolResponse(success=False, error=str(e))


def get_threat_statistics() -> MCPToolResponse:
    """Get threat database statistics."""
    try:
        stats = agg.get_stats()
        return MCPToolResponse(
            success=True,
            data={
                "total_threats": stats.total_threats,
                "threats_this_week": stats.threats_this_week,
                "threats_this_month": stats.threats_this_month,
                "by_severity": stats.by_severity,
                "by_category": stats.by_category,
                "by_source": stats.by_source,
                "last_fetch": stats.last_fetch.isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error in get_threat_statistics: {e}")
        return MCPToolResponse(success=False, error=str(e))


def get_threats_by_source(source: str, limit: int = 50) -> MCPToolResponse:
    """Get threats from a specific source."""
    try:
        threats = agg.get_by_source(source, limit=limit)
        data = [t.to_dict() for t in threats]
        return MCPToolResponse(
            success=True,
            data={
                "source": source,
                "count": len(data),
                "threats": data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_threats_by_source: {e}")
        return MCPToolResponse(success=False, error=str(e))


def fetch_latest_threats() -> MCPToolResponse:
    """Trigger a manual fetch of latest threats."""
    try:
        result = agg.fetch_threats()
        return MCPToolResponse(
            success=True,
            data={
                "source": result.source,
                "threats_found": result.threats_found,
                "threats_new": result.threats_new,
                "threats_duplicate": result.threats_duplicate,
                "errors": result.errors,
                "fetch_time_seconds": result.fetch_time_seconds
            }
        )
    except Exception as e:
        logger.error(f"Error in fetch_latest_threats: {e}")
        return MCPToolResponse(success=False, error=str(e))


def get_vulnerabilities(days: int = 7, limit: int = 20) -> MCPToolResponse:
    """Get CVE/vulnerability threats."""
    try:
        query = SearchQuery(
            category=ThreatCategory.VULNERABILITY,
            days_back=days,
            limit=limit
        )
        threats = agg.db.search_threats(query)
        data = [t.to_dict() for t in threats]
        return MCPToolResponse(
            success=True,
            data={
                "count": len(data),
                "threats": data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_vulnerabilities: {e}")
        return MCPToolResponse(success=False, error=str(e))


def get_malware_alerts(days: int = 7, limit: int = 20) -> MCPToolResponse:
    """Get malware/ransomware threats."""
    try:
        malware_query = SearchQuery(
            category=ThreatCategory.MALWARE,
            days_back=days,
            limit=limit // 2
        )
        ransomware_query = SearchQuery(
            category=ThreatCategory.RANSOMWARE,
            days_back=days,
            limit=limit // 2
        )

        threats = agg.db.search_threats(malware_query)
        threats.extend(agg.db.search_threats(ransomware_query))

        data = [t.to_dict() for t in sorted(
            threats,
            key=lambda x: x.published_date,
            reverse=True
        )[:limit]]

        return MCPToolResponse(
            success=True,
            data={
                "count": len(data),
                "threats": data
            }
        )
    except Exception as e:
        logger.error(f"Error in get_malware_alerts: {e}")
        return MCPToolResponse(success=False, error=str(e))


# MCP Tool Definitions
TOOLS = {
    "get_recent_threats": {
        "description": "Get recent threat intelligence from the last N days",
        "parameters": {
            "days": {"type": "integer", "description": "Days to look back (default: 7)"},
            "limit": {"type": "integer", "description": "Max threats to return (default: 20)"}
        },
        "handler": get_recent_threats
    },
    "get_critical_threats": {
        "description": "Get critical severity threats only",
        "parameters": {
            "limit": {"type": "integer", "description": "Max threats to return (default: 20)"}
        },
        "handler": get_critical_threats
    },
    "search_threats": {
        "description": "Search threats with filters",
        "parameters": {
            "keywords": {"type": "string", "description": "Search keywords"},
            "severity": {"type": "string", "description": "Filter by severity (critical, high, medium, low, info)"},
            "category": {"type": "string", "description": "Filter by category (cve, malware, breach, ransomware, etc.)"},
            "source": {"type": "string", "description": "Filter by source (Bleeping Computer, Palo Alto, etc.)"},
            "days": {"type": "integer", "description": "Days to look back (default: 7)"},
            "limit": {"type": "integer", "description": "Max results (default: 50)"}
        },
        "handler": search_threats
    },
    "get_threat_statistics": {
        "description": "Get threat database statistics and summary",
        "parameters": {},
        "handler": get_threat_statistics
    },
    "get_threats_by_source": {
        "description": "Get threats from a specific source",
        "parameters": {
            "source": {"type": "string", "description": "Source name"},
            "limit": {"type": "integer", "description": "Max threats (default: 50)"}
        },
        "handler": get_threats_by_source
    },
    "fetch_latest_threats": {
        "description": "Trigger a fresh fetch of latest threats from all sources",
        "parameters": {},
        "handler": fetch_latest_threats
    },
    "get_vulnerabilities": {
        "description": "Get CVE and vulnerability threats",
        "parameters": {
            "days": {"type": "integer", "description": "Days to look back (default: 7)"},
            "limit": {"type": "integer", "description": "Max threats (default: 20)"}
        },
        "handler": get_vulnerabilities
    },
    "get_malware_alerts": {
        "description": "Get malware and ransomware threat alerts",
        "parameters": {
            "days": {"type": "integer", "description": "Days to look back (default: 7)"},
            "limit": {"type": "integer", "description": "Max threats (default: 20)"}
        },
        "handler": get_malware_alerts
    }
}


def list_tools():
    """List available tools."""
    tools = []
    for name, tool_def in TOOLS.items():
        tools.append({
            "name": name,
            "description": tool_def["description"],
            "parameters": tool_def["parameters"]
        })
    return tools


def call_tool(tool_name: str, **kwargs) -> MCPToolResponse:
    """Call a tool by name."""
    if tool_name not in TOOLS:
        return MCPToolResponse(
            success=False,
            error=f"Unknown tool: {tool_name}"
        )

    handler = TOOLS[tool_name]["handler"]
    try:
        return handler(**kwargs)
    except Exception as e:
        logger.error(f"Error calling {tool_name}: {e}", exc_info=True)
        return MCPToolResponse(success=False, error=str(e))


# Simple CLI interface for testing
def interactive_mode():
    """Interactive CLI mode."""
    print("ThreatFeed MCP Server - Interactive Mode")
    print("Type 'help' for commands, 'quit' to exit\n")

    while True:
        try:
            cmd = input(">> ").strip()

            if not cmd:
                continue

            if cmd == "quit":
                break

            if cmd == "help":
                print("\nAvailable tools:")
                for tool in list_tools():
                    print(f"  - {tool['name']}: {tool['description']}")
                print()
                continue

            # Parse command
            parts = cmd.split()
            tool_name = parts[0]

            # Extract kwargs from remaining parts
            kwargs = {}
            for part in parts[1:]:
                if '=' in part:
                    key, val = part.split('=')
                    try:
                        kwargs[key] = int(val)
                    except ValueError:
                        kwargs[key] = val

            response = call_tool(tool_name, **kwargs)
            print(response.to_json())

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_mode()
    else:
        print("ThreatFeed MCP Server")
        print("Tools available:")
        for tool in list_tools():
            print(f"  - {tool['name']}")
        print("\nRun with --interactive for interactive mode")
