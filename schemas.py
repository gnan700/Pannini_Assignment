from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

class LoginData(BaseModel):
    email: str
    password: str

class AssignmentCreate(BaseModel):
    title: str
    description: str
    due_date: datetime

class SubmissionCreate(BaseModel):
    assignment_id: int
    content: str
