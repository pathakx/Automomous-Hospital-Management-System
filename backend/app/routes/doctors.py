from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.schemas.hospital import DoctorResponse, DoctorScheduleResponse

router = APIRouter(prefix="/doctors", tags=["Doctors Directory"])

@router.get("/", response_model=List[DoctorResponse])
def get_all_doctors(department: str = None, specialization: str = None, db: Session = Depends(get_db)):
    """Get a list of all doctors. Can filter by department or specialization."""
    query = db.query(Doctor).options(joinedload(Doctor.schedules))
    
    if department:
        query = query.filter(Doctor.department.ilike(f"%{department}%"))
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
        
    return query.all()

@router.get("/specialization/{spec_type}", response_model=List[DoctorResponse])
def get_doctors_by_specialization(spec_type: str, db: Session = Depends(get_db)):
    """Get all doctors matching a specific specialization (e.g., cardiology)."""
    doctors = db.query(Doctor).options(joinedload(Doctor.schedules)).filter(
        Doctor.specialization.ilike(f"%{spec_type}%")
    ).all()
    if not doctors:
        raise HTTPException(status_code=404, detail=f"No doctors found with specialization: {spec_type}")
    return doctors

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(doctor_id: str, db: Session = Depends(get_db)):
    """Get a specific doctor by ID, including their availability schedule."""
    doctor = db.query(Doctor).options(joinedload(Doctor.schedules)).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.get("/{doctor_id}/schedule", response_model=List[DoctorScheduleResponse])
def get_doctor_schedule(doctor_id: str, db: Session = Depends(get_db)):
    """Get only the schedule/availability for a specific doctor."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    schedules = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.is_available == True
    ).all()
    return schedules