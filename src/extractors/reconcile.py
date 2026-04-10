"""Reconciliation engine — merges code and AI extraction results.

Rules:
1. Prices: code wins (more reliable for exact numbers from structured data)
2. Features: AI wins (sees the full comparison table from screenshots)
3. Disagreements are flagged as warnings
4. Historical diffs (>20% feature change) trigger review flags
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Previous extraction data for historical comparison
DATA_DIR = Path(__file__).parent.parent.parent / "data"


def reconcile(
    code_result: dict | None,
    ai_result: dict | None,
    competitor: str,
) -> tuple[dict, list[str]]:
    """Merge code and AI extraction results.

    Args:
        code_result: Result from code-based extraction (may be partial or None)
        ai_result: Result from AI Vision extraction (may be None)
        competitor: Competitor slug

    Returns:
        (merged_result, list_of_warnings)
    """
    warnings: list[str] = []

    # Handle missing results
    if ai_result is None and code_result is None:
        raise RuntimeError(f"Both code and AI extraction failed for {competitor}")

    if ai_result is None:
        warnings.append(f"AI extraction unavailable — using code-only result for {competitor}")
        return code_result, warnings

    if code_result is None:
        warnings.append(f"Code extraction unavailable — using AI-only result for {competitor}")
        return ai_result, warnings

    # Both available — merge
    merged = _deep_copy(ai_result)  # Start with AI (has more complete features)

    # Override prices from code (more reliable)
    price_warnings = _reconcile_prices(merged, code_result, competitor)
    warnings.extend(price_warnings)

    # Override metadata
    merged["extraction_method"] = "hybrid"
    merged["extracted_at"] = datetime.now(timezone.utc).isoformat()

    # Historical comparison
    hist_warnings = _check_historical_drift(merged, competitor)
    warnings.extend(hist_warnings)

    return merged, warnings


def _reconcile_prices(merged: dict, code_result: dict, competitor: str) -> list[str]:
    """Override AI prices with code prices where available. Flag disagreements."""
    warnings = []

    if competitor == "monday":
        _reconcile_monday_prices(merged, code_result, warnings)
    else:
        _reconcile_standard_prices(merged, code_result, competitor, warnings)

    return warnings


def _reconcile_standard_prices(
    merged: dict, code_result: dict, competitor: str, warnings: list[str]
) -> None:
    """Reconcile prices for standard (non-Monday) competitors."""
    code_plans = {p.get("slug", p.get("name", "").lower()): p for p in code_result.get("plans", [])}

    for plan in merged.get("plans", []):
        slug = plan.get("slug", plan.get("name", "").lower())
        code_plan = code_plans.get(slug)

        if not code_plan or not code_plan.get("pricing"):
            continue

        ai_pricing = plan.get("pricing")
        code_pricing = code_plan["pricing"]

        if ai_pricing:
            # Check for disagreement
            for field in ["monthly_per_unit", "annual_per_unit"]:
                ai_val = ai_pricing.get(field)
                code_val = code_pricing.get(field)
                if ai_val and code_val and ai_val != code_val:
                    diff_pct = abs(ai_val - code_val) / code_val * 100
                    if diff_pct > 10:
                        warnings.append(
                            f"PRICE MISMATCH {competitor}/{slug}/{field}: "
                            f"code=${code_val} vs AI=${ai_val} ({diff_pct:.1f}% diff)"
                        )

        # Code prices win
        plan["pricing"] = code_pricing


def _reconcile_monday_prices(merged: dict, code_result: dict, warnings: list[str]) -> None:
    """Reconcile prices for Monday.com (multi-product structure)."""
    for product in merged.get("products", []):
        code_product = None
        for cp in code_result.get("products", []):
            if cp.get("slug") == product.get("slug"):
                code_product = cp
                break

        if not code_product:
            continue

        code_plans = {p.get("slug"): p for p in code_product.get("plans", [])}

        for plan in product.get("plans", []):
            slug = plan.get("slug")
            code_plan = code_plans.get(slug)
            if code_plan and code_plan.get("pricing"):
                plan["pricing"] = code_plan["pricing"]


def _check_historical_drift(current: dict, competitor: str) -> list[str]:
    """Compare current extraction with previous data to detect large changes."""
    warnings = []

    previous_path = DATA_DIR / f"{competitor}.json"
    if not previous_path.exists():
        return warnings

    try:
        with open(previous_path) as f:
            previous = json.load(f)
    except (json.JSONDecodeError, IOError):
        return warnings

    # Count features in both
    prev_features = _count_all_features(previous, competitor)
    curr_features = _count_all_features(current, competitor)

    if prev_features > 0:
        change_pct = abs(curr_features - prev_features) / prev_features * 100
        if change_pct > 30:
            warnings.append(
                f"LARGE FEATURE CHANGE for {competitor}: "
                f"{prev_features} → {curr_features} ({change_pct:.0f}% change). "
                f"Review needed — pricing pages rarely change this much."
            )

    # Check for price changes
    prev_prices = _extract_all_prices(previous, competitor)
    curr_prices = _extract_all_prices(current, competitor)

    for plan_slug, prev_price in prev_prices.items():
        curr_price = curr_prices.get(plan_slug)
        if prev_price and curr_price:
            for field in ["monthly_per_unit", "annual_per_unit"]:
                pv = prev_price.get(field)
                cv = curr_price.get(field)
                if pv and cv and pv != cv:
                    warnings.append(
                        f"PRICE CHANGED for {competitor}/{plan_slug}/{field}: "
                        f"${pv} → ${cv}"
                    )

    return warnings


def _count_all_features(data: dict, competitor: str) -> int:
    """Count total features in the first plan (representative)."""
    if competitor == "monday":
        for product in data.get("products", []):
            for plan in product.get("plans", []):
                total = sum(len(v) for v in (plan.get("features") or {}).values())
                if total > 0:
                    return total
    else:
        for plan in data.get("plans", []):
            total = sum(len(v) for v in (plan.get("features") or {}).values())
            if total > 0:
                return total
    return 0


def _extract_all_prices(data: dict, competitor: str) -> dict:
    """Extract plan_slug -> pricing dict mapping."""
    prices = {}
    if competitor == "monday":
        for product in data.get("products", []):
            for plan in product.get("plans", []):
                if plan.get("pricing"):
                    prices[plan.get("slug", "")] = plan["pricing"]
    else:
        for plan in data.get("plans", []):
            if plan.get("pricing"):
                prices[plan.get("slug", "")] = plan["pricing"]
    return prices


def _deep_copy(obj: Any) -> Any:
    """Deep copy via JSON serialization."""
    return json.loads(json.dumps(obj))
