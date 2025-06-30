from fastapi import FastAPI
from .database import Base, engine
from app.models import models  # Import models để register với SQLAlchemy
from app.routers import sales, auth, health, prefect_api
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.logging_config import logger

app = FastAPI(
    title="SaaS Analytics API",
    description="API phân tích dữ liệu bán hàng với logging và monitoring",
    version="1.0.0"
)

# Thêm middleware
app.add_middleware(LoggingMiddleware)

# Tạo bảng tự động nếu chưa có
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    logger.info("Home endpoint accessed")
    return {"message": "SaaS Analytics API is running 🚀"}

# Include routers
app.include_router(sales.router)
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(prefect_api.router)

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 SaaS Analytics API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 SaaS Analytics API shutting down...")