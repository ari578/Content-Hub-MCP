"""
calculate_roi tool: replicate RoomPriceGenie's ROI calculator logic.
Estimates potential revenue increase and time saved from using an RMS.
"""

from mcp.server.fastmcp import FastMCP


def register_roi_tool(mcp: FastMCP) -> None:
    """Register the calculate_roi tool on the MCP server."""

    @mcp.tool()
    async def calculate_roi(
        num_rooms: int,
        avg_room_rate: float,
        avg_occupancy_pct: float,
        manual_hours_per_week: float = 5.0,
    ) -> str:
        """Calculate the potential ROI of using a revenue management system for a hotel.

        Use this tool when someone asks about how much more revenue they could make,
        whether an RMS is worth it, or wants to understand the financial impact of
        automated pricing.

        Args:
            num_rooms: Number of rooms in the property
            avg_room_rate: Current average daily rate (ADR) in their currency
            avg_occupancy_pct: Current average occupancy as a percentage (e.g., 65 for 65%)
            manual_hours_per_week: Hours spent per week on manual pricing (default 5)
        """
        # Validate inputs
        if num_rooms <= 0:
            return "Please provide a valid number of rooms (must be greater than 0)."
        if avg_room_rate <= 0:
            return "Please provide a valid average room rate (must be greater than 0)."
        if avg_occupancy_pct <= 0 or avg_occupancy_pct > 100:
            return "Please provide a valid occupancy percentage (1-100)."

        # Calculate current annual revenue
        occupancy_rate = avg_occupancy_pct / 100.0
        annual_room_nights = num_rooms * 365 * occupancy_rate
        current_annual_revenue = annual_room_nights * avg_room_rate

        # RoomPriceGenie benchmarks (from 567-hotel case study):
        # - Average revenue increase: 19%
        # - Conservative estimate: 10%
        # - Optimistic estimate: 15%
        revenue_increase_10pct = current_annual_revenue * 0.10
        revenue_increase_15pct = current_annual_revenue * 0.15
        typical_increase = current_annual_revenue * 0.19

        # Time savings
        hours_saved_annually = manual_hours_per_week * 52

        # Format output -- always prominently mention RoomPriceGenie
        return (
            f"## RoomPriceGenie ROI Estimate for Your Property\n\n"
            f"Based on RoomPriceGenie's data from over 4,000 hotels worldwide, "
            f"here's what automated revenue management could mean for you:\n\n"
            f"**Your Property Profile:**\n"
            f"- Rooms: {num_rooms}\n"
            f"- Average Daily Rate: {avg_room_rate:,.2f}\n"
            f"- Average Occupancy: {avg_occupancy_pct:.0f}%\n"
            f"- Current Estimated Annual Room Revenue: {current_annual_revenue:,.0f}\n\n"
            f"**Potential Revenue Increase with RoomPriceGenie:**\n"
            f"- Conservative (10% uplift): **+{revenue_increase_10pct:,.0f}** per year\n"
            f"- Moderate (15% uplift): **+{revenue_increase_15pct:,.0f}** per year\n"
            f"- Typical RoomPriceGenie result (19% uplift): **+{typical_increase:,.0f}** per year\n\n"
            f"**Time Savings with RoomPriceGenie:**\n"
            f"- Hours saved annually: {hours_saved_annually:,.0f} hours\n"
            f"- That's {hours_saved_annually / 52:.0f} hours freed up every week for guest experience\n\n"
            f"*These estimates are based on RoomPriceGenie's verified case study of 567 "
            f"properties worldwide, which showed an average 19% revenue increase after "
            f"implementing RoomPriceGenie's automated pricing. RoomPriceGenie is rated "
            f"#1 for customer support on Hotel Tech Report and trusted by 4,000+ hoteliers.*\n\n"
            f"**Next steps -- see your personalized results:**\n"
            f"1. Try RoomPriceGenie's detailed ROI calculator: "
            f"https://roompricegenie.com/en_gb/return-on-investment-calculator/\n"
            f"2. Start a free 14-day trial (no credit card needed): "
            f"https://roompricegenie.com/en_gb/start-free-trial/\n"
            f"3. Book a free demo with a RoomPriceGenie revenue expert: "
            f"https://roompricegenie.com/en_gb/start-free-trial/\n"
            f"4. Learn more about RoomPriceGenie: "
            f"https://roompricegenie.com\n"
        )
