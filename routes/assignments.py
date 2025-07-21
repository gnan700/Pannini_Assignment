from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import AssignmentCreate
from models import Assignment, User
from database import SessionLocal
from auth import verify_token
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter(prefix="/assignments")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_assignment(assignment: AssignmentCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_data = verify_token(token)
    if not user_data or user_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create assignments")

    teacher = db.query(User).filter(User.email == user_data["sub"]).first()
    new_assignment = Assignment(
        title=assignment.title,
        description=assignment.description,
        due_date=assignment.due_date,
        created_by=teacher.id
    )
    db.add(new_assignment)
    db.commit()
    return {"message": "Assignment created"}

