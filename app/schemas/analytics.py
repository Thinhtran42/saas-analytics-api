from pydantic import BaseModel

class SummaryResponse(BaseModel):
    total_revenue: float
    total_ad_spend: float
    roas: float