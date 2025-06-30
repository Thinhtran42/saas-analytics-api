from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_revenue: float
    total_ad_spend: float
    roas: float


class TopUserResponse(BaseModel):
    user_id: int
    email: str
    total_revenue: float
