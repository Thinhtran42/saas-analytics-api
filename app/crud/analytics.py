from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import SalesData
from app.core.redis_client import r

import json

def get_summary(db: Session):
    cache_key = "analytics:summary"

    # Kiểm tra cache
    cached_data = r.get(cache_key)
    if cached_data:
        print("✅ Lấy từ Redis cache")
        return json.loads(cached_data)

    # khong co cache thi query tu db
    result = db.query(
        func.sum(SalesData.revenue).label("total_revenue"),
        func.sum(SalesData.ad_spend).label("total_ad_spend"),
    ).first()

    total_revenue = result.total_revenue or 0
    total_ad_spend = result.total_ad_spend or 0
    roas = (total_revenue / total_ad_spend) if total_ad_spend > 0 else 0

    summary = {
        "total_revenue": total_revenue,
        "total_ad_spend": total_ad_spend,
        "roas": round(roas, 2),
    }

    # ghi vao redis cache trong 60s
    r.setex(cache_key, 60, json.dumps(summary))
    print("📦 Ghi Redis cache")

    return summary