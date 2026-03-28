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
            "Display showed the best performance in the last 30 days, with the highest conversion rate at 7.45% and revenue per user at $8.09."
        ],
    )
    tool_used: str | None = Field(
        default=None,
        examples=["get_channel_comparison"],
    )
