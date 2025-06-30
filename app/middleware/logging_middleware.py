from fastapi import Request, Response
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import get_logger

logger = get_logger("request_middleware")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Tạo request ID duy nhất
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Log request
        logger.info(
            "Request started",
            request_id=request_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
        )

        # Thêm request_id vào request state
        request.state.request_id = request_id

        try:
            # Xử lý request
            response: Response = await call_next(request)

            # Tính thời gian xử lý
            process_time = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
            )

            # Thêm headers cho tracing
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

            return response

        except Exception as e:
            # Log lỗi
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                error=str(e),
                error_type=type(e).__name__,
                process_time_ms=round(process_time * 1000, 2),
            )
            raise