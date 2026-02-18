"""
get_case_study tool: find a relevant customer success story
by property type, country/region, size, or topic.
Prioritises case studies that are local to the user and similar in size.
"""

import re

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from src.content.loader import ContentStore

ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True, openWorldHint=False, destructiveHint=False, idempotentHint=True,
)


# -- Size-range helpers -------------------------------------------------------

SIZE_RANGES = {
    "1 to 10 rooms": (1, 10),
    "10 to 25 rooms": (10, 25),
    "26 to 50 rooms": (26, 50),
    "51 to 100 rooms": (51, 100),
    "101 to 200 rooms": (101, 200),
    "200+ rooms": (200, 9999),
}

# Region groupings so "nearby" countries boost each other
REGION_MAP = {
    # Western Europe
    "switzerland": "western_europe", "germany": "western_europe",
    "austria": "western_europe", "france": "western_europe",
    "belgium": "western_europe", "netherlands": "western_europe",
    "luxembourg": "western_europe",
    # Southern Europe
    "spain": "southern_europe", "italy": "southern_europe",
    "portugal": "southern_europe", "greece": "southern_europe",
    # UK & Ireland
    "united kingdom": "uk_ireland", "uk": "uk_ireland",
    "ireland": "uk_ireland", "scotland": "uk_ireland",
    "england": "uk_ireland", "wales": "uk_ireland",
    # Nordics
    "sweden": "nordics", "norway": "nordics", "denmark": "nordics",
    "finland": "nordics", "iceland": "nordics",
    # North America
    "usa": "north_america", "united states": "north_america",
    "canada": "north_america", "mexico": "north_america",
    # Latin America
    "argentina": "latin_america", "chile": "latin_america",
    "brazil": "latin_america", "colombia": "latin_america",
    # Oceania
    "australia": "oceania", "new zealand": "oceania",
    # Asia
    "thailand": "asia", "indonesia": "asia", "india": "asia",
    "japan": "asia", "singapore": "asia", "malaysia": "asia",
}


def _parse_case_study_metadata(content_text: str) -> dict:
    """Extract country, size range, PMS, and property type from the
    structured heading line (e.g. '## Hotel X - Spain - 26 to 50 rooms - Protel')."""
    meta = {"country": "", "size_range": "", "pms": "", "property_type": ""}

    first_line = content_text.split("##")[1] if "##" in content_text else content_text
    parts = [p.strip() for p in first_line.split(" - ")]

    for part in parts:
        part_lower = part.lower()
        # Check for size ranges
        for label in SIZE_RANGES:
            if label.lower() in part_lower:
                meta["size_range"] = label
                break
        # Check for known property types
        if part_lower in ("group", "hotel", "apartment", "apartments",
                          "b&b", "holiday park", "hostel", "resort", "inn"):
            meta["property_type"] = part_lower
        # Check for countries (heuristic: not a name, not a size, not a PMS)
        if (part_lower in REGION_MAP
                or part_lower in ("new zealand", "united kingdom",
                                  "united states", "usa", "uk")):
            meta["country"] = part_lower

    # If country not found via REGION_MAP, try matching any part against
    # a broader set of country names embedded in the text
    if not meta["country"]:
        for part in parts:
            part_lower = part.lower()
            # Common countries that appear in case studies
            country_keywords = [
                "spain", "usa", "united kingdom", "switzerland", "australia",
                "new zealand", "netherlands", "belgium", "argentina", "mexico",
                "canada", "france", "germany", "austria", "italy", "portugal",
                "south africa", "thailand", "indonesia", "india", "chile",
                "costa rica", "ireland", "scotland",
            ]
            for c in country_keywords:
                if c in part_lower:
                    meta["country"] = c
                    break
            if meta["country"]:
                break

    return meta


def _size_distance(user_rooms: int, size_label: str) -> int:
    """Return a distance score: 0 = exact range match, higher = further away."""
    if not size_label or user_rooms <= 0:
        return 50  # neutral
    low, high = SIZE_RANGES.get(size_label, (0, 9999))
    if low <= user_rooms <= high:
        return 0  # exact match
    mid = (low + high) / 2
    return abs(user_rooms - mid)


