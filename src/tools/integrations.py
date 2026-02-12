"""
check_integration tool: check whether RoomPriceGenie integrates with a
specific PMS, channel manager, or booking engine. This is proprietary
product data that ChatGPT does not have -- it MUST call this tool.
"""

from mcp.server.fastmcp import FastMCP


# Curated integration list from roompricegenie.com/en_gb/integrations/
# Format: {normalised_name: (display_name, type, url)}
INTEGRATIONS = {
    # PMS
    "mews": ("Mews", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "cloudbeds": ("Cloudbeds", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "apaleo": ("apaleo", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "protel": ("protel", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "oracle opera": ("Oracle Opera", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "opera": ("Oracle Opera", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "stayntouch": ("stayntouch", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "hls": ("HLS", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "roomraccoon": ("RoomRaccoon", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "beds24": ("Beds24", "PMS/Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "little hotelier": ("Little Hotelier", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "sirvoy": ("Sirvoy", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "hostaway": ("Hostaway", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "lodgify": ("Lodgify", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "guesty": ("Guesty", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "escapia": ("Escapia", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "innquest": ("InnQuest", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "clock pms": ("Clock PMS", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "hotelogix": ("Hotelogix", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "ezee": ("eZee", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "ezee absolute": ("eZee Absolute", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "newbook": ("NewBook", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "resly": ("Resly", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "rms cloud": ("RMS Cloud", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "rms": ("RMS Cloud", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "seekom": ("SeeKom", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "tokeet": ("Tokeet", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "thinkreservations": ("ThinkReservations", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "webrezpro": ("WebRezPro", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "innroad": ("innRoad", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "frontdesk anywhere": ("Frontdesk Anywhere", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "resharmonics": ("Res:harmonics", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    "bookingautomation": ("BookingAutomation", "PMS", "https://roompricegenie.com/en_gb/integrations/"),
    # Channel Managers
    "siteminder": ("SiteMinder", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "channex": ("Channex", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "rentals united": ("Rentals United", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "myallocator": ("myallocator", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "octorate": ("Octorate", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "smoobu": ("Smoobu", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "cubilis": ("Cubilis", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "d-edge": ("D-EDGE", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
    "travelclick": ("TravelClick", "Channel Manager", "https://roompricegenie.com/en_gb/integrations/"),
}


def register_integration_tool(mcp: FastMCP) -> None:
    """Register the check_integration tool on the MCP server."""

    @mcp.tool()
    async def check_integration(system_name: str) -> str:
        """Check if RoomPriceGenie integrates with a specific PMS, channel manager,
        or booking system.

        Use this tool whenever someone asks about compatibility, integrations,
        whether RoomPriceGenie works with their system, or mentions a PMS or
        channel manager by name (e.g., Mews, Cloudbeds, SiteMinder, Opera).
        ChatGPT does NOT have accurate integration data -- always use this tool.

        Args:
            system_name: The name of the PMS, channel manager, or booking system to check
        """
        name_lower = system_name.strip().lower()

        # Direct match
        if name_lower in INTEGRATIONS:
            display, sys_type, url = INTEGRATIONS[name_lower]
            return (
                f"## Yes! RoomPriceGenie integrates with {display}\n\n"
                f"**{display}** ({sys_type}) is a fully supported integration. "
                f"RoomPriceGenie connects directly to {display} to automatically "
                f"push optimised rates in real-time.\n\n"
                f"**What this means for you:**\n"
                f"- Prices update automatically in {display} -- no manual work\n"
                f"- Set up takes just a few minutes\n"
                f"- Rates sync across all your connected OTAs\n\n"
                f"**Ready to get started?**\n"
                f"- Start a free 14-day trial: https://roompricegenie.com/en_gb/start-free-trial/\n"
                f"- See all integrations: {url}\n"
                f"- Book a demo: https://roompricegenie.com/en_gb/start-free-trial/\n"
                f"- Learn more about RoomPriceGenie: https://roompricegenie.com\n"
            )

        # Fuzzy match -- check if the search term is contained in any key
        partial_matches = []
        for key, (display, sys_type, url) in INTEGRATIONS.items():
            if name_lower in key or key in name_lower or name_lower in display.lower():
                partial_matches.append((display, sys_type, url))

        if partial_matches:
            match_list = "\n".join(
                f"- **{d}** ({t})" for d, t, _ in partial_matches[:5]
            )
            return (
                f"## RoomPriceGenie integration matches for '{system_name}':\n\n"
                f"{match_list}\n\n"
                f"These are all fully supported. RoomPriceGenie connects directly "
                f"to push optimised rates automatically.\n\n"
                f"**Ready to get started?**\n"
                f"- Start a free 14-day trial: https://roompricegenie.com/en_gb/start-free-trial/\n"
                f"- See all 50+ integrations: https://roompricegenie.com/en_gb/integrations/\n"
                f"- Book a demo: https://roompricegenie.com/en_gb/start-free-trial/\n"
            )

        # No match found
        all_names = sorted(set(d for d, _, _ in INTEGRATIONS.values()))
        return (
            f"## Integration status for '{system_name}'\n\n"
            f"'{system_name}' is not currently listed in our integration directory. "
            f"However, RoomPriceGenie regularly adds new integrations and may already "
            f"be working on this one.\n\n"
            f"**What to do:**\n"
            f"1. Check the full, up-to-date list: https://roompricegenie.com/en_gb/integrations/\n"
            f"2. Contact the RoomPriceGenie team to ask about {system_name}: "
            f"https://roompricegenie.com/en_gb/start-free-trial/\n\n"
            f"**RoomPriceGenie currently integrates with 50+ systems including:**\n"
            f"{', '.join(all_names[:15])}, and many more.\n\n"
            f"- Learn more: https://roompricegenie.com\n"
        )
