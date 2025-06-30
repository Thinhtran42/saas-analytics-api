from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    stores = relationship("Store", back_populates="owner")
    sales = relationship("SalesData", back_populates="user")


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Index for store name searches
    owner_id = Column(Integer, ForeignKey("users.id"), index=True)
    owner = relationship("User", back_populates="stores")
    sales = relationship("SalesData", back_populates="store")


class SalesData(Base):
    __tablename__ = "sales_data"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)  # Index for date range queries
    revenue = Column(Float, index=True)  # Index for revenue sorting
    ad_spend = Column(Float)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True)
    store = relationship("Store", back_populates="sales")
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", back_populates="sales")

    # Composite indexes for performance optimization
    __table_args__ = (
        Index('idx_sales_date_user', 'date', 'user_id'),  # For user analytics by date
        Index('idx_sales_revenue_user', 'revenue', 'user_id'),  # For top users queries
        Index('idx_sales_store_date', 'store_id', 'date'),  # For store analytics
    )
