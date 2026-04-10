"""Tests for MCP query tools."""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.tools.query import register_query_tools


@pytest.fixture
def tools():
    """Register tools and return a dict of tool functions."""
    mcp = MagicMock()
    tool_funcs = {}

    original_tool = mcp.tool

    def capture_tool(*args, **kwargs):
        def decorator(func):
            tool_funcs[func.__name__] = func
            return func
        return decorator

    mcp.tool = capture_tool
    register_query_tools(mcp)
    return tool_funcs


class TestGetCompetitorPricing:
    def test_valid_competitor(self, tools):
        result = tools["get_competitor_pricing"]("smartsheet")
        assert "competitor" in result
        assert result["competitor"] == "smartsheet"

    def test_case_insensitive(self, tools):
        result = tools["get_competitor_pricing"]("Smartsheet")
        assert result.get("competitor") == "smartsheet"

    def test_invalid_competitor(self, tools):
        result = tools["get_competitor_pricing"]("invalid")
        assert "error" in result

    def test_all_competitors_loadable(self, tools):
        for slug in ["smartsheet", "wrike", "asana", "notion", "monday"]:
            result = tools["get_competitor_pricing"](slug)
            assert "error" not in result, f"Failed to load {slug}: {result.get('error')}"


class TestListCompetitors:
    def test_returns_all(self, tools):
        result = tools["list_competitors"]()
        assert len(result) == 5
        slugs = [c["competitor"] for c in result]
        assert "smartsheet" in slugs
        assert "monday" in slugs


class TestCompareTiers:
    def test_compare_all(self, tools):
        result = tools["compare_tiers"]()
        assert "tiers" in result
        assert len(result["tiers"]) > 0

    def test_compare_free_tiers(self, tools):
        result = tools["compare_tiers"](tier_type="free")
        assert "tiers" in result
        for tier in result["tiers"]:
            assert tier["tier_category"] == "free"

    def test_compare_specific_competitors(self, tools):
        result = tools["compare_tiers"](competitors=["asana", "notion"])
        assert result["competitors_compared"] == ["asana", "notion"]

    def test_compare_invalid_competitor(self, tools):
        result = tools["compare_tiers"](competitors=["invalid"])
        assert "error" in result


class TestGetPriceRange:
    def test_price_for_10_seats(self, tools):
        result = tools["get_price_range"](seats=10, billing="annual")
        assert "plans" in result
        assert len(result["plans"]) > 0
        # Should be sorted by monthly_total ascending
        totals = [p["monthly_total"] for p in result["plans"]]
        assert totals == sorted(totals)

    def test_price_monthly_billing(self, tools):
        result = tools["get_price_range"](seats=5, billing="monthly")
        assert result["billing"] == "monthly"

    def test_invalid_seats(self, tools):
        result = tools["get_price_range"](seats=0)
        assert "error" in result

    def test_invalid_billing(self, tools):
        result = tools["get_price_range"](seats=5, billing="weekly")
        assert "error" in result

    def test_monday_minimum_seats(self, tools):
        """Monday.com has a 3-seat minimum. Requesting 1 seat should still use 3."""
        result = tools["get_price_range"](seats=1, billing="annual")
        monday_plans = [p for p in result["plans"] if "Monday" in p.get("competitor", "")]
        for plan in monday_plans:
            assert plan["seats"] >= 3


class TestSearchFeatures:
    def test_search_sso(self, tools):
        result = tools["search_features"]("SSO")
        assert result["total_matches"] > 0
        assert any("SSO" in m["feature"] for m in result["matches"])

    def test_search_gantt(self, tools):
        result = tools["search_features"]("Gantt")
        assert result["total_matches"] > 0

    def test_search_empty(self, tools):
        result = tools["search_features"]("")
        assert "error" in result

    def test_search_nonexistent(self, tools):
        result = tools["search_features"]("xyznonexistentfeature123")
        assert result["total_matches"] == 0
