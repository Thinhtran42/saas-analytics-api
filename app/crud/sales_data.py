from sqlalchemy.orm import Session
from app.models.models import SalesData, User, Store
from app.schemas.sales_data import SalesDataCreate
from app.core.redis_client import r
from app.core.logging_config import get_logger
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
logger = get_logger("sales_crud")

def create_sales_data(db: Session, data: SalesDataCreate):
    logger.info("Creating new sales data",
                revenue=data.revenue,
                ad_spend=data.ad_spend,
                store_id=data.store_id,
                user_id=data.user_id)

    sales = SalesData(**data.dict())
    db.add(sales)
    db.commit()
    db.refresh(sales)

    # invalidate cache sau khi insert
    r.delete("analytics:summary")
    logger.info("Sales data created successfully",
                sales_id=sales.id,
                cache_invalidated=True)

    return sales

def get_all_sales_data(db: Session):
    logger.info("Fetching all sales data")
    sales_data = db.query(SalesData).all()
    logger.info("Sales data fetched", count=len(sales_data))
    return sales_data

def generate_fake_sales_data(db: Session, count: int = 50):
    """Tạo dữ liệu fake cho SalesData"""
    logger.info("Starting fake data generation", requested_count=count)

    # Lấy danh sách users và stores có sẵn
    users = db.query(User).all()
    stores = db.query(Store).all()

    if not users:
        logger.info("No users found, creating fake user")
        # Tạo user fake nếu chưa có
        fake_user = User(
            email=fake.email(),
            hashed_password="fake_password_hash"
        )
        db.add(fake_user)
        db.commit()
        db.refresh(fake_user)
        users = [fake_user]
        logger.info("Fake user created", user_id=fake_user.id, email=fake_user.email)

    if not stores:
        logger.info("No stores found, creating fake store")
        # Tạo store fake nếu chưa có
        fake_store = Store(
            name=fake.company(),
            owner_id=users[0].id
        )
        db.add(fake_store)
        db.commit()
        db.refresh(fake_store)
        stores = [fake_store]
        logger.info("Fake store created", store_id=fake_store.id, name=fake_store.name)

    created_sales = []
    total_revenue = 0
    total_ad_spend = 0

    for i in range(count):
        # Tạo ngày ngẫu nhiên trong 30 ngày gần đây
        fake_date = fake.date_between(start_date='-30d', end_date='today')

        # Tạo dữ liệu revenue và ad_spend ngẫu nhiên
        revenue = round(random.uniform(100, 5000), 2)
        ad_spend = round(random.uniform(10, revenue * 0.3), 2)  # Ad spend thường thấp hơn revenue

        total_revenue += revenue
        total_ad_spend += ad_spend

        sales_data = SalesData(
            date=fake_date,
            revenue=revenue,
            ad_spend=ad_spend,
            store_id=random.choice(stores).id,
            user_id=random.choice(users).id
        )

        db.add(sales_data)
        created_sales.append(sales_data)

        # Log progress mỗi 10 record
        if (i + 1) % 10 == 0:
            logger.info("Fake data generation progress",
                       created=i+1,
                       total=count,
                       progress_percent=round((i+1)/count*100, 1))

    db.commit()

    # Invalidate cache sau khi tạo fake data
    r.delete("analytics:summary")
    r.delete("analytics:top_users")

    logger.info("Fake data generation completed",
                total_created=len(created_sales),
                total_revenue=total_revenue,
                total_ad_spend=total_ad_spend,
                average_revenue=round(total_revenue/len(created_sales), 2),
                cache_invalidated=True)

    return created_sales
