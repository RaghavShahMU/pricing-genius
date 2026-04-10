#!/usr/bin/env python3
"""Run extraction for all competitors.

Usage:
    python scripts/extract_all.py                    # Extract all
    python scripts/extract_all.py smartsheet wrike   # Extract specific ones

Exit codes:
    0 = all extractions succeeded
    1 = one or more extractions failed (partial success)
    2 = all extractions failed
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors.smartsheet import SmartsheetExtractor
from src.extractors.wrike import WrikeExtractor
from src.extractors.asana import AsanaExtractor
from src.extractors.notion import NotionExtractor
from src.extractors.monday import MondayExtractor
from src.storage.json_store import save_competitor, load_competitor_raw, COMPETITOR_SLUGS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("extract_all")

EXTRACTORS = {
    "smartsheet": SmartsheetExtractor,
    "wrike": WrikeExtractor,
    "asana": AsanaExtractor,
    "notion": NotionExtractor,
    "monday": MondayExtractor,
}


def compare_extractions(slug: str, new_data: dict, old_data: dict | None) -> list[str]:
    """Compare new extraction with previous data and report differences.

    Returns a list of change descriptions for logging.
    """
    if old_data is None:
        return ["First extraction (no previous data to compare)"]

    changes = []

    # Compare plan counts
    old_plans = _get_all_plans(slug, old_data)
    new_plans = _get_all_plans(slug, new_data)

    if len(old_plans) != len(new_plans):
        changes.append(f"Plan count changed: {len(old_plans)} -> {len(new_plans)}")

    # Compare prices for each plan
    old_prices = {p.get("slug", p.get("name", "")): _get_price(p) for p in old_plans}
    new_prices = {p.get("slug", p.get("name", "")): _get_price(p) for p in new_plans}

    for plan_slug, new_price in new_prices.items():
        old_price = old_prices.get(plan_slug)
        if old_price != new_price:
            changes.append(f"Price changed for {plan_slug}: {old_price} -> {new_price}")

    # Check for new/removed plans
    added = set(new_prices.keys()) - set(old_prices.keys())
    removed = set(old_prices.keys()) - set(new_prices.keys())
    if added:
        changes.append(f"New plans added: {added}")
    if removed:
        changes.append(f"Plans removed: {removed}")

    if not changes:
        changes.append("No pricing changes detected")

    return changes


def _get_all_plans(slug: str, data: dict) -> list[dict]:
    """Get flat list of all plans from competitor data."""
    if slug == "monday":
        plans = []
        for product in data.get("products", []):
            plans.extend(product.get("plans", []))
        return plans
    return data.get("plans", [])


def _get_price(plan: dict) -> tuple | None:
    """Get comparable price tuple from a plan."""
    pricing = plan.get("pricing")
    if not pricing:
        return None
    return (pricing.get("monthly_per_unit"), pricing.get("annual_per_unit"))


async def extract_one(slug: str) -> tuple[bool, str]:
    """Extract pricing for a single competitor. Returns (success, message)."""
    extractor_cls = EXTRACTORS.get(slug)
    if not extractor_cls:
        return False, f"Unknown competitor: {slug}"

    extractor = extractor_cls()

    # Load previous data for comparison
    try:
        old_data = load_competitor_raw(slug)
    except FileNotFoundError:
        old_data = None

    try:
        result = await extractor.extract()

        # Convert to dict for comparison and storage
        new_data = json.loads(result.model_dump_json())

        # Compare with previous extraction
        changes = compare_extractions(slug, new_data, old_data)

        # Save the new data
        save_competitor(slug, result)

        change_summary = "; ".join(changes)
        return True, f"OK ({change_summary})"

    except Exception as e:
        return False, f"FAILED: {e}"


async def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(EXTRACTORS.keys())

    invalid = [t for t in targets if t not in EXTRACTORS]
    if invalid:
        print(f"Unknown competitors: {invalid}")
        print(f"Valid options: {list(EXTRACTORS.keys())}")
        sys.exit(2)

    print(f"Starting extraction for: {', '.join(targets)}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("-" * 60)

    results = {}
    for slug in targets:
        print(f"\nExtracting {slug}...")
        success, message = await extract_one(slug)
        results[slug] = (success, message)
        status = "OK" if success else "FAIL"
        print(f"  [{status}] {slug}: {message}")

    print("\n" + "=" * 60)
    successes = sum(1 for s, _ in results.values() if s)
    failures = sum(1 for s, _ in results.values() if not s)
    print(f"Results: {successes} succeeded, {failures} failed out of {len(targets)}")

    if failures == len(targets):
        sys.exit(2)
    elif failures > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
