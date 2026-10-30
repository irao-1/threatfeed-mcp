"""Database layer for threat storage."""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from models import Threat, SeverityLevel, ThreatCategory, SearchQuery, Stats


class ThreatDatabase:
    """SQLite-based threat database."""

    def __init__(self, db_path: str = "data/threats.db"):
        """Initialize database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Threats table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS threats (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT NOT NULL,
                url TEXT UNIQUE NOT NULL,
                published_date TIMESTAMP,
                fetched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity TEXT DEFAULT 'info',
                category TEXT DEFAULT 'general',
                cves TEXT,
                affected_products TEXT,
                keywords TEXT,
                is_duplicate BOOLEAN DEFAULT 0,
                duplicate_of TEXT,
                confidence_score REAL DEFAULT 0.0
            )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON threats(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_severity ON threats(severity)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON threats(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_published ON threats(published_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fetched ON threats(fetched_date)")

            # Fetch log table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS fetch_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                fetch_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                threats_found INTEGER,
                threats_new INTEGER,
                errors TEXT
            )
            """)

            conn.commit()

    def save_threat(self, threat: Threat) -> bool:
        """Save a threat to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT OR REPLACE INTO threats (
                    id, title, description, source, url, published_date,
                    fetched_date, severity, category, cves, affected_products,
                    keywords, is_duplicate, duplicate_of, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    threat.id, threat.title, threat.description,
                    threat.source, threat.url, threat.published_date,
                    threat.fetched_date, threat.severity.value,
                    threat.category.value, json.dumps(threat.cves),
                    json.dumps(threat.affected_products), json.dumps(threat.keywords),
                    threat.is_duplicate, threat.duplicate_of, threat.confidence_score
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def threat_exists(self, threat_id: str) -> bool:
        """Check if threat exists."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM threats WHERE id = ?", (threat_id,))
            return cursor.fetchone() is not None

    def get_threat(self, threat_id: str) -> Optional[Threat]:
        """Retrieve a threat by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM threats WHERE id = ?", (threat_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_threat(row)
        return None

    def search_threats(self, query: SearchQuery) -> List[Threat]:
        """Search threats with flexible filtering."""
        sql = "SELECT * FROM threats WHERE 1=1"
        params = []

        # Add filters
        if query.keywords:
            keywords = f"%{query.keywords}%"
            sql += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([keywords, keywords])

        if query.severity:
            sql += " AND severity = ?"
            params.append(query.severity.value)

        if query.category:
            sql += " AND category = ?"
            params.append(query.category.value)

        if query.source:
            sql += " AND source = ?"
            params.append(query.source)

        # Date range
        cutoff_date = datetime.utcnow() - timedelta(days=query.days_back)
        sql += " AND published_date > ?"
        params.append(cutoff_date)

        # Exclude duplicates
        sql += " AND is_duplicate = 0"

        # Order and limit
        sql += " ORDER BY published_date DESC LIMIT ? OFFSET ?"
        params.extend([query.limit, query.offset])

        threats = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            for row in cursor.fetchall():
                threats.append(self._row_to_threat(row))

        return threats

    def get_recent_threats(self, limit: int = 50, days: int = 7) -> List[Threat]:
        """Get recent threats."""
        query = SearchQuery(days_back=days, limit=limit)
        return self.search_threats(query)

    def get_by_severity(self, severity: SeverityLevel, limit: int = 50) -> List[Threat]:
        """Get threats by severity."""
        query = SearchQuery(severity=severity, limit=limit)
        return self.search_threats(query)

    def get_by_source(self, source: str, limit: int = 50) -> List[Threat]:
        """Get threats from a specific source."""
        query = SearchQuery(source=source, limit=limit)
        return self.search_threats(query)

    def get_stats(self) -> Stats:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total count
            cursor.execute("SELECT COUNT(*) FROM threats WHERE is_duplicate = 0")
            total = cursor.fetchone()[0]

            # By severity
            cursor.execute("""
            SELECT severity, COUNT(*) FROM threats
            WHERE is_duplicate = 0
            GROUP BY severity
            """)
            by_severity = dict(cursor.fetchall())

            # By category
            cursor.execute("""
            SELECT category, COUNT(*) FROM threats
            WHERE is_duplicate = 0
            GROUP BY category
            """)
            by_category = dict(cursor.fetchall())

            # By source
            cursor.execute("""
            SELECT source, COUNT(*) FROM threats
            WHERE is_duplicate = 0
            GROUP BY source
            """)
            by_source = dict(cursor.fetchall())

            # Last fetch
            cursor.execute("""
            SELECT MAX(fetch_date) FROM fetch_log
            """)
            last_fetch = cursor.fetchone()[0]
            if last_fetch:
                last_fetch = datetime.fromisoformat(last_fetch)
            else:
                last_fetch = datetime.utcnow()

            # This week
            week_ago = datetime.utcnow() - timedelta(days=7)
            cursor.execute("""
            SELECT COUNT(*) FROM threats
            WHERE is_duplicate = 0 AND published_date > ?
            """, (week_ago,))
            threats_this_week = cursor.fetchone()[0]

            # This month
            month_ago = datetime.utcnow() - timedelta(days=30)
            cursor.execute("""
            SELECT COUNT(*) FROM threats
            WHERE is_duplicate = 0 AND published_date > ?
            """, (month_ago,))
            threats_this_month = cursor.fetchone()[0]

        return Stats(
            total_threats=total,
            by_severity=by_severity,
            by_category=by_category,
            by_source=by_source,
            last_fetch=last_fetch,
            threats_this_week=threats_this_week,
            threats_this_month=threats_this_month
        )

    def log_fetch(self, source: str, found: int, new: int, errors: List[str] = None):
        """Log a fetch operation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO fetch_log (source, threats_found, threats_new, errors)
            VALUES (?, ?, ?, ?)
            """, (source, found, new, json.dumps(errors or [])))
            conn.commit()

    def cleanup_old_threats(self, days: int = 90):
        """Remove threats older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            DELETE FROM threats WHERE published_date < ? AND is_duplicate = 1
            """, (cutoff_date,))
            conn.commit()
            return cursor.rowcount

    @staticmethod
    def _row_to_threat(row) -> Threat:
        """Convert database row to Threat object."""
        return Threat(
            id=row[0],
            title=row[1],
            description=row[2],
            source=row[3],
            url=row[4],
            published_date=datetime.fromisoformat(row[5]) if row[5] else datetime.utcnow(),
            fetched_date=datetime.fromisoformat(row[6]),
            severity=SeverityLevel(row[7]),
            category=ThreatCategory(row[8]),
            cves=json.loads(row[9]) if row[9] else [],
            affected_products=json.loads(row[10]) if row[10] else [],
            keywords=json.loads(row[11]) if row[11] else [],
            is_duplicate=bool(row[12]),
            duplicate_of=row[13],
            confidence_score=row[14]
        )
