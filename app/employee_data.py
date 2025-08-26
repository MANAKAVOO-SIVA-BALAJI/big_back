from math import e
from sqlalchemy.orm import Session
from .models import EmployeeMaster, RosterSchedule, RosterTime, AttendanceMaster

from datetime import datetime, date, time
from pydantic import BaseModel
from typing import Optional

def convert_minutes_to_hours_minutes(total_minutes: int) -> str:
    """
    Convert minutes into hours and minutes.
    Example: 70 -> "1 hour 10 minutes"
    """
    if total_minutes <=0 or None:
        return "0 minutes"
    hours = total_minutes // 60
    minutes = total_minutes % 60
    hours = int(hours)
    minutes = int(minutes)
    
    if hours > 0 and minutes > 0:
        return f"{hours} hr{'s' if hours > 1 else ''},{minutes} min{'s' if minutes > 1 else ''}"
    elif hours > 0:
        return f"{hours} hr{'s' if hours > 1 else ''}"
    else:
        return f"{minutes} min{'s' if minutes > 1 else ''}"
    
def get_all_attendance_by_date(db: Session, target_date: date):
    results = []

    # Join Employee → Schedule → Roster → Attendance
    employees = (
        db.query(EmployeeMaster, RosterTime, AttendanceMaster)
        .join(RosterSchedule, RosterSchedule.emp_id == EmployeeMaster.emp_id)
        .join(RosterTime, RosterTime.roster_id == RosterSchedule.roster_id)
        .outerjoin(
            AttendanceMaster,
            (AttendanceMaster.emp_id == EmployeeMaster.emp_id) &
            (AttendanceMaster.activity_date == target_date)
        )
        .all()
    )

    # Collect attendance per employee
    emp_dict = {}
    for emp, roster, attendance in employees:
        if emp.emp_id not in emp_dict:
            emp_dict[emp.emp_id] = {
                "employee_id": emp.emp_id,
                "employee_name": emp.emp_name,
                "shift_time_start": roster.start_time.strftime("%I:%M %p"),
                "shift_time_end": roster.end_time.strftime("%I:%M %p"),
                "check_in": "",
                "check_out": "",
                "duration": "",
                "entry_status":""
            }

        if attendance:
            if attendance.activity_type == "IN":
                emp_dict[emp.emp_id]["check_in"] = attendance.activity_time.strftime("%H:%M")
            elif attendance.activity_type == "OUT":
                emp_dict[emp.emp_id]["check_out"] = attendance.activity_time.strftime("%H:%M")

        if emp_dict[emp.emp_id]["check_in"] and emp_dict[emp.emp_id]["check_out"]:
            check_in_time = datetime.strptime(emp_dict[emp.emp_id]["check_in"], "%H:%M")
            check_out_time = datetime.strptime(roster.start_time.strftime("%H:%M"), "%H:%M")
            emp_dict[emp.emp_id]["duration"] = convert_minutes_to_hours_minutes((check_out_time - check_in_time).total_seconds() / 60)
        
        if emp_dict[emp.emp_id]["check_in"] and not emp_dict[emp.emp_id]["check_out"]:
            emp_dict[emp.emp_id]["entry_status"] = "Late"
        
        if not emp_dict[emp.emp_id]["check_in"] and emp_dict[emp.emp_id]["check_out"]:
            emp_dict[emp.emp_id]["entry_status"] = "Early"

    results = list(emp_dict.values())
    return results


def get_attendance_summary_by_date(db: Session, target_date: date):
    total_employees = db.query(EmployeeMaster).count()

    wfh_count = db.query(EmployeeMaster).filter(EmployeeMaster.workplace == "WFH").count()
    wfo_count = db.query(EmployeeMaster).filter(EmployeeMaster.workplace == "WFO").count()
    developement_count = db.query(EmployeeMaster).filter(EmployeeMaster.dept == "Developement").count()
    operations_count = db.query(EmployeeMaster).filter(EmployeeMaster.dept == "Operations").count()

    # --- Present (at least one check-in for the date) ---
    present_ids = (
        db.query(AttendanceMaster.emp_id)
        .filter(
            AttendanceMaster.activity_date == target_date,
            AttendanceMaster.activity_type == "IN"
        )
        .distinct()
        .all()
    )
    present_ids = [row[0] for row in present_ids]
    present_count = len(present_ids)

    # --- Absentees (employees with no IN record on that date) ---
    absentee_count = total_employees - present_count

    return {
        "dashboard_data": {
            "total_employees": total_employees,
            "WFH": wfh_count,
            "WFO": wfo_count
        },
        "Present": present_count,
        "Absentee": absentee_count,
        "pie_chart_data": {
            "Developement": developement_count,
            "Operations": operations_count
        }
    }

def get_graph_data_by_period(db: Session, peroid: str):
    return {
        "period": peroid,
        "data": []
    }


def create_attendance_record(db: Session, data):
    activity_date = data.activity_date or date.today()
    activity_time = data.activity_time or datetime.now().time()

    schedule = (
        db.query(RosterSchedule)
        .filter(
            RosterSchedule.emp_id == data.emp_id,
            RosterSchedule.start_date <= activity_date,
            RosterSchedule.end_date >= activity_date
        )
        .first()
    )

    if not schedule:
        raise ValueError(f"No active schedule found for employee {data.emp_id} on {activity_date}")

    attendance = AttendanceMaster(
        emp_id=data.emp_id,
        schedule_id=schedule.schedule_id,
        activity_date=activity_date,
        activity_time=activity_time,
        activity_type=data.activity_type,
        location=data.location
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return {
        "message": "Attendance recorded successfully",
        "attendance_id": attendance.attendance_id,
        "emp_id": attendance.emp_id,
        "schedule_id": attendance.schedule_id,
        "activity_type": attendance.activity_type,
        "activity_time": str(attendance.activity_time),
        "activity_date": str(attendance.activity_date),
        "location": attendance.location
    }


# from .db import get_db

# db = next(get_db())
# from datetime import date

# summary = get_attendance_summary_by_date(db, date.today())

# print("------------------------------------\n\n")
# print(summary)

# emp_data = get_all_attendance_by_date(db, date.today())
# print("------------------------------------\n\n")

# print(emp_data)

