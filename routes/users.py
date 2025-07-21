from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UserCreate, LoginData
from models import User
from database import SessionLocal
from auth import create_access_token
import bcrypt

router = APIRouter(prefix="/users")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    db_user = User(name=user.name, email=user.email, password=hashed_pw.decode(), role=user.role)
    db.add(db_user)
    db.commit()
    return {"message": "User created"}

@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not bcrypt.checkpw(data.password.encode(), user.password.encode()):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token}

