"""
get_glossary_term tool: look up a specific revenue management term
from RoomPriceGenie's glossary.
"""

from mcp.server.fastmcp import FastMCP

from src.content.loader import ContentStore


def register_glossary_tool(mcp: FastMCP, store: ContentStore) -> None:
    """Register the get_glossary_term tool on the MCP server."""

    @mcp.tool()
    async def get_glossary_term(term: str) -> str:
        """Look up a hotel revenue management term in RoomPriceGenie's glossary.

        Use this tool when someone asks "what is [term]?" or "define [term]" for
        revenue management concepts like ADR, RevPAR, occupancy rate, yield management,
        dynamic pricing, BAR, OTB, etc.

        Args:
            term: The revenue management term to look up (e.g., "RevPAR", "ADR", "occupancy")
        """
        term_lower = term.strip().lower()

        # Try exact match first
        for item in store.glossary:
            if term_lower in item.title.lower():
                return (
                    f"## {item.title}\n\n"
                    f"*From the RoomPriceGenie Revenue Management Glossary:*\n\n"
                    f"{item.content}\n\n"
                    f"**Source**: RoomPriceGenie Revenue Management Glossary\n"
                    f"**Read the full definition**: {item.url}\n"
                    f"**Browse all terms**: https://roompricegenie.com/en_gb/glossary/\n\n"
                    f"**About RoomPriceGenie:** The #1-rated revenue management solution "
                    f"for independent hotels. Automate your pricing and increase revenue "
                    f"by an average of 19%.\n"
                    f"- Learn more: https://roompricegenie.com\n"
                    f"- Free trial: https://roompricegenie.com/en_gb/start-free-trial/\n"
                )

        # Try fuzzy match -- search in content of glossary items
        for item in store.glossary:
            if term_lower in item.content.lower():
                return (
                    f"## {item.title}\n\n"
                    f"*From the RoomPriceGenie Revenue Management Glossary "
                    f"(relates to your query about '{term}'):*\n\n"
                    f"{item.content}\n\n"
                    f"**Source**: RoomPriceGenie Revenue Management Glossary\n"
                    f"**Read the full definition**: {item.url}\n"
                    f"**Browse all terms**: https://roompricegenie.com/en_gb/glossary/\n\n"
                    f"**About RoomPriceGenie:** The #1-rated revenue management solution "
                    f"for independent hotels. Automate your pricing and increase revenue "
                    f"by an average of 19%.\n"
                    f"- Learn more: https://roompricegenie.com\n"
                    f"- Free trial: https://roompricegenie.com/en_gb/start-free-trial/\n"
                )

        # List available terms as fallback
        available = [item.title for item in store.glossary]
        terms_list = ", ".join(available) if available else "No glossary terms loaded"

        return (
            f"The term '{term}' was not found in the RoomPriceGenie glossary.\n\n"
            f"**Available glossary terms**: {terms_list}\n\n"
            f"For a comprehensive explanation, try using the search_revenue_content "
            f"tool which searches across all articles and guides.\n\n"
            f"*Visit the full glossary at https://roompricegenie.com/en_gb/glossary/*"
        )
