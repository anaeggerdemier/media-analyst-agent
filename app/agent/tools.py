import logging
from langchain_core.tools import tool
from app.services.bigquery_service import BigQueryService
from app.schemas.query import (
    TrafficVolumeParams,
    RevenueByChannelParams,
    ChannelComparisonParams,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

bq_service = BigQueryService(
    project_id=settings.BQ_PROJECT_ID,
    credentials_path=settings.BQ_CREDENTIALS_PATH,
)


@tool
def get_traffic_volume(traffic_source: str | None = None, days: int = 30) -> str:
    """
    Returns the volume of users by traffic source (channel) for a given period.
    Use this tool when the user asks about visits, traffic, user volume, or a specific channel like Search, Organic, Facebook, Email or Display.

    Args:
        traffic_source: Filter by a specific channel (e.g. 'Search', 'Organic', 'Facebook'). If None, returns all channels.
        days: Number of days to look back. Default is 30.
    """
    try:
        params = TrafficVolumeParams(traffic_source=traffic_source, days=days)
        results = bq_service.get_traffic_volume(params.traffic_source, params.days)
        if not results:
            return "No traffic data found for the given filters."
        lines = [
            f"- {r['traffic_source']}: {r['total_users']:,} users" for r in results
        ]
        return f"Traffic volume (last {params.days} days):\n" + "\n".join(lines)
    except Exception as e:
        logger.error(f"Error in get_traffic_volume: {e}")
        return f"Error fetching traffic volume: {str(e)}"


@tool
def get_revenue_by_channel(days: int = 30) -> str:
    """
    Returns revenue, total orders and average order value broken down by traffic channel.
    Use this tool when the user asks about revenue, sales, orders or financial performance by channel.

    Args:
        days: Number of days to look back. Default is 30.
    """
    try:
        params = RevenueByChannelParams(days=days)
        results = bq_service.get_revenue_by_channel(params.days)
        if not results:
            return "No revenue data found for the given period."
        lines = [
            f"- {r['traffic_source']}: ${r['total_revenue']:,.2f} revenue | "
            f"{r['total_orders']:,} orders | "
            f"avg order ${r['avg_order_value']:,.2f}"
            for r in results
        ]
        return f"Revenue by channel (last {params.days} days):\n" + "\n".join(lines)
    except Exception as e:
        logger.error(f"Error in get_revenue_by_channel: {e}")
        return f"Error fetching revenue data: {str(e)}"


@tool
def get_channel_comparison(days: int = 30) -> str:
    """
    Returns a full comparison of all channels including users, orders, revenue, conversion rate and revenue per user.
    Use this tool when the user asks which channel performs best, wants a ranking, or asks for an overall analysis.

    Args:
        days: Number of days to look back. Default is 30.
    """
    try:
        params = ChannelComparisonParams(days=days)
        results = bq_service.get_channel_comparison(params.days)
        if not results:
            return "No comparison data found for the given period."
        lines = [
            f"- {r['traffic_source']}: "
            f"{r['total_users']:,} users | "
            f"{r['conversion_rate_pct']}% conversion | "
            f"${r['total_revenue']:,.2f} revenue | "
            f"${r['revenue_per_user']:,.2f} per user"
            for r in results
        ]
        return f"Channel comparison (last {params.days} days):\n" + "\n".join(lines)
    except Exception as e:
        logger.error(f"Error in get_channel_comparison: {e}")
        return f"Error fetching channel comparison: {str(e)}"
