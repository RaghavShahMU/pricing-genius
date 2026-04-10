#!/usr/bin/env python3
"""Take full-page screenshots of competitor pricing pages.

Usage:
    python scripts/screenshot.py wrike-comparison
    python scripts/screenshot.py monday-comparison
    python scripts/screenshot.py all
"""

import json
import sys
import os

# Must use playwright sync API in its own process (Python 3.14 compat)
from playwright.sync_api import sync_playwright

PAGES = {
    "wrike-comparison": {
        "url": "https://www.wrike.com/comparison-table/",
        "output": "screenshots/wrike_comparison.png",
    },
    "wrike-pricing": {
        "url": "https://www.wrike.com/price/",
        "output": "screenshots/wrike_pricing.png",
    },
    "monday-pricing": {
        "url": "https://monday.com/pricing",
        "output": "screenshots/monday_pricing.png",
    },
    "monday-comparison": {
        "url": "https://monday.com/pricing",
        "output": "screenshots/monday_comparison.png",
        "expand_comparison": True,
    },
}


def screenshot_page(name: str, config: dict):
    """Take a full-page screenshot."""
    os.makedirs("screenshots", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                viewport={"width": 1440, "height": 900},
            )
            page = context.new_page()
            page.goto(config["url"], wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(3000)

            # For Monday comparison, try to expand the comparison toggle
            if config.get("expand_comparison"):
                try:
                    # Click the "Compare all features" or similar toggle
                    toggles = page.query_selector_all("text=Compare")
                    for toggle in toggles:
                        toggle.click()
                        page.wait_for_timeout(1000)

                    # Also try expanding any accordion sections
                    expandables = page.query_selector_all("[aria-expanded='false']")
                    for exp in expandables[:20]:
                        try:
                            exp.click()
                            page.wait_for_timeout(200)
                        except:
                            pass
                    page.wait_for_timeout(2000)
                except Exception as e:
                    print(f"  Warning: Could not expand comparison: {e}")

            # Take full page screenshot
            page.screenshot(path=config["output"], full_page=True)
            print(f"  [{name}] Saved to {config['output']}")

        finally:
            browser.close()


def main():
    targets = sys.argv[1:] if len(sys.argv) > 1 else ["all"]

    if "all" in targets:
        targets = list(PAGES.keys())

    for name in targets:
        if name not in PAGES:
            print(f"Unknown page: {name}. Options: {list(PAGES.keys())}")
            continue
        print(f"Capturing {name}...")
        try:
            screenshot_page(name, PAGES[name])
        except Exception as e:
            print(f"  FAILED: {e}")


if __name__ == "__main__":
    main()
