from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.hospital import AppointmentCreate, AppointmentResponse
from app.services.deps import get_current_patient

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/book", response_model=AppointmentResponse)
def book_appointment(appt_in: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Book a new appointment. Requires a valid Patient JWT."""
    
    # 1. Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == appt_in.doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
        
    # 2. Prevent double booking for the exact same doctor and time
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == appt_in.doctor_id,
        Appointment.appointment_date == appt_in.appointment_date,
        Appointment.appointment_time == appt_in.appointment_time,
        Appointment.status == "scheduled"
    ).first()
    
    if conflict:
        raise HTTPException(status_code=409, detail="This time slot is already booked.")

    # 3. Create the appointment using the currently logged in user's linked_id!
    new_appt = Appointment(
        patient_id=current_user.linked_id,
        doctor_id=appt_in.doctor_id,
        appointment_date=appt_in.appointment_date,
        appointment_time=appt_in.appointment_time,
        status="scheduled"
    )
    
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)
    
    return db.query(Appointment).options(joinedload(Appointment.doctor)).filter(Appointment.id == new_appt.id).first()

@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Get all appointments for the currently logged-in patient."""
    appointments = db.query(Appointment).options(joinedload(Appointment.doctor)).filter(
        Appointment.patient_id == current_user.linked_id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return appointments