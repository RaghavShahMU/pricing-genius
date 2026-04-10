"""Asana pricing extractor.

Code extraction: prices from JSON-LD structured data in HTML.
AI extraction: full comparison table from screenshot.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from src.schemas.asana import AsanaPricing
from .base import BaseExtractor


class AsanaExtractor(BaseExtractor):
    competitor = "asana"
    display_name = "Asana"
    url = "https://asana.com/pricing"
    schema_cls = AsanaPricing

    async def code_extract(self, html: str) -> dict[str, Any] | None:
        """Extract prices from Asana's HTML (JSON-LD + visible prices)."""
        plans = []

        # Asana has JSON-LD with pricing
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
                                "slug": name.lower().replace(" ", "-").replace("+", "-plus"),
                                "pricing": {
                                    "annual_per_unit": float(price),
                                    "unit": "user",
                                    "currency": "USD",
                                },
                                "is_free": float(price) == 0,
                                "is_custom_pricing": False,
                            })
            except (json.JSONDecodeError, ValueError):
                continue

        # Also extract from data-cy attributes
        for match in re.finditer(r'data-cy="(\w+)-price"[^>]*>\$?([\d.]+)', html):
            plan_name = match.group(1).capitalize()
            price_val = float(match.group(2))
            # Monthly price pattern
            slug = plan_name.lower()
            existing = [p for p in plans if p.get("slug") == slug]
            if existing:
                existing[0]["pricing"]["annual_per_unit"] = price_val
            else:
                plans.append({
                    "name": plan_name,
                    "slug": slug,
                    "pricing": {"annual_per_unit": price_val, "unit": "user", "currency": "USD"},
                    "is_custom_pricing": False,
                })

        # Extract monthly prices from text
        for match in re.finditer(r'\$([\d.]+)\s+billed monthly', html):
            monthly_val = float(match.group(1))
            # Find which plan this belongs to (closest preceding plan)
            # For now just store them — reconciliation will merge

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
        return """### Asana Specifics
- Plans: Personal (free), Starter, Advanced, Enterprise, Enterprise+
- Prices are "per user/month"
- Look for both the pricing cards AND the comparison table below
- Enterprise/Enterprise+ are "Contact Sales"
- url: "https://asana.com/pricing"
"""
