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
            "**Display had the best overall performance** in the last 30 days, despite bringing in the lowest volume of users.\n\n"
            "- **Highest conversion rate**: 7.45% (vs. 6.68% average across channels)\n"
            "- **Best revenue per user**: $8.09 (19% higher than the next best channel)\n\n"
            "**Recommendation:** Increase Display budget allocation — it's your most efficient channel for converting visitors into customers."
        ],
    )
    tool_used: str | None = Field(
        default=None,
        examples=["get_channel_comparison"],
    )
