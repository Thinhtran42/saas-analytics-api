import logging
import structlog
from datetime import datetime
import sys
import os

def setup_logging():
    """Cấu hình logging cho ứng dụng"""

    # Cấu hình structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Cấu hình logging standard
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # Tắt logging của uvicorn access log (để tránh duplicate)
    logging.getLogger("uvicorn.access").disabled = True

def get_logger(name: str = None):
    """Lấy logger với tên cho trước"""
    return structlog.get_logger(name or __name__)

# Khởi tạo logging
setup_logging()
logger = get_logger("saas_analytics")