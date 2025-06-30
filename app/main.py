from fastapi import FastAPI
from .database import Base, engine
from app.models import models
from app.routers import  sales, auth

app = FastAPI()

# Tạo bảng tự động nếu chưa có
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "SaaS Analytics API is running 🚀"}

app.include_router(sales.router)
app.include_router(auth.router)