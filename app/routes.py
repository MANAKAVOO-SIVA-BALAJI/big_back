from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .schemas import AttendanceCreate, AttendanceResponse
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .db import get_db
from datetime import date, datetime, timedelta
from .employee_data import get_all_attendance_by_date , get_attendance_summary_by_date , create_attendance_record ,get_graph_data_by_period

from .create_user import get_user_by_username
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from .models import User

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

SECRET_KEY = "secret123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

@router.get("/")
def home():
    return {"message": "Hello World"}

@router.get("/attendance/{request_date}")
def read_attendance(request_date:str ,db: Session = Depends(get_db)):

    return get_all_attendance_by_date(db, request_date)



@router.get("/daily_summary/{request_date}")
def daily_summary(request_date:str ,db: Session = Depends(get_db)):

    return get_attendance_summary_by_date(db, request_date)


@router.get("/graph/{period}")
def get_graph(period: str, db: Session = Depends(get_db)):
    return get_graph_data_by_period(db, period)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(request.password)
    user = User(username=request.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered successfully"}


@router.post("/logout")
def logout():
    return {"message": "Logout successful"}


@router.post("/store_attendance")
def store_attendance(attendance_data: AttendanceCreate, db: Session = Depends(get_db)):
    
    result=create_attendance_record(db, attendance_data)
    return {"message": "Attendance stored successfully"
            , "result": result.get("schedule_id", "")
            }



