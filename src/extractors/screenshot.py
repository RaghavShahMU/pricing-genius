"""Screenshot capture module using Playwright.

Captures full-page screenshots of competitor pricing pages.
Handles page-specific interactions (expanding toggles, scrolling).

Designed to run on Linux (GitHub Actions). On macOS where Playwright
may have issues, falls back gracefully and returns None.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

# Directory to store screenshots
SCREENSHOTS_DIR = Path(__file__).parent.parent.parent / "data" / "screenshots"

# Per-competitor screenshot configuration
SCREENSHOT_CONFIGS = {
    "smartsheet": {
        "urls": [
            {"url": "https://www.smartsheet.com/pricing", "name": "pricing"},
        ],
    },
    "wrike": {
        "urls": [
            {"url": "https://www.wrike.com/comparison-table/", "name": "comparison"},
        ],
    },
    "asana": {
        "urls": [
            {"url": "https://asana.com/pricing", "name": "pricing"},
        ],
    },
    "notion": {
        "urls": [
            {"url": "https://www.notion.com/pricing", "name": "pricing"},
        ],
    },
    "monday": {
        "urls": [
            {"url": "https://monday.com/pricing", "name": "pricing"},
        ],
        "pre_screenshot_actions": [
            # Expand the "Compare all features" toggle
            {"action": "click", "selector": "text=Compare all features", "optional": True},
            {"action": "wait", "ms": 2000},
            # Expand all collapsed sections
            {"action": "expand_all_sections"},
        ],
    },
}


async def capture_screenshots(competitor: str) -> list[Path] | None:
    """Capture full-page screenshots for a competitor.

    Returns list of screenshot paths, or None if Playwright unavailable.
    """
    config = SCREENSHOT_CONFIGS.get(competitor)
    if not config:
        logger.warning(f"No screenshot config for {competitor}")
        return None

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Build the Playwright script as a standalone Python file
    # This runs in a subprocess to avoid Python 3.14 async compat issues
    screenshots = []
    for url_config in config["urls"]:
        url = url_config["url"]
        name = url_config["name"]
        output_path = SCREENSHOTS_DIR / f"{competitor}_{name}_{date_str}.png"
        latest_path = SCREENSHOTS_DIR / f"{competitor}_{name}_latest.png"

        pre_actions = config.get("pre_screenshot_actions", [])
        script = _build_screenshot_script(url, str(output_path), str(latest_path), pre_actions)

        success = await _run_playwright_script(script)
        if success and output_path.exists():
            screenshots.append(latest_path)
            logger.info(f"Screenshot captured: {latest_path}")
        else:
            logger.warning(f"Screenshot failed for {competitor}/{name}")

    return screenshots if screenshots else None


def _build_screenshot_script(
    url: str,
    output_path: str,
    latest_path: str,
    pre_actions: list[dict],
) -> str:
    """Build a standalone Playwright script for screenshot capture."""

    actions_code = ""
    for action in pre_actions:
        if action["action"] == "click":
            selector = action["selector"]
            optional = action.get("optional", False)
            if optional:
                actions_code += f"""
    try:
        el = page.query_selector("{selector}")
        if el:
            el.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass
"""
            else:
                actions_code += f"""
    page.click("{selector}")
    page.wait_for_timeout(1000)
"""
        elif action["action"] == "wait":
            ms = action["ms"]
            actions_code += f"    page.wait_for_timeout({ms})\n"
        elif action["action"] == "expand_all_sections":
            actions_code += """
    # Expand all collapsed/accordion sections
    try:
        expandables = page.query_selector_all('[aria-expanded="false"]')
        for el in expandables[:30]:
            try:
                el.click()
                page.wait_for_timeout(300)
            except Exception:
                pass
        page.wait_for_timeout(2000)
    except Exception:
        pass
"""

    return f'''
import shutil
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    try:
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={{"width": 1440, "height": 900}},
        )
        page = context.new_page()
        page.goto("{url}", wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(3000)

        # Pre-screenshot actions
{actions_code}

        # Scroll to bottom to trigger lazy-loaded content
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        # Full page screenshot
        page.screenshot(path="{output_path}", full_page=True)

        # Copy to latest
        shutil.copy2("{output_path}", "{latest_path}")

        print("SUCCESS")
    finally:
        browser.close()
'''


async def _run_playwright_script(script: str) -> bool:
    """Run a Playwright script in a subprocess. Returns True on success."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        proc = await asyncio.create_subprocess_exec(
            "python", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

        if proc.returncode == 0 and b"SUCCESS" in stdout:
            return True

        # Log failure details
        stderr_text = stderr.decode()[:500] if stderr else ""
        logger.warning(f"Playwright script failed (rc={proc.returncode}): {stderr_text}")
        return False

    except asyncio.TimeoutError:
        logger.warning("Playwright script timed out")
        return False
    except FileNotFoundError:
        logger.warning("Python not found for Playwright subprocess")
        return False
    finally:
        os.unlink(script_path)
