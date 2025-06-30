from sqlalchemy.orm import Session
from app.models.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email:str, password:str):
    hashed_pw = pwd_context.hash(password)
    user = User(email = email, hashed_password = hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_pw: str, hashed_pw: str):
    return pwd_context.verify(plain_pw, hashed_pw)
