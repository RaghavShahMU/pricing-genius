"""Notion pricing extractor.

Code extraction: prices from visible HTML text.
AI extraction: full comparison table from screenshot.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from src.schemas.notion import NotionPricing
from .base import BaseExtractor


class NotionExtractor(BaseExtractor):
    competitor = "notion"
    display_name = "Notion"
    url = "https://www.notion.com/pricing"
    schema_cls = NotionPricing

    async def code_extract(self, html: str) -> dict[str, Any] | None:
        """Extract prices from Notion's HTML."""
        plans = []

        # Notion shows prices in visible text like "$10 per member / month"
        # Look for plan-price pairs
        plan_price_patterns = [
            (r"Free", 0, True),
            (r"Plus", None, False),
            (r"Business", None, False),
            (r"Enterprise", None, True),
        ]

        # Extract dollar amounts near plan names
        for plan_name, default_price, is_special in plan_price_patterns:
            slug = plan_name.lower()

            if is_special and default_price == 0:
                plans.append({
                    "name": plan_name,
                    "slug": slug,
                    "is_free": True,
                    "is_custom_pricing": False,
                    "pricing": None,
                    "file_upload_limit": "5 MB",
                    "page_history_days": 7,
                    "external_guests": 10,
                    "charts": 1,
                    "notion_site_domains": 1,
                    "ai_data_retention_days": 30,
                })
                continue

            if is_special:  # Enterprise
                plans.append({
                    "name": plan_name,
                    "slug": slug,
                    "is_free": False,
                    "is_custom_pricing": True,
                    "pricing": None,
                    "file_upload_limit": "unlimited",
                    "page_history_days": "unlimited",
                    "external_guests": "unlimited",
                    "charts": "unlimited",
                    "notion_site_domains": 5,
                    "ai_data_retention_days": 0,
                })
                continue

            # Find prices near the plan name
            # Pattern: $X per member / month (or /member/month)
            prices_near = re.findall(
                rf'{plan_name}[\s\S]{{0,200}}\$(\d+(?:\.\d+)?)',
                html, re.I
            )
            if prices_near:
                price_val = float(prices_near[0])
                plans.append({
                    "name": plan_name,
                    "slug": slug,
                    "is_free": False,
                    "is_custom_pricing": False,
                    "pricing": {
                        "monthly_per_unit": price_val,
                        "unit": "member",
                        "currency": "USD",
                    },
                    "file_upload_limit": "unlimited",
                    "page_history_days": 30 if slug == "plus" else 90,
                    "external_guests": "unlimited",
                    "charts": "unlimited",
                    "notion_site_domains": 5,
                    "ai_data_retention_days": 30,
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
        return """### Notion Specifics
- Plans: Free, Plus, Business, Enterprise
- Prices are "per member/month"
- Extract Notion-specific limits: file upload limit, page history days,
  external guests count, charts count, notion.site domains, AI data retention days
- Extract add-ons (AI Add-on, Custom Agents, Custom Domains)
- url: "https://www.notion.com/pricing"
"""
