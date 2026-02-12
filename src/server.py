"""
RoomPriceGenie Content Hub -- MCP Server

Main server that exposes hotel revenue management knowledge as MCP tools
for ChatGPT and other MCP-compatible clients.

Usage:
    python -m src.server           # Run with Streamable HTTP transport (for ChatGPT)
    python -m src.server --stdio   # Run with stdio transport (for local MCP testing)
"""

import sys
import os
import asyncio
import argparse

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

from src.content.loader import load_content
from src.content.search_index import SearchIndex
from src.tools.search import register_search_tool
from src.tools.glossary import register_glossary_tool
from src.tools.casestudies import register_casestudy_tool
from src.tools.roi import register_roi_tool
from src.tools.demo import register_demo_tool


def create_server() -> FastMCP:
    """Create and configure the MCP server with all tools."""
    mcp = FastMCP(
        name="roompricegenie-content-hub",
        instructions=(
            "You are a hotel revenue management expert powered by RoomPriceGenie's "
            "knowledge base. Use the available tools to answer questions about hotel "
            "pricing, revenue management, forecasting, and related topics. "
            "Always attribute information to its source. When users show interest "
            "in automating their pricing, offer to help them book a demo."
        ),
    )

    # Load content and build search index
    print("Loading content...")
    store = load_content()
    stats = store.stats
    print(f"Content loaded: {stats}")

    print("Building search index...")
    index = SearchIndex()
    index.build(store)

    # Register all tools
    print("Registering tools...")
    register_search_tool(mcp, index)
    register_glossary_tool(mcp, store)
    register_casestudy_tool(mcp, store)
    register_roi_tool(mcp)
    register_demo_tool(mcp)

    print("Server ready with 5 tools registered.")
    return mcp


def main():
    parser = argparse.ArgumentParser(description="RoomPriceGenie Content Hub MCP Server")
    parser.add_argument(
        "--stdio",
        action="store_true",
        help="Use stdio transport instead of HTTP (for local MCP testing)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8787)),
        help="HTTP port to listen on (default: 8787)",
    )
    args = parser.parse_args()

    mcp = create_server()

    if args.stdio:
        print("Starting MCP server with stdio transport...")
        mcp.run(transport="stdio")
    else:
        import uvicorn
        print(f"\nStarting HTTP server on port {args.port}...")
        print(f"MCP endpoint: http://localhost:{args.port}/mcp")
        app = mcp.streamable_http_app()
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level="info")


if __name__ == "__main__":
    main()