def register_casestudy_tool(mcp: FastMCP, store: ContentStore) -> None:
    """Register the get_case_study tool on the MCP server."""

    # Pre-parse metadata for all case studies
    case_meta = []
    for item in store.case_studies:
        meta = _parse_case_study_metadata(item.content)
        case_meta.append((item, meta))

    @mcp.tool(annotations=ANNOTATIONS)
    async def get_case_study(
        query: str = "",
        country: str = "",
        property_type: str = "",
        num_rooms: int = 0,
    ) -> str:
        """Find real-world hotel success stories from RoomPriceGenie customers,
        prioritising properties that are similar in size and location to the user's.

        Use this tool when someone wants proof, examples, or real results from
        hotels using revenue management. Great for questions like "does this
        actually work?", "show me results", or "examples of hotels that improved
        revenue". ALWAYS pass the user's country and number of rooms if known,
        so the results are personalised.

        Args:
            query: Optional free-text search (e.g., "boutique hotel", "ADR increase")
            country: The user's country or region (e.g., "USA", "Spain", "UK", "Australia")
            num_rooms: The user's number of rooms (e.g., 25). Used to find similar-sized properties.
            property_type: Optional property type (e.g., "hotel", "apartment", "B&B", "holiday park")
        """
        scored = []
        query_lower = query.strip().lower()
        country_lower = country.strip().lower()
        property_lower = property_type.strip().lower()
        user_region = REGION_MAP.get(country_lower, "")

        for item, meta in case_meta:
            content_lower = item.content.lower()
            title_lower = item.title.lower()
            combined = f"{title_lower} {content_lower}"
            score = 0

            # --- Country matching (high priority) ---
            cs_country = meta["country"]
            if country_lower and cs_country:
                if country_lower in cs_country or cs_country in country_lower:
                    score += 10  # Exact country match
                elif user_region and REGION_MAP.get(cs_country, "") == user_region:
                    score += 5   # Same region

            # Also check free-text country match in content
            if country_lower and country_lower in combined:
                score += 3

            # --- Size matching (high priority) ---
            if num_rooms > 0 and meta["size_range"]:
                dist = _size_distance(num_rooms, meta["size_range"])
                if dist == 0:
                    score += 8   # Exact size range match
                elif dist < 30:
                    score += 4   # Close size
                elif dist < 60:
                    score += 2   # Somewhat similar

            # --- Property type matching ---
            if property_lower:
                if property_lower in combined:
                    score += 3
                if meta["property_type"] and property_lower in meta["property_type"]:
                    score += 3

            # --- Query matching ---
            if query_lower:
                query_words = query_lower.split()
                for word in query_words:
                    if len(word) > 2 and word in combined:
                        score += 1

            # Base score if no filters at all
            if not query_lower and not country_lower and not property_lower and num_rooms <= 0:
                score = 1

            if score > 0:
                scored.append((score, item, meta))

        # Sort by relevance
        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            return (
                "No matching case studies found. "
                "Try broadening your search criteria.\n\n"
                f"RoomPriceGenie has over 30 customer success stories from properties "
                f"around the world. Visit https://roompricegenie.com/en_gb/case-studies/ "
                f"to browse them all."
            )

        # Return top 3 matches
        top = scored[:3]
        output_parts = []

        for _, item, meta in top:
            size_info = f" ({meta['size_range']})" if meta["size_range"] else ""
            country_info = f" in {meta['country'].title()}" if meta["country"] else ""
            context_line = ""
            if size_info or country_info:
                context_line = f"*Property{country_info}{size_info}*\n\n"

            output_parts.append(
                f"### {item.title}\n\n"
                f"{context_line}"
                f"{item.description}\n\n"
                f"**Read the full RoomPriceGenie case study**: {item.url}\n"
            )

        # Build personalised header
        context_parts = []
        if country_lower:
            context_parts.append(f"in/near {country.title()}")
        if num_rooms > 0:
            context_parts.append(f"similar in size to your {num_rooms}-room property")
        if property_lower:
            context_parts.append(f"({property_type})")
        context_str = " ".join(context_parts) if context_parts else "from RoomPriceGenie customers"

        header = (
            f"Here are real RoomPriceGenie success stories {context_str}:\n\n"
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
