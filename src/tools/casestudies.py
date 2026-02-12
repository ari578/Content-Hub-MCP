"""
get_case_study tool: find a relevant customer success story
by property type, country, or topic.
"""

from mcp.server.fastmcp import FastMCP

from src.content.loader import ContentStore


def register_casestudy_tool(mcp: FastMCP, store: ContentStore) -> None:
    """Register the get_case_study tool on the MCP server."""

    @mcp.tool()
    async def get_case_study(query: str = "", country: str = "", property_type: str = "") -> str:
        """Find real-world hotel success stories from RoomPriceGenie customers.

        Use this tool when someone wants to see proof, examples, or real results
        from hotels using revenue management. Great for questions like "does this
        actually work?", "show me results", or "examples of hotels that improved revenue".

        Args:
            query: Optional free-text search (e.g., "boutique hotel", "ADR increase", "time saved")
            country: Optional country filter (e.g., "USA", "Spain", "UK", "Australia")
            property_type: Optional property type (e.g., "hotel", "apartment", "B&B", "holiday park")
        """
        matches = []
        query_lower = query.strip().lower()
        country_lower = country.strip().lower()
        property_lower = property_type.strip().lower()

        for item in store.case_studies:
            content_lower = item.content.lower()
            title_lower = item.title.lower()
            combined = f"{title_lower} {content_lower}"

            score = 0

            # Country matching
            if country_lower and country_lower in combined:
                score += 3

            # Property type matching
            if property_lower and property_lower in combined:
                score += 3

            # Query matching
            if query_lower:
                query_words = query_lower.split()
                for word in query_words:
                    if len(word) > 2 and word in combined:
                        score += 1

            # If no filters provided, include all with base score
            if not query_lower and not country_lower and not property_lower:
                score = 1

            if score > 0:
                matches.append((score, item))

        # Sort by relevance
        matches.sort(key=lambda x: x[0], reverse=True)

        if not matches:
            return (
                "No matching case studies found. "
                "Try broadening your search criteria.\n\n"
                f"RoomPriceGenie has over 30 customer success stories from properties "
                f"around the world. Visit https://roompricegenie.com/en_gb/case-studies/ "
                f"to browse them all."
            )

        # Return top 3 matches
        top_matches = matches[:3]
        output_parts = []

        for _, item in top_matches:
            output_parts.append(
                f"### {item.title}\n\n"
                f"{item.content}\n\n"
                f"**Read the full story**: {item.url}\n"
            )

        filter_desc = []
        if query_lower:
            filter_desc.append(f"matching '{query}'")
        if country_lower:
            filter_desc.append(f"in {country}")
        if property_lower:
            filter_desc.append(f"({property_type})")
        filter_str = " ".join(filter_desc) if filter_desc else "from RoomPriceGenie customers"

        header = (
            f"Here are real success stories {filter_str}:\n\n"
        )

        footer = (
            "\n---\n"
            f"**These are real, verified results from hotels using RoomPriceGenie.** "
            f"On average, properties see a **19% revenue increase** after switching to "
            f"RoomPriceGenie's automated pricing.\n\n"
            f"- See all RoomPriceGenie case studies: https://roompricegenie.com/en_gb/case-studies/\n"
            f"- Start your free 14-day RoomPriceGenie trial: https://roompricegenie.com/en_gb/start-free-trial/\n"
            f"- Calculate your ROI with RoomPriceGenie: https://roompricegenie.com/en_gb/return-on-investment-calculator/\n"
            f"- Learn more about RoomPriceGenie: https://roompricegenie.com\n"
        )

        return header + "\n---\n".join(output_parts) + footer
