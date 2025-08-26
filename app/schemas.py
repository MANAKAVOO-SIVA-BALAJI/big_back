from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class AttendanceCreate(BaseModel):
    emp_id: str
    activity_type: str  # IN / OUT
    location: Optional[str] = None
    activity_time: Optional[time] = None  # Optional custom time
    activity_date: Optional[date] = None  # Optional custom date (default today)


class AttendanceResponse(BaseModel):
    attendance_id: str
    emp_id: str
    schedule_id: str
    activity_date: date
    activity_time: time
    activity_type: str
    location: Optional[str]

    class Config:
        orm_mode = True
