"""Monday.com pricing extractor.

Code extraction: prices from i18n bundle + JSON-LD.
AI extraction: full comparison table from screenshot (primary source for features).
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from src.schemas.monday import MondayPricing
from .base import BaseExtractor


class MondayExtractor(BaseExtractor):
    competitor = "monday"
    display_name = "Monday.com"
    url = "https://monday.com/pricing"
    schema_cls = MondayPricing

    async def code_extract(self, html: str) -> dict[str, Any] | None:
        """Extract prices from Monday's i18n bundle and JSON-LD."""
        prices = {}

        # Try JSON-LD first
        json_ld = re.findall(
            r'<script[^>]*type="application/ld\+json"[^>]*>([\s\S]*?)</script>', html
        )
        for block in json_ld:
            try:
                data = json.loads(block)
                if isinstance(data, dict) and data.get("@type") == "Product":
                    for offer in data.get("offers", []):
                        name = offer.get("name", "").lower()
                        price = offer.get("price")
                        if price and name:
                            prices[name] = {"annual_per_unit": float(price)}
            except (json.JSONDecodeError, ValueError):
                continue

        # Build partial result with prices only
        tiers = ["free", "basic", "standard", "pro", "enterprise"]
        plans = []
        for tier in tiers:
            plan: dict[str, Any] = {
                "name": "Free" if tier == "free" else (
                    "Enterprise" if tier == "enterprise" else tier.capitalize()
                ),
                "slug": tier,
                "is_free": tier == "free",
                "is_custom_pricing": tier == "enterprise",
                "features": {},
            }

            if tier == "free":
                plan["pricing"] = None
                plan["free_seats_limit"] = 2
            elif tier == "enterprise":
                plan["pricing"] = None
            else:
                price_data = prices.get(tier, {})
                if price_data:
                    plan["pricing"] = {
                        "annual_per_unit": price_data.get("annual_per_unit"),
                        "monthly_per_unit": price_data.get("monthly_per_unit"),
                        "unit": "seat",
                        "currency": "USD",
                    }

            plans.append(plan)

        return {
            "competitor": self.competitor,
            "display_name": self.display_name,
            "url": self.url,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "extraction_method": "python",
            "data_version": 1,
            "global_policies": {
                "minimum_seats": 3,
                "annual_discount_pct": 18.0,
                "trial_days": 14,
                "custom_quote_above_seats": 40,
                "refund_window_days": 30,
            },
            "products": [
                {
                    "name": "Work Management",
                    "slug": "work-management",
                    "plans": plans,
                }
            ],
        }

    def get_extraction_prompt(self) -> str:
        return """### Monday.com Specifics
- Focus on Work Management product only
- Plans: Free, Basic, Standard, Pro, Enterprise
- Prices are "per seat/month" — minimum 3 seats on paid plans
- The comparison table has MANY sections: Essentials, Collaboration,
  Productivity, Views and reporting, Resource management, Security & privacy,
  Administration & control, Advanced reporting & analytics, Support
- There are 50+ features across these sections — extract ALL of them
- Each cell shows: checkmark, dash, or a specific value
- url: "https://monday.com/pricing"
"""
