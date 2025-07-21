from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from schemas import SubmissionCreate
from models import Submission, Assignment, User
from database import SessionLocal
from auth import verify_token
from fastapi.security import OAuth2PasswordBearer
import shutil
import os

router = APIRouter(prefix="/submissions")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create upload directory if not exists
UPLOAD_DIR = "uploaded_submissions"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def submit_assignment(
    assignment_id: int,
    token: str = Depends(oauth2_scheme),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user_data = verify_token(token)
    if not user_data or user_data.get("role") != "student":
        raise HTTPException(status_code=403, detail="Only students can submit")

    student = db.query(User).filter(User.email == user_data["sub"]).first()

    file_location = f"{UPLOAD_DIR}/{student.id}_{assignment_id}_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_submission = Submission(
        assignment_id=assignment_id,
        student_id=student.id,
        content=file_location  # Save the file path
    )
    db.add(new_submission)
    db.commit()
    return {"message": "Submission successful", "file_saved": file_location}

@router.get("/assignment/{assignment_id}")
def view_submissions(
    assignment_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_data = verify_token(token)
    if not user_data or user_data.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view submissions")

    submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
    return submissions
