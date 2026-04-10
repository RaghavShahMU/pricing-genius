# Pricing Genius

Competitive pricing intelligence tool for ClickUp. Tracks pricing and packaging data for project management competitors and exposes it via MCP endpoints.

## Competitors Tracked

| Competitor | Pricing Page |
|-----------|-------------|
| Smartsheet | https://www.smartsheet.com/pricing |
| Wrike | https://www.wrike.com/price/ |
| Asana | https://asana.com/pricing |
| Notion | https://www.notion.com/pricing |
| Monday.com | https://monday.com/pricing |

## Quick Start

```bash
# Install dependencies
pip install -r requirements-dev.txt
playwright install chromium

# Seed initial data
python scripts/seed_data.py

# Run MCP server locally
python src/server.py

# Run extraction
python scripts/extract_all.py

# Run tests
pytest tests/
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_competitor_pricing(competitor)` | Full pricing data for one competitor |
| `compare_tiers(competitors, tier_type)` | Cross-competitor tier comparison |
| `get_price_range(seats, billing)` | Cost per competitor for given seat count |
| `search_features(feature)` | Search which tiers include a feature |
| `list_competitors()` | List all tracked competitors |

## Architecture

- **Data extraction**: Playwright + BeautifulSoup (Python-first), Gemini 2.5 Flash fallback
- **Storage**: Structured JSON files in `data/`
- **MCP server**: FastMCP with streamable-http transport
- **Deployment**: GCP Cloud Run
- **Automation**: GitHub Actions daily extraction at 12:00 AM IST

## Data Schema

Each competitor has a dedicated Pydantic schema in `src/schemas/` reflecting their unique pricing structure. Shared types are in `src/schemas/common.py`.
