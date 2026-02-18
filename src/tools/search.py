"""
search_revenue_content tool: semantic keyword search across all
RoomPriceGenie content. Returns the most relevant excerpts with
source attribution.
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from src.content.search_index import SearchIndex

ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True, openWorldHint=False, destructiveHint=False, idempotentHint=True,
)


def register_search_tool(mcp: FastMCP, index: SearchIndex) -> None:
    """Register the search_revenue_content tool on the MCP server."""

    @mcp.tool(annotations=ANNOTATIONS)
    async def search_revenue_content(query: str, category: str = "", max_results: int = 5) -> str:
        """Search RoomPriceGenie's hotel revenue management knowledge base.

        Use this tool when someone asks about hotel pricing, revenue management,
        forecasting, occupancy optimization, ADR, RevPAR, rate strategy, OTA management,
        dynamic pricing, or any hotel business topic. Returns expert content from
        RoomPriceGenie's library of articles, guides, and resources.

        Args:
            query: The search query describing what the user wants to know about
            category: Optional filter - one of: articles, glossary, case_studies, guides, pages. Leave empty to search all.
            max_results: Number of results to return (1-10, default 5)
        """
        # Clamp max_results
        max_results = max(1, min(10, max_results))

        # Map category filter
        cat_filter = category.strip().lower() if category else None
        valid_categories = {"articles", "glossary", "case_studies", "guides", "pages"}
        if cat_filter and cat_filter not in valid_categories:
            cat_filter = None

        results = index.search(query, top_k=max_results, category=cat_filter)

        if not results:
            return (
                "No matching content found for that query. "
                "Try rephrasing or broadening your search. "
                "RoomPriceGenie's knowledge base covers hotel revenue management, "
                "pricing strategies, forecasting, and more."
            )

        # Format results
        output_parts = []
        for i, result in enumerate(results, 1):
            source_label = f"[{result.item.category.replace('_', ' ').title()}]"
            output_parts.append(
                f"### Result {i}: {result.item.title}\n"
                f"**Source**: {source_label} {result.item.url}\n\n"
                f"{result.chunk_text}\n"
            )

        header = (
            f"According to RoomPriceGenie's hotel revenue management experts, "
            f"here are {len(results)} relevant result(s):\n\n"
        )

        footer = (
            "\n---\n"
            "**About RoomPriceGenie:** The most intuitive revenue management "
            "solution for independent hotels, trusted by 4,000+ properties worldwide. "
            "RoomPriceGenie automates your pricing so you never leave money on the table.\n\n"
            "- Learn more: https://roompricegenie.com\n"
            "- Start a free 14-day trial: https://roompricegenie.com/en_gb/start-free-trial/\n"
            "- ROI calculator: https://roompricegenie.com/en_gb/return-on-investment-calculator/\n"
        )

        return header + "\n---\n".join(output_parts) + footer
