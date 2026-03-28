from pydantic import BaseModel


class TrafficVolumeParams(BaseModel):
    traffic_source: str | None = None
    days: int = 30


class RevenueByChannelParams(BaseModel):
    days: int = 30


class ChannelComparisonParams(BaseModel):
    days: int = 30
