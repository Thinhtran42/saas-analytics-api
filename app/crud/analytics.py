from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import SalesData
from app.core.redis_client import r
from app.models.models import User
from app.core.logging_config import get_logger
import json
import time

logger = get_logger("analytics_crud")

def get_summary(db: Session):
    start_time = time.time()
    cache_key = "analytics:summary"

    # Kiểm tra cache
    cached_data = r.get(cache_key)
    if cached_data:
        query_time = round((time.time() - start_time) * 1000, 2)
        logger.info("Analytics summary cache hit",
                   cache_key=cache_key,
                   query_time_ms=query_time)
        return json.loads(cached_data)

    logger.info("Analytics summary cache miss, querying database", cache_key=cache_key)

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
    query_time = round((time.time() - start_time) * 1000, 2)

    logger.info("Analytics summary computed and cached",
               cache_key=cache_key,
               total_revenue=total_revenue,
               total_ad_spend=total_ad_spend,
               roas=round(roas, 2),
               query_time_ms=query_time,
               cache_ttl_seconds=60)

    return summary

def get_top_users(db: Session, limit: int = 3):
    start_time = time.time()
    cache_key = "analytics:top_users"

    cached_data = r.get(cache_key)
    if cached_data:
        query_time = round((time.time() - start_time) * 1000, 2)
        logger.info("Top users cache hit",
                   cache_key=cache_key,
                   limit=limit,
                   query_time_ms=query_time)
        return json.loads(cached_data)

    logger.info("Top users cache miss, querying database",
               cache_key=cache_key,
               limit=limit)

    result = (
        db.query(
            User.id.label('user_id'),
            User.email,
            func.sum(SalesData.revenue).label("total_revenue")
        )
        .join(SalesData, SalesData.user_id == User.id)
        .group_by(User.id, User.email)
        .order_by(func.sum(SalesData.revenue).desc())
        .limit(limit)
        .all()
    )

    top_users = [
        {
            "user_id": row.user_id,
            "email": row.email,
            "total_revenue": round(row.total_revenue, 2)
        }
        for row in result
    ]

    r.setex(cache_key, 60, json.dumps(top_users))
    query_time = round((time.time() - start_time) * 1000, 2)

    logger.info("Top users computed and cached",
               cache_key=cache_key,
               users_count=len(top_users),
               limit=limit,
               query_time_ms=query_time,
               cache_ttl_seconds=60,
               top_user_revenue=top_users[0]["total_revenue"] if top_users else 0)

    return top_users
