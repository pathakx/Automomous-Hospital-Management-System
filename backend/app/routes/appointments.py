from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.hospital import AppointmentCreate, AppointmentResponse, AppointmentReschedule
from app.services.deps import get_current_patient
from app.services.appointment_service import (
    validate_doctor_exists, check_slot_conflict, create_appointment,
    cancel_appointment, reschedule_appointment
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("/book", response_model=AppointmentResponse)
def book_appointment(appt_in: AppointmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Book a new appointment. Requires a valid Patient JWT."""
    
    # 1. Verify doctor exists
    validate_doctor_exists(db, appt_in.doctor_id)
        
    # 2. Prevent double booking
    check_slot_conflict(db, appt_in.doctor_id, appt_in.appointment_date, appt_in.appointment_time)

    # 3. Create the appointment
    new_appt = create_appointment(
        db, current_user.linked_id, appt_in.doctor_id,
        appt_in.appointment_date, appt_in.appointment_time
    )
    
    return db.query(Appointment).options(joinedload(Appointment.doctor)).filter(Appointment.id == new_appt.id).first()

@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Get all appointments for the currently logged-in patient."""
    appointments = db.query(Appointment).options(joinedload(Appointment.doctor)).filter(
        Appointment.patient_id == current_user.linked_id
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return appointments

@router.put("/cancel/{appointment_id}", response_model=AppointmentResponse)
def cancel_my_appointment(appointment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Cancel a scheduled appointment. Only the patient who booked it can cancel."""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_user.linked_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    updated = cancel_appointment(db, appointment)
    return updated

@router.put("/reschedule/{appointment_id}", response_model=AppointmentResponse)
def reschedule_my_appointment(
    appointment_id: str, 
    reschedule_in: AppointmentReschedule,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_patient)
):
    """Reschedule an existing appointment to a new date/time."""
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.patient_id == current_user.linked_id
    ).first()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    updated = reschedule_appointment(db, appointment, reschedule_in.appointment_date, reschedule_in.appointment_time)
    return updated