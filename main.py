import logging
from fastapi import FastAPI
from app.api.routes import router, health_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

tags_metadata = [
    {
        "name": "Agent",
        "description": "Endpoints for interacting with the Junior Media Analyst Agent.",
    },
    {
        "name": "Health",
        "description": "Service health and version information.",
    },
]

app = FastAPI(
    title="Junior Media Analyst Agent API",
    summary="AI agent API for e-commerce traffic and revenue analysis.",
    description=(
        "Autonomous AI agent for e-commerce media analysis. "
        "Interprets natural language questions, uses tool calling to query BigQuery, "
        "and returns actionable insights on traffic quality, channel performance, and revenue efficiency.\n\n"
        "**Available tools:**\n"
        "- `get_traffic_volume` — user volume by traffic source\n"
        "- `get_revenue_by_channel` — revenue, orders, and average order value per channel\n"
        "- `get_channel_comparison` — channel performance comparison\n\n"
        "**Behavior:**\n"
        "- Handles only media and growth analysis questions\n"
        "- Declines out-of-scope requests without tool execution\n"
        "- Relies on tool calling instead of prompt-only reasoning"
    ),
    version=settings.APP_VERSION,
    openapi_tags=tags_metadata,
)

app.include_router(health_router)
app.include_router(router, prefix="/api/v1")
