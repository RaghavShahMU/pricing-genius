"""Wrike pricing extractor — direct JSON parsing from structured API data.

Wrike embeds its comparison table data as structured JSON inside the page's
script tags at the key '/tp/api/v2/en/comparison-table/?product=WRIKE'.
We extract this directly — no AI needed, zero hallucination risk.

Data sources:
- /price/ — plan cards with prices, trial info
- /comparison-table/ — structured JSON with 12 categories and 78+ features
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from bs4 import BeautifulSoup

from src.schemas.common import BillingUnit, ExtractionMethod, Feature, PricingInfo, TrialInfo, UserLimits
from src.schemas.wrike import WrikeAddOn, WrikePlan, WrikePricing
from .base import BaseExtractor, ExtractionError


# Map Wrike plan display names to our slugs
PLAN_SLUG_MAP = {
    "Free": "free",
    "Team": "team",
    "Business": "business",
    "Enterprise": "enterprise",
    "Pinnacle": "pinnacle",
    "Apex": "apex",
}


class WrikeExtractor(BaseExtractor):
    competitor = "wrike"
    display_name = "Wrike"
    url = "https://www.wrike.com/price/"
    schema_cls = WrikePricing
    requires_js = False

    comparison_url = "https://www.wrike.com/comparison-table/"

    async def fetch_html(self) -> str:
        """Fetch both pricing and comparison pages."""
        import httpx

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
        }

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            pricing_resp = await client.get(self.url, headers=headers)
            pricing_resp.raise_for_status()

            comparison_resp = await client.get(self.comparison_url, headers=headers)
            comparison_resp.raise_for_status()

        return json.dumps({
            "pricing_html": pricing_resp.text,
            "comparison_html": comparison_resp.text,
        })

    async def extract(self) -> WrikePricing:
        """Direct extraction — parse structured data, no AI needed."""
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"Fetching Wrike pricing + comparison data")
        raw_json = await self.fetch_html()
        pages = json.loads(raw_json)

        comparison_html = pages["comparison_html"]

        # Extract the embedded JSON data from the comparison page
        comparison_data = self._extract_embedded_json(comparison_html)
        if not comparison_data:
            raise ExtractionError("Could not find embedded comparison data in Wrike page")

        widget = self._find_comparison_widget(comparison_data)
        if not widget:
            raise ExtractionError("Could not find pricing_comparison_widget in Wrike data")

        # Parse pricing cards
        plans = self._parse_pricing_cards(widget)

        # Parse feature comparison table
        features_by_category = self._parse_comparison_table(widget)

        # Merge features into plans
        plan_names_in_table = self._get_plan_names_from_table(widget)
        for plan in plans:
            plan_display = plan["name"]
            plan_features: dict[str, list[dict]] = {}

            for category, features in features_by_category.items():
                cat_features = []
                for feat in features:
                    values = feat.get("values", {})
                    # Find value for this plan
                    value_for_plan = values.get(plan_display, None)

                    available = True
                    feat_value = None
                    note = None

                    if value_for_plan == "–" or value_for_plan == "-":
                        available = False
                    elif value_for_plan and value_for_plan not in ("", None):
                        # Non-empty, non-dash = has a specific value
                        feat_value = value_for_plan
                    # Empty string = checkmark (available with no specific value)

                    cat_features.append({
                        "name": feat["name"],
                        "available": available,
                        "value": feat_value,
                        "note": note,
                    })

                if cat_features:
                    plan_features[category] = cat_features

            plan["features"] = plan_features

        # Parse add-ons (last category in the table)
        add_ons = self._parse_add_ons(features_by_category)

        result = WrikePricing(
            competitor=self.competitor,
            display_name=self.display_name,
            url=self.url,
            extracted_at=datetime.now(timezone.utc),
            extraction_method=ExtractionMethod.PYTHON,
            data_version=1,
            plans=[WrikePlan(**p) for p in plans],
            add_ons=add_ons,
        )

        logger.info(f"Wrike extraction succeeded: {len(plans)} plans, {sum(len(v) for v in features_by_category.values())} features")
        return result

    def _extract_embedded_json(self, html: str) -> dict | None:
        """Extract the main JSON data blob from Wrike's comparison page."""
        script_blocks = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
        for block in script_blocks:
            match = re.search(r'(\{"environment"[\s\S]+)', block)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        return None

    def _find_comparison_widget(self, data: dict) -> dict | None:
        """Find the pricing_comparison_widget in the page data."""
        comp_key = "/tp/api/v2/en/comparison-table/?product=WRIKE"
        page_data = data.get(comp_key, {})
        for widget in page_data.get("widgets", []):
            if widget.get("class_name") == "pricing_comparison_widget":
                return widget
        return None

    def _parse_pricing_cards(self, widget: dict) -> list[dict]:
        """Extract plan pricing from the pricing cards."""
        plans = []
        pricing_tabs = widget.get("pricingWidget", {}).get("pricingTabs", [])

        for tab in pricing_tabs:
            cards = tab.get("pricingCards", [])
            if not isinstance(cards, list):
                continue

            for card_wrapper in cards:
                card = card_wrapper.get("pricingCards", card_wrapper)
                plan_name = card.get("planName", "")
                slug = PLAN_SLUG_MAP.get(plan_name, plan_name.lower())
                amount_str = card.get("amount", "")
                price_desc = card.get("priceDescription", "")

                plan: dict[str, Any] = {
                    "name": plan_name,
                    "slug": slug,
                    "is_free": slug == "free",
                    "is_custom_pricing": amount_str is None or amount_str == "" or "contact" in (amount_str or "").lower(),
                    "features": {},
                }

                if plan["is_free"]:
                    plan["pricing"] = None
                elif not plan["is_custom_pricing"] and amount_str:
                    price = float(re.sub(r'[^\d.]', '', amount_str))
                    plan["pricing"] = PricingInfo(
                        annual_per_unit=price,
                        monthly_per_unit=None,
                        unit=BillingUnit.USER,
                    ).model_dump()
                else:
                    plan["pricing"] = None
                    plan["is_custom_pricing"] = True

                # Trial info
                if not plan["is_free"]:
                    plan["trial"] = TrialInfo(days=14, credit_card_required=False).model_dump()

                plans.append(plan)

        return plans

    def _get_plan_names_from_table(self, widget: dict) -> list[str]:
        """Get the plan column names from the first table header."""
        blocks = widget.get("contentBlocks", [])
        for i in range(1, len(blocks), 2):
            table_html = blocks[i].get("data", {}).get("tableLayout", "")
            soup = BeautifulSoup(table_html, "html.parser")
            for row in soup.find_all("tr"):
                cells = row.find_all("td")
                texts = [c.get_text(strip=True) for c in cells]
                if texts and texts[0] == "Features":
                    return texts[1:]
        return []

    def _parse_comparison_table(self, widget: dict) -> dict[str, list[dict]]:
        """Parse all feature categories and their rows from the comparison table."""
        blocks = widget.get("contentBlocks", [])
        categories: dict[str, list[dict]] = {}

        for i in range(0, len(blocks), 2):
            # Header block
            header_html = blocks[i].get("content", "")
            soup = BeautifulSoup(header_html, "html.parser")
            cat_name = soup.get_text(strip=True)

            # Skip footnotes, empty headers
            if not cat_name or len(cat_name) > 100 or cat_name.startswith("*"):
                continue

            # Data block
            if i + 1 >= len(blocks):
                continue
            data_block = blocks[i + 1].get("data", {})
            table_html = data_block.get("tableLayout", "")

            features = self._parse_table_html(table_html)
            if features:
                categories[cat_name] = features

        return categories

    def _parse_table_html(self, table_html: str) -> list[dict]:
        """Parse a single HTML comparison table into feature rows."""
        soup = BeautifulSoup(table_html, "html.parser")
        rows = soup.find_all("tr")

        plan_names = []
        features = []

        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue

            first_cell = cells[0]
            clean_name = self._extract_feature_name(first_cell)
            cell_texts = [c.get_text(strip=True) for c in cells]

            # First row is header
            if cell_texts[0] == "Features" or clean_name == "Features":
                plan_names = cell_texts[1:]
                continue

            if clean_name:
                values = dict(zip(plan_names, cell_texts[1:]))
                features.append({"name": clean_name, "values": values})

        return features

    def _extract_feature_name(self, cell) -> str:
        """Extract just the feature name from a table cell, excluding tooltip descriptions.

        Wrike's cells have this structure:
        <td>
          <span class="website-wysiwyg__text-for-tooltip">
            Feature Name
            <span class="website-wysiwyg__tooltip">Description...</span>
          </span>
        </td>
        OR simply:
        <td>Feature Name</td>
        OR:
        <td><a href="...">Feature Name</a></td>
        """
        # First: remove all tooltip spans from the cell before extracting text
        for tooltip in cell.find_all("span", class_=lambda c: c and "tooltip" in c and "text-for" not in c):
            tooltip.decompose()

        # Now get text from the cleaned cell
        # For "text-for-tooltip" spans, only get direct text (not nested spans)
        text_for_tooltip = cell.find("span", class_=lambda c: c and "text-for-tooltip" in c)
        if text_for_tooltip:
            # Get only direct text nodes from this span
            parts = []
            for child in text_for_tooltip.children:
                if isinstance(child, str):
                    text = child.strip()
                    if text:
                        parts.append(text)
            name = " ".join(parts).strip()
            if name:
                return name

        # For <a> tags, get their text
        link = cell.find("a")
        if link:
            return link.get_text(strip=True)

        # Direct text
        return cell.get_text(strip=True)

    def _parse_add_ons(self, features_by_category: dict) -> list[WrikeAddOn]:
        """Extract add-ons from the 'Add-On Capabilities' category."""
        add_on_cat = None
        for cat_name, features in features_by_category.items():
            if "add-on" in cat_name.lower():
                add_on_cat = features
                break

        if not add_on_cat:
            return []

        add_ons = []
        for feat in add_on_cat:
            eligible = []
            for plan, val in feat.get("values", {}).items():
                if val != "–" and val != "-":
                    slug = PLAN_SLUG_MAP.get(plan, plan.lower())
                    eligible.append(slug)

            add_ons.append(WrikeAddOn(
                name=feat["name"],
                eligible_plans=eligible,
            ))

        return add_ons

    # Override — we don't need AI for Wrike
    def get_extraction_prompt(self) -> str:
        return ""  # Not used — direct parsing
