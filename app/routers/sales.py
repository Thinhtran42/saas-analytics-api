from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import ALGORITHM, SECRET_KEY
from app.crud import analytics as analytics_crud
from app.crud import sales_data as crud
from app.dependencies.deps import get_db
from app.models.models import User
from app.schemas.analytics import SummaryResponse, TopUserResponse
from app.schemas.sales_data import SalesDataCreate, SalesDataOut

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/sales-data/", response_model=SalesDataOut)
def create_sales(
    data: SalesDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_sales_data(db, data)


@router.get("/sales-data/", response_model=list[SalesDataOut])
def read_sales(db: Session = Depends(get_db)):
    return crud.get_all_sales_data(db)


@router.post("/sales-data/generate-fake")
def generate_fake_sales(
    count: int = 50,
    db: Session = Depends(get_db)
):
    """Tạo dữ liệu fake cho sales data"""
    try:
        created_sales = crud.generate_fake_sales_data(db, count)
        return {
            "message": f"✅ Đã tạo {len(created_sales)} dữ liệu fake thành công",
            "count": len(created_sales),
            "data": [
                {
                    "id": sales.id,
                    "date": str(sales.date),
                    "revenue": sales.revenue,
                    "ad_spend": sales.ad_spend,
                    "store_id": sales.store_id,
                    "user_id": sales.user_id
                }
                for sales in created_sales[:5]  # Chỉ hiển thị 5 record đầu
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo fake data: {str(e)}")


@router.get("/analytics/summary", response_model=SummaryResponse)
def analytics_summary(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return analytics_crud.get_summary(db)


@router.get("/analytics/top_users", response_model=list[TopUserResponse])
def top_users(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return analytics_crud.get_top_users(db)
