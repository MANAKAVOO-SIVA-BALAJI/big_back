from sqlalchemy import (
    Column, String, Boolean, Date, Time, ForeignKey, CheckConstraint,
    Sequence,DateTime
)
from sqlalchemy.orm import declarative_base, relationship
 
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from .db import Base 


employee_seq = Sequence("employee_seq", start=1)

class EmployeeMaster(Base):
    __tablename__ = "employee_master"

    emp_id = Column(
        String,
        primary_key=True,
        server_default=("'EMP' || LPAD(nextval('employee_seq')::TEXT, 5, '0')")
    )
    emp_name = Column(String(100), nullable=False)
    position = Column(String(50))
    dept = Column(String(50))
    workplace = Column(String(10), CheckConstraint("workplace IN ('WFO', 'WFH')"))
    is_active = Column(Boolean, default=True)

    schedules = relationship("RosterSchedule", back_populates="employee")
    attendance_records = relationship("AttendanceMaster", back_populates="employee")



roster_seq = Sequence("roster_seq", start=1)

class RosterTime(Base):
    __tablename__ = "roster_time"

    roster_id = Column(
        String,
        primary_key=True,
        server_default=("'ROS' || LPAD(nextval('roster_seq')::TEXT, 5, '0')")
    )
    shift_name = Column(String(50), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    weekoffs = relationship("RosterWeekOff", back_populates="roster", cascade="all, delete")
    schedules = relationship("RosterSchedule", back_populates="roster")



weekoff_seq = Sequence("weekoff_seq", start=1)

class RosterWeekOff(Base):
    __tablename__ = "roster_weekoff"

    weekoff_id = Column(
        String,
        primary_key=True,
        server_default=("'WOF' || LPAD(nextval('weekoff_seq')::TEXT, 5, '0')")
    )
    roster_id = Column(String, ForeignKey("roster_time.roster_id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(
        String(10),
        CheckConstraint("day_of_week IN ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')")
    )

    roster = relationship("RosterTime", back_populates="weekoffs")


schedule_seq = Sequence("schedule_seq", start=1)

class RosterSchedule(Base):
    __tablename__ = "roster_schedule"

    schedule_id = Column(
        String,
        primary_key=True,
        server_default=("'SCH' || LPAD(nextval('schedule_seq')::TEXT, 5, '0')")
    )
    emp_id = Column(String, ForeignKey("employee_master.emp_id", ondelete="CASCADE"), nullable=False)
    roster_id = Column(String, ForeignKey("roster_time.roster_id", ondelete="CASCADE"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    employee = relationship("EmployeeMaster", back_populates="schedules")
    roster = relationship("RosterTime", back_populates="schedules")
    attendance_records = relationship("AttendanceMaster", back_populates="schedule")


attendance_seq = Sequence("attendance_seq", start=1)

class AttendanceMaster(Base):
    __tablename__ = "attendance_master"

    attendance_id = Column(
        String,
        primary_key=True,
        server_default=("'ATT' || LPAD(nextval('attendance_seq')::TEXT, 6, '0')")
    )
    emp_id = Column(String, ForeignKey("employee_master.emp_id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(String, ForeignKey("roster_schedule.schedule_id", ondelete="CASCADE"), nullable=False)
    activity_date = Column(Date, nullable=False)
    activity_time = Column(Time, nullable=False)
    activity_type = Column(String(3), CheckConstraint("activity_type IN ('IN','OUT')"))
    location = Column(String(100))

    employee = relationship("EmployeeMaster", back_populates="attendance_records")
    schedule = relationship("RosterSchedule", back_populates="attendance_records")
    


class User(Base):
    __tablename__ = "user_table"
    
    username = Column(String(50), primary_key=True, unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(username={self.username})>"
    



