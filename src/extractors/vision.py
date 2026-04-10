"""AI Vision extraction using Gemini 2.5 Flash.

Sends screenshots to Gemini's Vision API to extract pricing data.
This is the primary extraction method for most competitors because:
- What you see is what you get — no hidden HTML, no JS rendering issues
- AI reads the comparison table exactly as a human would
- Resilient to UI changes (reads visual layout, not CSS selectors)

Anti-hallucination measures:
1. Screenshot-based = AI can only extract what's visually present
2. Explicit rules: "null if unclear, never guess"
3. Feature count bounds checked after extraction
4. Prices cross-verified with code extraction
5. Historical diff flagging (>20% change = review)
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Minimum expected features per competitor (triggers warning if below)
MIN_FEATURE_COUNTS = {
    "smartsheet": 40,
    "wrike": 60,
    "asana": 50,
    "notion": 30,
    "monday": 50,
}


async def extract_from_screenshot(
    screenshot_path: Path,
    competitor: str,
    schema_json: str,
) -> dict[str, Any]:
    """Extract pricing data from a screenshot using Gemini Vision.

    Args:
        screenshot_path: Path to the full-page screenshot PNG
        competitor: Competitor slug
        schema_json: JSON schema string for the expected output

    Returns:
        Extracted data as a dict matching the schema
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("No GEMINI_API_KEY or GOOGLE_API_KEY set")

    import google.generativeai as genai

    genai.configure(api_key=api_key)

    # Read and encode the screenshot
    image_bytes = screenshot_path.read_bytes()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Build the extraction prompt
    prompt = _build_vision_prompt(competitor, schema_json)

    logger.info(
        f"Sending screenshot ({len(image_bytes)} bytes) to Gemini Vision "
        f"for {competitor}"
    )

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = await model.generate_content_async(
        [
            {"mime_type": "image/png", "data": image_b64},
            prompt,
        ],
        generation_config=genai.GenerationConfig(
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    result = _parse_json_response(response.text)

    # Override metadata — don't trust AI to copy these correctly
    result["competitor"] = competitor
    result["extracted_at"] = datetime.now(timezone.utc).isoformat()
    result["extraction_method"] = "ai"
    result["data_version"] = 1

    # Validate feature count
    total_features = _count_features(result, competitor)
    min_expected = MIN_FEATURE_COUNTS.get(competitor, 20)
    if total_features < min_expected:
        logger.warning(
            f"Low feature count for {competitor}: {total_features} "
            f"(expected >= {min_expected}). AI may have missed rows."
        )

    return result


def _build_vision_prompt(competitor: str, schema_json: str) -> str:
    """Build the extraction prompt for Gemini Vision."""

    competitor_instructions = COMPETITOR_PROMPTS.get(competitor, "")

    return f"""You are a precise data extraction system. You are looking at a screenshot of a pricing page.

## TASK
Extract ALL pricing and feature data visible in this screenshot into structured JSON.

## COMPETITOR: {competitor}

{competitor_instructions}

## CRITICAL RULES — READ EVERY ONE

### Prices
- All prices in USD, per-unit, per-MONTH
- "monthly_per_unit" = price when billed month-to-month (higher number)
- "annual_per_unit" = price per month when billed annually (lower number)
- Most SaaS: $5-$60/user/month. If you read >$100/user/month, recheck.
- "Contact Sales" / "Custom" → is_custom_pricing: true, pricing: null
- Free plans → is_free: true, pricing: null

### Features — BE EXHAUSTIVE
- Extract EVERY SINGLE ROW from every comparison table visible
- Each row is a feature. Read every column (one per plan tier).
- Checkmark (✓) → available: true
- Dash (—) or empty → available: false
- Specific text/number → available: true, value: "the text"
- If a cell has a number like "250/month" or "5 GB", capture it as the value
- Group features by their section headers (e.g., "Essentials", "Collaboration")

### DO NOT
- Do NOT invent features that aren't visible in the screenshot
- Do NOT guess values you can't read clearly — use null instead
- Do NOT skip rows because they seem similar to others
- Do NOT merge multiple features into one

### Section Headers
- The comparison table has section headers (bold text rows spanning all columns)
- Use these as feature category names
- Extract ALL sections, even if partially visible

## JSON SCHEMA
Output must conform to this schema:
```json
{schema_json}
```

## METADATA (include these exact values)
- display_name: use the proper capitalized name
- url: the pricing page URL for this competitor

## OUTPUT
Return ONLY valid JSON. No markdown, no explanation.
"""


COMPETITOR_PROMPTS = {
    "smartsheet": """### Smartsheet Specifics
- Plans: Pro, Business, Enterprise, Advanced Work Management (AWM)
- Prices are "per Member/month"
- Look for the full comparison table below the pricing cards
- Extract add-ons (Brandfolder, Resource Management, Dynamic View, etc.)
- Extract support tiers (Standard, Premium, TAM)
- url: "https://www.smartsheet.com/pricing"
""",
    "wrike": """### Wrike Specifics
- Plans: Free, Team, Business, Enterprise, Pinnacle, Apex
- Prices are "per user/month"
- The comparison table is very detailed with 10+ categories
- url: "https://www.wrike.com/price/"
""",
    "asana": """### Asana Specifics
- Plans: Personal (free), Starter, Advanced, Enterprise, Enterprise+
- Prices are "per user/month"
- Look for both the pricing cards AND the comparison table below
- Enterprise/Enterprise+ are "Contact Sales"
- url: "https://asana.com/pricing"
""",
    "notion": """### Notion Specifics
- Plans: Free, Plus, Business, Enterprise
- Prices are "per member/month"
- Extract Notion-specific limits: file upload limit, page history days,
  external guests count, charts count, notion.site domains, AI data retention days
- Extract add-ons (AI Add-on, Custom Agents, Custom Domains)
- url: "https://www.notion.com/pricing"
""",
    "monday": """### Monday.com Specifics
- Focus on Work Management product only
- Plans: Free, Basic, Standard, Pro, Enterprise
- Prices are "per seat/month" — minimum 3 seats on paid plans
- The comparison table has MANY sections: Essentials, Collaboration,
  Productivity, Views and reporting, Resource management, Security & privacy,
  Administration & control, Advanced reporting & analytics, Support
- There are 50+ features across these sections — extract ALL of them
- Each cell shows: checkmark, dash, or a specific value (e.g., "250/month", "5 GB")
- url: "https://monday.com/pricing"
""",
}


def _parse_json_response(text: str) -> dict[str, Any]:
    """Parse JSON from AI response with repair for common issues."""
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip markdown fences
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Brace matching
    start = text.find("{")
    if start == -1:
        raise RuntimeError(f"No JSON object in response. Preview: {text[:300]}")

    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    json_str = text[start:end]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Try truncating at last valid brace
    for i in range(len(json_str) - 1, 0, -1):
        if json_str[i] == "}":
            try:
                return json.loads(json_str[: i + 1])
            except json.JSONDecodeError:
                continue

    raise RuntimeError(f"Could not parse JSON. Length: {len(text)}")


def _count_features(data: dict, competitor: str) -> int:
    """Count total features across all plans."""
    total = 0
    if competitor == "monday":
        for product in data.get("products", []):
            for plan in product.get("plans", []):
                for feats in (plan.get("features") or {}).values():
                    total += len(feats)
    else:
        for plan in data.get("plans", []):
            for feats in (plan.get("features") or {}).values():
                total += len(feats)
    return total
