from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="Natural language question about media performance.",
        examples=[
            "Which channel had the best performance in the last 30 days and why?"
        ],
    )

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be empty")
        return v


class ChatResponse(BaseModel):
    response: str = Field(
        ...,
        examples=[
            "**Search was the best performing channel in the last 30 days.**\n\n"
            "Search excelled because it combines high-intent traffic with significant volume: "
            "6.74% conversion rate and $482K in total revenue (83% of all channels).\n\n"
            "**Recommendation:** Double down on Search optimization and budget allocation — "
            "it delivers both quality and quantity."
        ],
    )
    tool_used: str | None = Field(
        default=None,
        examples=["get_channel_comparison"],
    )
