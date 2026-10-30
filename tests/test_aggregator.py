"""Tests for the threat aggregator."""

import unittest
from datetime import datetime
from src.models import Threat, SeverityLevel, ThreatCategory
from src.utils import (
    extract_cves, score_severity, categorize_threat,
    similarity_score, generate_id
)


class TestCVEExtraction(unittest.TestCase):
    """Test CVE extraction."""

    def test_single_cve(self):
        text = "Critical CVE-2026-1234 vulnerability"
        cves = extract_cves(text)
        self.assertIn("CVE-2026-1234", cves)

    def test_multiple_cves(self):
        text = "CVE-2026-1234 and CVE-2026-5678 are critical"
        cves = extract_cves(text)
        self.assertEqual(len(cves), 2)

    def test_no_cves(self):
        text = "No CVEs mentioned here"
        cves = extract_cves(text)
        self.assertEqual(len(cves), 0)

    def test_case_insensitive(self):
        text = "cve-2026-1234 and CVE-2026-5678"
        cves = extract_cves(text)
        self.assertEqual(len(cves), 2)


class TestSeverityScoring(unittest.TestCase):
    """Test threat severity scoring."""

    def test_critical_keywords(self):
        title = "Zero-day RCE in OpenSSL"
        description = "Remote code execution vulnerability"
        severity = score_severity(title, description)
        self.assertEqual(severity, SeverityLevel.CRITICAL)

    def test_high_keywords(self):
        title = "Vulnerability in Apache"
        description = "Privilege escalation issue"
        severity = score_severity(title, description)
        self.assertEqual(severity, SeverityLevel.HIGH)

    def test_medium_keywords(self):
        title = "Denial of Service"
        description = "DoS attack possible"
        severity = score_severity(title, description)
        self.assertEqual(severity, SeverityLevel.MEDIUM)

    def test_default_info(self):
        title = "Security news"
        description = "General announcement"
        severity = score_severity(title, description)
        self.assertEqual(severity, SeverityLevel.INFO)


class TestThreatCategorization(unittest.TestCase):
    """Test threat categorization."""

    def test_cve_category(self):
        title = "CVE-2026-1234 in Linux kernel"
        description = "Critical vulnerability"
        category = categorize_threat(title, description)
        self.assertEqual(category, ThreatCategory.CVE)

    def test_malware_category(self):
        title = "New ransomware variant found"
        description = "Malware spreading globally"
        category = categorize_threat(title, description)
        self.assertIn(category, [ThreatCategory.MALWARE, ThreatCategory.RANSOMWARE])

    def test_breach_category(self):
        title = "Data breach at company X"
        description = "Customer data stolen"
        category = categorize_threat(title, description)
        self.assertEqual(category, ThreatCategory.BREACH)

    def test_general_category(self):
        title = "Security update available"
        description = "Patches released"
        category = categorize_threat(title, description)
        self.assertEqual(category, ThreatCategory.GENERAL)


class TestSimilarityScore(unittest.TestCase):
    """Test text similarity scoring."""

    def test_identical_text(self):
        text1 = "Critical vulnerability in Linux"
        text2 = "Critical vulnerability in Linux"
        score = similarity_score(text1, text2)
        self.assertGreater(score, 0.9)

    def test_similar_text(self):
        text1 = "Critical vulnerability in Linux kernel"
        text2 = "Critical vulnerability in Linux"
        score = similarity_score(text1, text2)
        self.assertGreater(score, 0.5)

    def test_different_text(self):
        text1 = "Critical vulnerability in Linux"
        text2 = "New feature released in Windows"
        score = similarity_score(text1, text2)
        self.assertLess(score, 0.3)

    def test_empty_text(self):
        score = similarity_score("", "text")
        self.assertEqual(score, 0.0)


class TestThreatModel(unittest.TestCase):
    """Test Threat data model."""

    def test_threat_creation(self):
        threat = Threat(
            id="test123",
            title="Test Threat",
            description="A test threat",
            source="Test Source",
            url="https://example.com/threat",
            published_date=datetime.utcnow(),
            severity=SeverityLevel.CRITICAL,
            category=ThreatCategory.VULNERABILITY
        )

        self.assertEqual(threat.id, "test123")
        self.assertEqual(threat.severity, SeverityLevel.CRITICAL)
        self.assertFalse(threat.is_duplicate)

    def test_threat_to_dict(self):
        threat = Threat(
            id="test123",
            title="Test",
            description="Description",
            source="Source",
            url="https://example.com",
            published_date=datetime.utcnow(),
            cves=["CVE-2026-1234"]
        )

        threat_dict = threat.to_dict()
        self.assertIn("id", threat_dict)
        self.assertIn("cves", threat_dict)
        self.assertEqual(threat_dict["cves"], ["CVE-2026-1234"])


class TestIDGeneration(unittest.TestCase):
    """Test unique ID generation."""

    def test_id_consistency(self):
        url = "https://example.com/threat"
        id1 = generate_id(url)
        id2 = generate_id(url)
        self.assertEqual(id1, id2)

    def test_id_uniqueness(self):
        url1 = "https://example.com/threat1"
        url2 = "https://example.com/threat2"
        id1 = generate_id(url1)
        id2 = generate_id(url2)
        self.assertNotEqual(id1, id2)

    def test_id_format(self):
        url = "https://example.com/threat"
        threat_id = generate_id(url)
        self.assertEqual(len(threat_id), 16)
        self.assertTrue(all(c in '0123456789abcdef' for c in threat_id))


class TestDatabase(unittest.TestCase):
    """Test database operations."""

    def setUp(self):
        """Set up test database."""
        from src.database import ThreatDatabase
        self.db = ThreatDatabase(":memory:")  # In-memory SQLite

    def test_save_and_retrieve_threat(self):
        threat = Threat(
            id="test123",
            title="Test Threat",
            description="A test",
            source="Test",
            url="https://example.com",
            published_date=datetime.utcnow()
        )

        saved = self.db.save_threat(threat)
        self.assertTrue(saved)

        retrieved = self.db.get_threat("test123")
        self.assertIsNotNull(retrieved)
        self.assertEqual(retrieved.title, "Test Threat")

    def test_threat_exists(self):
        threat = Threat(
            id="test456",
            title="Test",
            description="Test",
            source="Test",
            url="https://example.com/2",
            published_date=datetime.utcnow()
        )

        self.db.save_threat(threat)
        self.assertTrue(self.db.threat_exists("test456"))
        self.assertFalse(self.db.threat_exists("nonexistent"))

    def assertIsNotNull(self, obj):
        """Assert object is not None."""
        self.assertIsNotNone(obj)


if __name__ == '__main__':
    unittest.main()
