from pydantic import BaseModel
from datetime import date

class SalesDataCreate(BaseModel):
    date: date
    revenue: float
    ad_spend: float
    store_id: int
    user_id: int

class SalesDataOut(SalesDataCreate):
    id: int

    class Config:
        from_attributes = True