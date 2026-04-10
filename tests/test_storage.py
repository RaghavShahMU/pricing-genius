"""Tests for the JSON storage layer."""

import json
import pytest
from pathlib import Path

from src.storage.json_store import (
    COMPETITOR_SLUGS,
    get_data_path,
    list_competitors,
    load_competitor,
    load_competitor_raw,
    save_competitor,
)


class TestStorageBasics:
    def test_competitor_slugs(self):
        assert "smartsheet" in COMPETITOR_SLUGS
        assert "wrike" in COMPETITOR_SLUGS
        assert "asana" in COMPETITOR_SLUGS
        assert "notion" in COMPETITOR_SLUGS
        assert "monday" in COMPETITOR_SLUGS
        assert len(COMPETITOR_SLUGS) == 5

    def test_get_data_path(self):
        path = get_data_path("smartsheet")
        assert path.name == "smartsheet.json"

    def test_get_data_path_invalid(self):
        with pytest.raises(ValueError, match="Unknown competitor"):
            get_data_path("invalid")

    def test_list_competitors(self):
        result = list_competitors()
        assert len(result) == 5
        for item in result:
            assert "competitor" in item
            assert "has_data" in item

    def test_load_and_validate_all(self):
        """Load all seeded data and validate against schemas."""
        for slug in COMPETITOR_SLUGS:
            path = get_data_path(slug)
            if not path.exists():
                pytest.skip(f"No seed data for {slug}")

            data = load_competitor(slug)
            assert data.competitor == slug

    def test_load_raw(self):
        for slug in COMPETITOR_SLUGS:
            path = get_data_path(slug)
            if not path.exists():
                pytest.skip(f"No seed data for {slug}")

            raw = load_competitor_raw(slug)
            assert isinstance(raw, dict)
            assert raw["competitor"] == slug

    def test_roundtrip_save_load(self, tmp_path, monkeypatch):
        """Save and reload data to verify JSON serialization roundtrip."""
        import src.storage.json_store as store
        monkeypatch.setattr(store, "DATA_DIR", tmp_path)

        # Load original data
        original_path = Path(__file__).parent.parent / "data" / "notion.json"
        if not original_path.exists():
            pytest.skip("Seed data not available")

        from src.schemas.notion import NotionPricing
        raw = json.loads(original_path.read_text())
        original = NotionPricing.model_validate(raw)

        # Save to temp dir
        save_competitor("notion", original)

        # Reload
        reloaded = load_competitor("notion")
        assert reloaded.competitor == original.competitor
        assert len(reloaded.plans) == len(original.plans)
        for orig_plan, reload_plan in zip(original.plans, reloaded.plans):
            assert orig_plan.name == reload_plan.name
            assert orig_plan.slug == reload_plan.slug
            if orig_plan.pricing and reload_plan.pricing:
                assert orig_plan.pricing.monthly_per_unit == reload_plan.pricing.monthly_per_unit
                assert orig_plan.pricing.annual_per_unit == reload_plan.pricing.annual_per_unit
