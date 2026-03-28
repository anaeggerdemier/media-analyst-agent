import logging
from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.agent.agent import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Agent"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to the Media Analyst Agent",
    description=(
        "Accepts a natural language question about traffic or revenue performance. "
        "The agent autonomously selects the appropriate BigQuery tool, fetches real data, "
        "and returns an interpreted, actionable insight.\n\n"
        "**Example questions:**\n"
        "- *How was the volume of users from Search in the last month?*\n"
        "- *Which channel has the best performance and why?*\n"
        "- *What was the revenue per channel in the last 7 days?*\n\n"
        "Out-of-scope questions (e.g. weather, coding) are politely declined."
    ),
)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        logger.info(f"Received message: {request.message}")
        result = run_agent(request.message)
        return ChatResponse(
            response=result["response"],
            tool_used=result["tool_used"],
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))
