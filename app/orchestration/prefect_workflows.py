"""
Prefect Workflows for SaaS Analytics API
Modern orchestration using Prefect 3.0 - Industry standard tool
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
from prefect import flow, task, get_run_logger, serve
from prefect.tasks import task_input_hash

from app.core.logging_config import get_logger
from app.database import SessionLocal
from app.crud.analytics import get_summary, get_top_users
from app.crud.sales_data import get_all_sales_data
from app.models.models import SalesData, User

logger = get_logger("prefect_workflows")

@task(
    name="extract_sales_data",
    description="Extract sales data from database",
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def extract_sales_data() -> Dict:
    """Extract sales data - ETL Extract step"""
    prefect_logger = get_run_logger()

    try:
        db = SessionLocal()
        sales_data = get_all_sales_data(db)

        # Convert to DataFrame for processing
        df_data = []
        for sale in sales_data:
            df_data.append({
                'id': sale.id,
                'date': sale.date,
                'revenue': sale.revenue,
                'ad_spend': sale.ad_spend,
                'user_id': sale.user_id,
                'store_id': sale.store_id
            })

        df = pd.DataFrame(df_data)

        prefect_logger.info(f"Extracted {len(df)} sales records from database")

        return {
            "total_records": len(df),
            "date_range": {
                "start": str(df['date'].min()) if not df.empty else None,
                "end": str(df['date'].max()) if not df.empty else None
            },
            "raw_data": df_data
        }

    except Exception as e:
        prefect_logger.error(f"Failed to extract sales data: {str(e)}")
        raise
    finally:
        db.close()

@task(
    name="transform_sales_analytics",
    description="Transform data for analytics",
    retries=3,
    retry_delay_seconds=10
)
def transform_sales_analytics(sales_data: Dict) -> Dict:
    """Transform sales data - ETL Transform step"""
    prefect_logger = get_run_logger()

    try:
        df = pd.DataFrame(sales_data["raw_data"])

        if df.empty:
            prefect_logger.warning("No data to transform")
            return {"transformed_data": [], "metrics": {}}

        # Calculate metrics
        total_revenue = df['revenue'].sum()
        total_ad_spend = df['ad_spend'].sum()
        roas = total_revenue / total_ad_spend if total_ad_spend > 0 else 0

        # Monthly aggregations
        df['date'] = pd.to_datetime(df['date'])
        monthly_metrics = df.groupby(df['date'].dt.to_period('M')).agg({
            'revenue': 'sum',
            'ad_spend': 'sum'
        }).reset_index()

        monthly_metrics['roas'] = monthly_metrics['revenue'] / monthly_metrics['ad_spend'].replace(0, 1)
        monthly_metrics['date'] = monthly_metrics['date'].astype(str)

        # Top performing users
        user_metrics = df.groupby('user_id').agg({
            'revenue': 'sum',
            'ad_spend': 'sum'
        }).reset_index()
        user_metrics['roas'] = user_metrics['revenue'] / user_metrics['ad_spend'].replace(0, 1)
        user_metrics = user_metrics.sort_values('revenue', ascending=False).head(10)

        transformed_data = {
            "overall_metrics": {
                "total_revenue": float(total_revenue),
                "total_ad_spend": float(total_ad_spend),
                "roas": float(roas),
                "avg_daily_revenue": float(df.groupby('date')['revenue'].sum().mean())
            },
            "monthly_trends": monthly_metrics.to_dict('records'),
            "top_users": user_metrics.to_dict('records')
        }

        prefect_logger.info(f"Transformed data with {len(monthly_metrics)} monthly periods and {len(user_metrics)} top users")

        return transformed_data

    except Exception as e:
        prefect_logger.error(f"Failed to transform sales data: {str(e)}")
        raise

@task(
    name="load_analytics_cache",
    description="Load analytics results to cache",
    retries=2
)
def load_analytics_cache(transformed_data: Dict) -> Dict:
    """Load transformed data to cache - ETL Load step"""
    prefect_logger = get_run_logger()

    try:
        from app.core.redis_client import r
        import json

        # Cache overall metrics
        r.setex(
            "analytics:summary_prefect",
            3600,  # 1 hour TTL
            json.dumps(transformed_data["overall_metrics"])
        )

        # Cache monthly trends
        r.setex(
            "analytics:monthly_trends",
            3600,
            json.dumps(transformed_data["monthly_trends"])
        )

        # Cache top users
        r.setex(
            "analytics:top_users_prefect",
            3600,
            json.dumps(transformed_data["top_users"])
        )

        prefect_logger.info("Analytics data successfully cached to Redis")

        return {
            "cache_status": "success",
            "cached_items": 3,
            "ttl_seconds": 3600
        }

    except Exception as e:
        prefect_logger.error(f"Failed to load data to cache: {str(e)}")
        raise

@task(
    name="generate_daily_report",
    description="Generate daily analytics report"
)
def generate_daily_report(analytics_data: Dict) -> Dict:
    """Generate daily report task"""
    prefect_logger = get_run_logger()

    try:
        report = {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": analytics_data["overall_metrics"],
            "insights": [],
            "recommendations": []
        }

        # Add insights
        overall = analytics_data["overall_metrics"]
        if overall["roas"] > 3.0:
            report["insights"].append("🎉 Excellent ROAS performance - above 3.0 threshold")
        elif overall["roas"] < 1.0:
            report["insights"].append("⚠️ ROAS below 1.0 - advertising spend exceeds revenue")

        if overall["avg_daily_revenue"] > 10000:
            report["insights"].append("📈 High daily revenue performance")

        # Add recommendations
        if len(analytics_data["top_users"]) > 0:
            top_user_revenue = analytics_data["top_users"][0]["revenue"]
            report["recommendations"].append(f"Focus on top user segment - generating ${top_user_revenue:,.2f}")

        prefect_logger.info("Daily report generated successfully")

        return report

    except Exception as e:
        prefect_logger.error(f"Failed to generate daily report: {str(e)}")
        raise

@flow(
    name="daily_analytics_etl",
    description="Daily Analytics ETL Pipeline using Prefect",
    version="1.0.0"
)
def daily_analytics_etl_flow():
    """
    Main ETL Flow for daily analytics processing
    Demonstrates Prefect orchestration capabilities
    """
    flow_logger = get_run_logger()
    flow_logger.info("🚀 Starting Daily Analytics ETL Flow")

    # ETL Pipeline with task dependencies
    sales_data = extract_sales_data()
    transformed_data = transform_sales_analytics(sales_data)
    cache_result = load_analytics_cache(transformed_data)
    daily_report = generate_daily_report(transformed_data)

    flow_logger.info("✅ Daily Analytics ETL Flow completed successfully")

    return {
        "flow_status": "completed",
        "processed_records": sales_data["total_records"],
        "cache_status": cache_result["cache_status"],
        "report_generated": True
    }

@flow(
    name="data_quality_check",
    description="Data quality validation flow"
)
def data_quality_check_flow():
    """Data quality validation flow"""
    flow_logger = get_run_logger()
    flow_logger.info("🔍 Starting Data Quality Check Flow")

    try:
        db = SessionLocal()

        # Check for data consistency
        total_sales = db.query(SalesData).count()
        total_users = db.query(User).count()

        # Data quality metrics
        recent_sales = db.query(SalesData).filter(
            SalesData.date >= datetime.now() - timedelta(days=7)
        ).count()

        quality_metrics = {
            "total_sales_records": total_sales,
            "total_users": total_users,
            "recent_sales_7days": recent_sales,
            "data_freshness": "good" if recent_sales > 0 else "stale"
        }

        flow_logger.info(f"Data quality check completed: {quality_metrics}")

        return quality_metrics

    except Exception as e:
        flow_logger.error(f"Data quality check failed: {str(e)}")
        raise
    finally:
        db.close()

# Deployment configurations
if __name__ == "__main__":
    # Create deployment for daily ETL using serve method
    daily_etl_deployment = daily_analytics_etl_flow.to_deployment(
        name="daily-analytics-etl",
        cron="0 2 * * *",  # Daily at 2 AM
        tags=["analytics", "etl", "daily"],
        description="Daily analytics ETL pipeline with Prefect orchestration"
    )

    # Create deployment for data quality check using serve method
    quality_check_deployment = data_quality_check_flow.to_deployment(
        name="data-quality-check",
        cron="0 */6 * * *",  # Every 6 hours
        tags=["data-quality", "monitoring"],
        description="Data quality validation checks"
    )

    print("🚀 Prefect deployments configured!")
    print("Starting serve process for flows...")

    # Serve both deployments
    serve(daily_etl_deployment, quality_check_deployment)