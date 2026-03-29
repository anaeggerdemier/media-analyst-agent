from pydantic import BaseModel, Field
from typing import Literal


class TrafficVolumeParams(BaseModel):
    traffic_source: (
        Literal["Search", "Organic", "Facebook", "Email", "Display"] | None
    ) = None
    days: int = Field(default=30, ge=1, le=365)


class RevenueByChannelParams(BaseModel):
    days: int = Field(default=30, ge=1, le=365)


class ChannelComparisonParams(BaseModel):
    days: int = Field(default=30, ge=1, le=365)
