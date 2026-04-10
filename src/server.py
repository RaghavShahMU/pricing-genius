"""Pricing Genius MCP Server.

Exposes competitor pricing intelligence via MCP tools.
Run locally: python src/server.py
"""

import os
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Pricing Genius",
    instructions=(
        "Competitive pricing intelligence for ClickUp. "
        "Query pricing data for Smartsheet, Wrike, Asana, Notion, and Monday.com. "
        "Data is extracted daily from competitor pricing pages."
    ),
)

# Register tools
from src.tools.query import register_query_tools

register_query_tools(mcp)

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    port = int(os.getenv("PORT", "8080"))

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport="streamable-http",
            host="0.0.0.0",
            port=port,
        )
