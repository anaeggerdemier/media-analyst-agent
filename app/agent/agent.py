import logging
import warnings
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.agent.tools import (
    get_traffic_volume,
    get_revenue_by_channel,
    get_channel_comparison,
)
from app.core.config import settings

logger = logging.getLogger(__name__)

tools = [get_traffic_volume, get_revenue_by_channel, get_channel_comparison]

llm = ChatAnthropic(
    model="claude-sonnet-4-20250514",
    api_key=settings.ANTHROPIC_API_KEY,
    temperature=0,
)

with warnings.catch_warnings():
    # LangGraph v1.x emits a DeprecationWarning suggesting migration to
    # `langchain.agents.create_react_agent`, but that symbol does not exist
    # in langchain==1.2.x. Suppression is scoped to this block intentionally.
    # Revisit when langgraph>=2.0 is released.
    warnings.filterwarnings(
        "ignore",
        category=DeprecationWarning,
        module="langgraph",
    )
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )


def run_agent(message: str) -> dict:
    try:
        logger.info(f"Running agent with message: {message}")
        result = agent.invoke({"messages": [{"role": "user", "content": message}]})

        messages = result.get("messages", [])
        final_response = messages[-1].content if messages else "No response generated."

        tools_used = [
            tool_call.get("name")
            for msg in messages
            if hasattr(msg, "tool_calls") and msg.tool_calls
            for tool_call in msg.tool_calls
        ]

        return {
            "response": final_response,
            "tool_used": tools_used[0] if tools_used else None,
        }
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise
