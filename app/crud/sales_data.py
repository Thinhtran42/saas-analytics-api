from sqlalchemy.orm import Session
from app.models.models import SalesData
from app.schemas.sales_data import SalesDataCreate
from app.core.redis_client import r

def create_sales_data(db: Session, data: SalesDataCreate):
    sales = SalesData(**data.dict())
    db.add(sales)
    db.commit()
    db.refresh(sales)

    # invalidate cache sau khi insert
    r.delete("analytics:summary")
    print("🔄 Redis cache invalidated")

    return sales

def get_all_sales_data(db: Session):
    return db.query(SalesData).all()
