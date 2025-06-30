from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies.deps import get_db
from app.core.redis_client import r
from app.core.logging_config import get_logger
import psutil
import time
from datetime import datetime
from sqlalchemy import text

router = APIRouter(prefix="/health", tags=["Health Check"])
logger = get_logger("health_check")

@router.get("/")
def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SaaS Analytics API"
    }

@router.get("/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check với kiểm tra database và redis"""
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SaaS Analytics API",
        "version": "1.0.0",
        "checks": {}
    }

    # Kiểm tra Database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "PostgreSQL connection OK"
        }
        logger.info("Database health check passed")
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}"
        }
        health_status["status"] = "unhealthy"
        logger.error("Database health check failed", error=str(e))

    # Kiểm tra Redis
    try:
        r.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection OK"
        }
        logger.info("Redis health check passed")
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis error: {str(e)}"
        }
        health_status["status"] = "unhealthy"
        logger.error("Redis health check failed", error=str(e))

    # Thời gian phản hồi
    response_time = round((time.time() - start_time) * 1000, 2)
    health_status["response_time_ms"] = response_time

    return health_status

@router.get("/metrics")
def system_metrics():
    """System metrics và monitoring"""

    # CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)

    # Memory usage
    memory = psutil.virtual_memory()

    # Disk usage
    disk = psutil.disk_usage('/')

    # Network stats (nếu có)
    try:
        network = psutil.net_io_counters()
        network_stats = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv,
            "packets_sent": network.packets_sent,
            "packets_recv": network.packets_recv
        }
    except:
        network_stats = {"error": "Network stats not available"}

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "network": network_stats
        }
    }

    logger.info("System metrics collected",
                cpu_percent=cpu_percent,
                memory_percent=memory.percent)

    return metrics

@router.get("/redis-info")
def redis_info():
    """Thông tin chi tiết về Redis"""
    try:
        info = r.info()

        # Chỉ lấy các metrics quan trọng
        redis_metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "redis": {
                "version": info.get("redis_version"),
                "uptime_seconds": info.get("uptime_in_seconds"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory"),
                "used_memory_human": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace": {
                    db: info.get(db, {}) for db in info.keys()
                    if db.startswith('db')
                }
            }
        }

        logger.info("Redis info collected",
                   connected_clients=info.get("connected_clients"))

        return redis_metrics

    except Exception as e:
        logger.error("Failed to get Redis info", error=str(e))
        raise HTTPException(status_code=503, detail=f"Redis error: {str(e)}")