"""MCP tools for querying competitor pricing data."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from src.storage.json_store import (
    COMPETITOR_SLUGS,
    load_competitor,
    load_competitor_raw,
    list_competitors as _list_competitors,
)


def register_query_tools(mcp: FastMCP) -> None:
    """Register all query tools with the MCP server."""

    @mcp.tool()
    def get_competitor_pricing(competitor: str) -> dict[str, Any]:
        """Get full pricing data for a specific competitor.

        Args:
            competitor: Competitor slug. One of: smartsheet, wrike, asana, notion, monday
        """
        competitor = competitor.lower().strip()
        if competitor not in COMPETITOR_SLUGS:
            return {"error": f"Unknown competitor: {competitor}. Valid options: {COMPETITOR_SLUGS}"}
        try:
            return load_competitor_raw(competitor)
        except FileNotFoundError:
            return {"error": f"No data available for {competitor}"}

    @mcp.tool()
    def list_competitors() -> list[dict[str, Any]]:
        """List all tracked competitors with their data status and last extraction time."""
        return _list_competitors()

    @mcp.tool()
    def compare_tiers(
        competitors: list[str] | None = None,
        tier_type: str = "all",
    ) -> dict[str, Any]:
        """Compare pricing tiers across competitors.

        Args:
            competitors: List of competitor slugs to compare. None = all competitors.
            tier_type: Filter by tier type: 'free', 'mid', 'enterprise', 'all'
        """
        slugs = [s.lower().strip() for s in (competitors or COMPETITOR_SLUGS)]
        invalid = [s for s in slugs if s not in COMPETITOR_SLUGS]
        if invalid:
            return {"error": f"Unknown competitors: {invalid}. Valid: {COMPETITOR_SLUGS}"}

        comparison = []
        for slug in slugs:
            try:
                raw = load_competitor_raw(slug)
            except FileNotFoundError:
                continue

            plans = _extract_plans(slug, raw)
            for plan in plans:
                tier_category = _categorize_tier(plan)
                if tier_type != "all" and tier_category != tier_type:
                    continue

                entry = {
                    "competitor": raw.get("display_name", slug),
                    "competitor_slug": slug,
                    "tier_category": tier_category,
                    "plan_name": plan.get("name", ""),
                    "is_free": plan.get("is_free", False),
                    "is_custom_pricing": plan.get("is_custom_pricing", False),
                }

                pricing = plan.get("pricing")
                if pricing:
                    entry["monthly_per_unit"] = pricing.get("monthly_per_unit")
                    entry["annual_per_unit"] = pricing.get("annual_per_unit")
                    entry["unit"] = pricing.get("unit")
                    entry["annual_discount_pct"] = pricing.get("annual_discount_pct")
                else:
                    entry["monthly_per_unit"] = None
                    entry["annual_per_unit"] = None
                    entry["unit"] = None

                comparison.append(entry)

        return {
            "tier_type": tier_type,
            "competitors_compared": slugs,
            "tiers": comparison,
        }

    @mcp.tool()
    def get_price_range(seats: int, billing: str = "annual") -> dict[str, Any]:
        """Calculate actual cost per competitor for a given number of seats.

        Accounts for minimum seat requirements and per-seat pricing.

        Args:
            seats: Number of seats/users needed
            billing: Billing period: 'monthly' or 'annual'
        """
        if seats < 1:
            return {"error": "Seats must be at least 1"}
        if billing not in ("monthly", "annual"):
            return {"error": "Billing must be 'monthly' or 'annual'"}

        results = []
        for slug in COMPETITOR_SLUGS:
            try:
                raw = load_competitor_raw(slug)
            except FileNotFoundError:
                continue

            plans = _extract_plans(slug, raw)
            for plan in plans:
                if plan.get("is_custom_pricing") or plan.get("is_free"):
                    continue

                pricing = plan.get("pricing")
                if not pricing:
                    continue

                price_field = "monthly_per_unit" if billing == "monthly" else "annual_per_unit"
                unit_price = pricing.get(price_field)
                if unit_price is None:
                    continue

                # Check minimum seats for Monday.com
                effective_seats = seats
                if slug == "monday":
                    min_seats = raw.get("global_policies", {}).get("minimum_seats", 3)
                    effective_seats = max(seats, min_seats)

                # Check member limits
                members = plan.get("members") or plan.get("users")
                if members:
                    max_users = members.get("max")
                    if max_users is not None and seats > max_users:
                        continue

                monthly_total = unit_price * effective_seats
                annual_total = monthly_total * 12

                product_prefix = ""
                if slug == "monday":
                    product_prefix = plan.get("_product_name", "") + " - " if plan.get("_product_name") else ""

                results.append({
                    "competitor": raw.get("display_name", slug),
                    "plan": f"{product_prefix}{plan.get('name', '')}",
                    "unit_price": unit_price,
                    "billing": billing,
                    "seats": effective_seats,
                    "monthly_total": round(monthly_total, 2),
                    "annual_total": round(annual_total, 2),
                })

        results.sort(key=lambda x: x["monthly_total"])
        return {
            "seats_requested": seats,
            "billing": billing,
            "plans": results,
        }

    @mcp.tool()
    def search_features(feature: str) -> dict[str, Any]:
        """Search for a feature keyword across all competitors and tiers.

        Args:
            feature: Feature keyword to search for (e.g., 'SSO', 'automations', 'Gantt', 'time tracking')
        """
        feature_lower = feature.lower().strip()
        if not feature_lower:
            return {"error": "Feature search term cannot be empty"}

        matches = []
        for slug in COMPETITOR_SLUGS:
            try:
                raw = load_competitor_raw(slug)
            except FileNotFoundError:
                continue

            plans = _extract_plans(slug, raw)
            for plan in plans:
                features_dict = plan.get("features", {})
                for category, features_list in features_dict.items():
                    for feat in features_list:
                        feat_name = feat.get("name", "").lower()
                        feat_value = str(feat.get("value", "")).lower() if feat.get("value") else ""
                        feat_note = (feat.get("note") or "").lower()

                        if feature_lower in feat_name or feature_lower in feat_value or feature_lower in feat_note:
                            matches.append({
                                "competitor": raw.get("display_name", slug),
                                "plan": plan.get("name", ""),
                                "category": category,
                                "feature": feat.get("name", ""),
                                "available": feat.get("available", False),
                                "value": feat.get("value"),
                                "note": feat.get("note"),
                            })

        return {
            "search_term": feature,
            "total_matches": len(matches),
            "matches": matches,
        }


def _extract_plans(slug: str, raw: dict) -> list[dict]:
    """Extract plan list from raw data, handling different competitor structures."""
    if slug == "monday":
        plans = []
        for product in raw.get("products", []):
            for plan in product.get("plans", []):
                plan_copy = dict(plan)
                plan_copy["_product_name"] = product.get("name", "")
                plans.append(plan_copy)
        return plans
    return raw.get("plans", [])


def _categorize_tier(plan: dict) -> str:
    """Categorize a tier as free/mid/enterprise based on its properties."""
    if plan.get("is_free"):
        return "free"

    name_lower = plan.get("name", "").lower()
    slug_lower = plan.get("slug", "").lower()

    if any(kw in name_lower for kw in ["enterprise", "pinnacle", "apex", "ultimate", "advanced work"]):
        return "enterprise"
    if any(kw in slug_lower for kw in ["enterprise", "pinnacle", "apex", "ultimate", "awm"]):
        return "enterprise"

    return "mid"
