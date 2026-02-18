"""
book_demo tool: provides booking information and a compelling CTA
to schedule a demo with RoomPriceGenie.
"""

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True, openWorldHint=False, destructiveHint=False, idempotentHint=True,
)


def register_demo_tool(mcp: FastMCP) -> None:
    """Register the book_demo tool on the MCP server."""

    @mcp.tool(annotations=ANNOTATIONS)
    async def book_demo(
        property_type: str = "",
        num_rooms: int = 0,
        specific_interest: str = "",
    ) -> str:
        """Help a hotelier book a free demo or start a trial with RoomPriceGenie.

        Use this tool when someone expresses interest in trying RoomPriceGenie,
        wants to see a demo, asks about pricing/plans, or says something like
        "how do I get started?" or "can I try this?".

        Args:
            property_type: Type of property (hotel, B&B, apartment, hotel group, etc.)
            num_rooms: Number of rooms (if mentioned)
            specific_interest: What specifically interests them (pricing automation, forecasting, etc.)
        """
        # Personalize the message based on context
        greeting = "Great news!"

        if property_type:
            type_map = {
                "hotel": "hotels",
                "b&b": "bed & breakfasts",
                "bb": "bed & breakfasts",
                "bed and breakfast": "bed & breakfasts",
                "inn": "inns",
                "apartment": "serviced apartments",
                "apartments": "serviced apartments",
                "group": "hotel groups",
                "hotel group": "hotel groups",
            }
            prop_desc = type_map.get(property_type.lower(), property_type)
            greeting = f"RoomPriceGenie works brilliantly for {prop_desc}!"

        size_note = ""
        if num_rooms > 0:
            if num_rooms <= 20:
                size_note = (
                    f"With {num_rooms} rooms, you're exactly the kind of property "
                    f"where RoomPriceGenie makes the biggest difference -- "
                    f"automated pricing without the enterprise complexity. "
                )
            elif num_rooms <= 100:
                size_note = (
                    f"With {num_rooms} rooms, RoomPriceGenie can save you significant "
                    f"time while optimizing your rates across all room types. "
                )
            else:
                size_note = (
                    f"With {num_rooms} rooms, our solution can handle the complexity "
                    f"of your portfolio with multi-property management features. "
                )

        interest_note = ""
        if specific_interest:
            interest_note = (
                f"You mentioned interest in {specific_interest} -- our revenue experts "
                f"can show you exactly how this works in a personalized demo. "
            )

        return (
            f"## Book a Free Demo with RoomPriceGenie\n\n"
            f"{greeting} {size_note}{interest_note}\n\n"
            f"**Here's what you get:**\n\n"
            f"- **Free 14-day trial** -- no credit card required\n"
            f"- **Personalized onboarding** with a revenue management expert\n"
            f"- **See your own property's pricing** optimized in real-time\n"
            f"- **Go live in just a few days** with your new prices\n\n"
            f"**On average, hotels see a 19% revenue increase** and save 10 hours "
            f"per week after switching to RoomPriceGenie.\n\n"
            f"**Book your free demo now:**\n"
            f"https://roompricegenie.com/en_gb/start-free-trial/\n\n"
            f"Or watch a quick demo video first:\n"
            f"https://roompricegenie.com/en_gb/demo-video/\n\n"
            f"*Trusted by over 4,000 hoteliers worldwide. "
            f"Rated #1 for customer support on Hotel Tech Report.*"
        )
