from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from typing import List

from app.database import get_db
from app.models.doctor import Doctor
from app.schemas.hospital import DoctorResponse

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

@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor_by_id(doctor_id: str, db: Session = Depends(get_db)):
    """Get a specific doctor by ID, including their availability schedule."""
    doctor = db.query(Doctor).options(joinedload(Doctor.schedules)).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor