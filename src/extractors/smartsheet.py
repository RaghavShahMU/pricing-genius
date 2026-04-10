"""Smartsheet pricing extractor.

Code extraction: prices from JSON-LD structured data in HTML.
AI extraction: full comparison table from screenshot.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from src.schemas.smartsheet import SmartsheetPricing
from .base import BaseExtractor


class SmartsheetExtractor(BaseExtractor):
    competitor = "smartsheet"
    display_name = "Smartsheet"
    url = "https://www.smartsheet.com/pricing"
    schema_cls = SmartsheetPricing

    async def code_extract(self, html: str) -> dict[str, Any] | None:
        """Extract prices from Smartsheet's HTML."""
        plans = []

        # Extract JSON-LD pricing data
        json_ld = re.findall(
            r'<script[^>]*type="application/ld\+json"[^>]*>([\s\S]*?)</script>', html
        )
        for block in json_ld:
            try:
                data = json.loads(block)
                if isinstance(data, dict) and "offers" in data:
                    for offer in data["offers"]:
                        name = offer.get("name", "")
                        price = offer.get("price")
                        if name and price:
                            plans.append({
                                "name": name,
                                "slug": name.lower().replace(" ", "-"),
                                "pricing": {
                                    "annual_per_unit": float(price),
                                    "unit": "member",
                                    "currency": "USD",
                                },
                                "is_custom_pricing": False,
                            })
            except (json.JSONDecodeError, ValueError):
                continue

        # Also try extracting from visible price elements
        price_pattern = r'\$(\d+)\s*(?:per\s+)?(?:Member|member)\s*/\s*month'
        for match in re.finditer(price_pattern, html):
            price_val = float(match.group(1))
            # Deduplicate
            if not any(
                p.get("pricing", {}).get("annual_per_unit") == price_val
                for p in plans
            ):
                plans.append({
                    "name": f"Plan ${price_val}",
                    "pricing": {"annual_per_unit": price_val, "unit": "member", "currency": "USD"},
                    "is_custom_pricing": False,
                })

        if not plans:
            return None

        return {
            "competitor": self.competitor,
            "display_name": self.display_name,
            "url": self.url,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "extraction_method": "python",
            "data_version": 1,
            "plans": plans,
        }

    def get_extraction_prompt(self) -> str:
        return """### Smartsheet Specifics
- Plans: Pro, Business, Enterprise, Advanced Work Management (AWM)
- Prices are "per Member/month"
- Look for the full comparison table below the pricing cards
- Extract add-ons and support tiers
- url: "https://www.smartsheet.com/pricing"
"""
