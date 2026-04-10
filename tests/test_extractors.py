"""Tests for extractor logic (unit tests, not live extraction).

Live extraction tests are in the QA section and run separately.
These tests verify extractor class setup and validation logic.
"""

import pytest

from src.extractors.smartsheet import SmartsheetExtractor
from src.extractors.wrike import WrikeExtractor
from src.extractors.asana import AsanaExtractor
from src.extractors.notion import NotionExtractor
from src.extractors.monday import MondayExtractor


class TestExtractorSetup:
    """Verify all extractors have required attributes."""

    extractors = [
        SmartsheetExtractor,
        WrikeExtractor,
        AsanaExtractor,
        NotionExtractor,
        MondayExtractor,
    ]

    @pytest.mark.parametrize("cls", extractors)
    def test_has_competitor(self, cls):
        assert hasattr(cls, "competitor")
        assert cls.competitor in ["smartsheet", "wrike", "asana", "notion", "monday"]

    @pytest.mark.parametrize("cls", extractors)
    def test_has_url(self, cls):
        assert hasattr(cls, "url")
        assert cls.url.startswith("https://")

    @pytest.mark.parametrize("cls", extractors)
    def test_has_schema(self, cls):
        assert hasattr(cls, "schema_cls")

    @pytest.mark.parametrize("cls", extractors)
    def test_has_display_name(self, cls):
        assert hasattr(cls, "display_name")
        assert len(cls.display_name) > 0


class TestSmartsheetExtractor:
    def test_parse_empty_html(self):
        """Python extraction should fail gracefully on empty HTML."""
        import asyncio
        ext = SmartsheetExtractor()
        with pytest.raises(Exception):
            asyncio.run(ext.python_extract("<html><body></body></html>"))


class TestWrikeExtractor:
    def test_parse_empty_html(self):
        import asyncio
        ext = WrikeExtractor()
        with pytest.raises(Exception):
            asyncio.run(ext.python_extract("<html><body></body></html>"))


class TestNotionExtractor:
    def test_parse_empty_html(self):
        import asyncio
        ext = NotionExtractor()
        with pytest.raises(Exception):
            asyncio.run(ext.python_extract("<html><body></body></html>"))
