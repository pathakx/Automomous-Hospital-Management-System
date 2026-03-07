from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from datetime import date, time


def validate_doctor_exists(db: Session, doctor_id: str) -> Doctor:
    """Check that the doctor exists, raise 404 if not."""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


def check_slot_conflict(db: Session, doctor_id: str, appt_date: date, appt_time: time) -> None:
    """Check that the requested time slot is not already booked."""
    conflict = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appt_date,
        Appointment.appointment_time == appt_time,
        Appointment.status == "scheduled"
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="This time slot is already booked.")


def create_appointment(db: Session, patient_id: str, doctor_id: str, appt_date: date, appt_time: time) -> Appointment:
    """Create and persist a new appointment."""
    new_appt = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        status="scheduled"
    )
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)
    return new_appt


def cancel_appointment(db: Session, appointment: Appointment) -> Appointment:
    """Cancel a scheduled appointment."""
    if appointment.status == "cancelled":
        raise HTTPException(status_code=400, detail="Appointment is already cancelled.")
    appointment.status = "cancelled"
    db.commit()
    db.refresh(appointment)
    return appointment


def reschedule_appointment(db: Session, appointment: Appointment, new_date: date, new_time: time) -> Appointment:
    """Reschedule an existing appointment to a new date/time."""
    if appointment.status == "cancelled":
        raise HTTPException(status_code=400, detail="Cannot reschedule a cancelled appointment.")
    
    # Check new slot is free
    check_slot_conflict(db, appointment.doctor_id, new_date, new_time)
    
    appointment.appointment_date = new_date
    appointment.appointment_time = new_time
    appointment.status = "rescheduled"
    db.commit()
    db.refresh(appointment)
    return appointment