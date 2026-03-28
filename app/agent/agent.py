import logging
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

        tool_used = None
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_used = msg.tool_calls[0].get("name")
                break

        return {
            "response": final_response,
            "tool_used": tool_used,
        }
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise
