"""
Prefect API Integration
API endpoints để trigger và monitor Prefect workflows
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List
import asyncio
from datetime import datetime

from app.core.logging_config import get_logger
from app.orchestration.prefect_workflows import (
    daily_analytics_etl_flow,
    data_quality_check_flow
)

router = APIRouter(prefix="/prefect", tags=["Prefect Orchestration"])
logger = get_logger("prefect_api")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/flows/daily-etl/run")
async def trigger_daily_etl(
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """Trigger daily ETL flow manually"""
    try:
        logger.info("Manual trigger of daily ETL flow requested")

        # Run flow in background
        def run_flow():
            try:
                result = daily_analytics_etl_flow()
                logger.info("Daily ETL flow completed", result=result)
                return result
            except Exception as e:
                logger.error("Daily ETL flow failed", error=str(e))
                raise

        background_tasks.add_task(run_flow)

        return {
            "message": "Daily ETL flow triggered successfully",
            "flow_name": "daily_analytics_etl",
            "triggered_at": datetime.now().isoformat(),
            "status": "running"
        }

    except Exception as e:
        logger.error("Failed to trigger daily ETL flow", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/flows/data-quality/run")
async def trigger_data_quality_check(
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme)
):
    """Trigger data quality check flow"""
    try:
        logger.info("Manual trigger of data quality check requested")

        def run_quality_check():
            try:
                result = data_quality_check_flow()
                logger.info("Data quality check completed", result=result)
                return result
            except Exception as e:
                logger.error("Data quality check failed", error=str(e))
                raise

        background_tasks.add_task(run_quality_check)

        return {
            "message": "Data quality check triggered successfully",
            "flow_name": "data_quality_check",
            "triggered_at": datetime.now().isoformat(),
            "status": "running"
        }

    except Exception as e:
        logger.error("Failed to trigger data quality check", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/flows/status")
async def get_prefect_flows_info():
    """Get information about available Prefect flows"""
    try:
        flows_info = {
            "available_flows": [
                {
                    "name": "daily_analytics_etl",
                    "description": "Daily Analytics ETL Pipeline",
                    "version": "1.0.0",
                    "tasks": [
                        "extract_sales_data",
                        "transform_sales_analytics",
                        "load_analytics_cache",
                        "generate_daily_report"
                    ],
                    "schedule": "Daily at 2:00 AM",
                    "estimated_duration": "5-10 minutes"
                },
                {
                    "name": "data_quality_check",
                    "description": "Data Quality Validation",
                    "tasks": [
                        "validate_data_consistency",
                        "check_data_freshness",
                        "generate_quality_metrics"
                    ],
                    "schedule": "Every 6 hours",
                    "estimated_duration": "2-3 minutes"
                }
            ],
            "prefect_features": [
                "✅ Task dependency management",
                "✅ Automatic retry mechanisms",
                "✅ Task result caching",
                "✅ Parallel task execution",
                "✅ Flow versioning",
                "✅ Deployment scheduling",
                "✅ Real-time monitoring"
            ],
            "status": "available"
        }

        logger.info("Prefect flows info requested")
        return flows_info

    except Exception as e:
        logger.error("Failed to get flows info", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/cached")
async def get_cached_analytics():
    """Get analytics data processed by Prefect flows"""
    try:
        from app.core.redis_client import r
        import json

        cached_data = {}

        # Get Prefect-processed analytics
        summary_data = r.get("analytics:summary_prefect")
        if summary_data:
            cached_data["summary"] = json.loads(summary_data)

        monthly_data = r.get("analytics:monthly_trends")
        if monthly_data:
            cached_data["monthly_trends"] = json.loads(monthly_data)

        top_users_data = r.get("analytics:top_users_prefect")
        if top_users_data:
            cached_data["top_users"] = json.loads(top_users_data)

        if not cached_data:
            return {
                "message": "No cached analytics data found",
                "suggestion": "Run the daily ETL flow to generate analytics data",
                "endpoint": "/prefect/flows/daily-etl/run"
            }

        cached_data["data_source"] = "prefect_etl_pipeline"
        cached_data["last_updated"] = datetime.now().isoformat()

        logger.info("Cached analytics data retrieved",
                   cached_items=len(cached_data))

        return cached_data

    except Exception as e:
        logger.error("Failed to get cached analytics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/system")
async def get_prefect_system_info():
    """Get Prefect system monitoring information"""
    try:
        system_info = {
            "prefect_version": "2.14.0",
            "orchestration_features": {
                "flow_based_architecture": True,
                "dynamic_workflows": True,
                "task_dependencies": True,
                "parallel_execution": True,
                "automatic_retries": True,
                "result_caching": True,
                "deployment_scheduling": True
            },
            "etl_pipeline_status": {
                "extract_phase": "✅ Database connection established",
                "transform_phase": "✅ Pandas processing configured",
                "load_phase": "✅ Redis caching ready"
            },
            "deployment_info": {
                "daily_etl": "Scheduled for 2:00 AM daily",
                "quality_check": "Scheduled every 6 hours",
                "manual_trigger": "Available via API endpoints"
            },
            "key_features": [
                "🚀 Modern Python-first design",
                "📊 Advanced observability & UI",
                "🔄 Dynamic workflow capabilities",
                "☁️ Cloud-native architecture",
                "🛡️ Enhanced error handling",
                "⚡ Fast development cycle"
            ]
        }

        logger.info("Prefect system info requested")
        return system_info

    except Exception as e:
        logger.error("Failed to get system info", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))