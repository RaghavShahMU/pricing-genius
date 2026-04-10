"""JSON file storage for competitor pricing data.

Reads and writes structured JSON files in the data/ directory.
Each competitor has its own JSON file (e.g., data/smartsheet.json).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from src.schemas.asana import AsanaPricing
from src.schemas.monday import MondayPricing
from src.schemas.notion import NotionPricing
from src.schemas.smartsheet import SmartsheetPricing
from src.schemas.wrike import WrikePricing

DATA_DIR = Path(__file__).parent.parent.parent / "data"

COMPETITOR_SCHEMAS: dict[str, type[BaseModel]] = {
    "smartsheet": SmartsheetPricing,
    "wrike": WrikePricing,
    "asana": AsanaPricing,
    "notion": NotionPricing,
    "monday": MondayPricing,
}

COMPETITOR_SLUGS = list(COMPETITOR_SCHEMAS.keys())


def get_data_path(competitor: str) -> Path:
    """Get the JSON file path for a competitor."""
    if competitor not in COMPETITOR_SCHEMAS:
        raise ValueError(f"Unknown competitor: {competitor}. Valid: {COMPETITOR_SLUGS}")
    return DATA_DIR / f"{competitor}.json"


def load_competitor(competitor: str) -> BaseModel:
    """Load and validate competitor pricing data from JSON."""
    path = get_data_path(competitor)
    if not path.exists():
        raise FileNotFoundError(f"No data file for {competitor} at {path}")

    with open(path) as f:
        raw = json.load(f)

    schema_cls = COMPETITOR_SCHEMAS[competitor]
    return schema_cls.model_validate(raw)


def load_competitor_raw(competitor: str) -> dict[str, Any]:
    """Load competitor data as raw dict (no validation)."""
    path = get_data_path(competitor)
    if not path.exists():
        raise FileNotFoundError(f"No data file for {competitor} at {path}")

    with open(path) as f:
        return json.load(f)


def save_competitor(competitor: str, data: BaseModel) -> Path:
    """Save competitor pricing data to JSON. Validates before writing."""
    path = get_data_path(competitor)
    schema_cls = COMPETITOR_SCHEMAS[competitor]

    if not isinstance(data, schema_cls):
        raise TypeError(f"Expected {schema_cls.__name__}, got {type(data).__name__}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    json_str = data.model_dump_json(indent=2)
    path.write_text(json_str)
    return path


def list_competitors() -> list[dict[str, Any]]:
    """List all competitors with their data file status."""
    result = []
    for slug in COMPETITOR_SLUGS:
        path = get_data_path(slug)
        info = {
            "competitor": slug,
            "display_name": COMPETITOR_SCHEMAS[slug].__name__.replace("Pricing", ""),
            "has_data": path.exists(),
            "file_path": str(path),
        }
        if path.exists():
            try:
                data = load_competitor(slug)
                info["extracted_at"] = data.extracted_at.isoformat()
                info["extraction_method"] = data.extraction_method.value
            except Exception as e:
                info["error"] = str(e)
        result.append(info)
    return result
