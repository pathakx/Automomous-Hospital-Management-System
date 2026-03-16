"""
appointment_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for all appointment operations:
  - get_doctors_by_specialization
  - get_available_slots
  - book_appointment
  - cancel_appointment
  - reschedule_appointment

All functions return ToolResult. They catch exceptions internally and
never raise HTTPException — the AI layer is not an HTTP context.
"""
import logging
import uuid
from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session

from app.schemas.tool_result import ToolResult
from app.models.doctor import Doctor
from app.models.doctor_schedule import DoctorSchedule
from app.models.appointment import Appointment
from app.services.appointment_service import (
    validate_doctor_exists,
    check_slot_conflict,
    create_appointment,
    cancel_appointment as svc_cancel,
    reschedule_appointment as svc_reschedule,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool 1: get_doctors_by_specialization
# ---------------------------------------------------------------------------
def get_doctors_by_specialization(db: Session, specialization: str) -> ToolResult:
    """
    Finds doctors whose specialization matches the given string (case-insensitive).

    Args:
        db:             Database session.
        specialization: e.g., "cardiology", "dermatology"

    Returns:
        ToolResult with data=list of doctor dicts, or error="no_doctors_found".
    """
    logger.info(f"[Tool] get_doctors_by_specialization | specialization={specialization}")

    try:
        doctors = (
            db.query(Doctor)
            .filter(Doctor.specialization.ilike(f"%{specialization}%"))
            .all()
        )

        if not doctors:
            logger.warning(f"No doctors found for specialization: {specialization}")
            return ToolResult(success=False, error="no_doctors_found")

        doctor_list = [
            {
                "doctor_id": d.id,
                "name": d.name,
                "specialization": d.specialization,
                "department": d.department,
                "consultation_fee": d.consultation_fee,
                "experience_years": d.experience_years,
            }
            for d in doctors
        ]

        logger.info(f"[Tool] Found {len(doctor_list)} doctor(s) for '{specialization}'")
        return ToolResult(success=True, data={"doctors": doctor_list})

    except Exception as e:
        logger.error(f"[Tool] get_doctors_by_specialization error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 2: get_available_slots
# ---------------------------------------------------------------------------
def get_available_slots(db: Session, doctor_id: str, date_str: str) -> ToolResult:
    """
    Returns available 30-minute time slots for a doctor on a given date.
    Slots are generated from the doctor's weekly schedule (DoctorSchedule)
    and filtered against existing Appointment records.

    Args:
        db:         Database session.
        doctor_id:  UUID of the doctor.
        date_str:   ISO date string e.g., "2026-03-20". Also accepts "tomorrow".

    Returns:
        ToolResult with data={"slots": ["09:00", "09:30", ...]}, or error code.
    """
    logger.info(f"[Tool] get_available_slots | doctor_id={doctor_id} | date={date_str}")

    try:
        # Resolve relative date strings
        if date_str.lower() == "tomorrow":
            target_date = date.today() + timedelta(days=1)
        elif date_str.lower() == "today":
            target_date = date.today()
        else:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        day_name = target_date.strftime("%A")  # e.g., "Monday"

        # Get doctor's schedule for that day
        schedule = (
            db.query(DoctorSchedule)
            .filter(
                DoctorSchedule.doctor_id == doctor_id,
                DoctorSchedule.day_of_week == day_name,
                DoctorSchedule.is_available == True,
            )
            .first()
        )

        if not schedule:
            return ToolResult(success=False, error="no_schedule_for_day")

        # Generate 30-minute slots between start_time and end_time
        slots = []
        current = datetime.combine(target_date, schedule.start_time)
        end = datetime.combine(target_date, schedule.end_time)
        while current < end:
            slots.append(current.strftime("%H:%M"))
            current += timedelta(minutes=30)

        # Remove slots that are already booked
        booked = db.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status == "scheduled",
        ).all()
        booked_times = {str(a.appointment_time)[:5] for a in booked}  # "HH:MM"
        available = [s for s in slots if s not in booked_times]

        if not available:
            return ToolResult(success=False, error="no_available_slots")

        logger.info(f"[Tool] {len(available)} slot(s) available on {target_date}")
        return ToolResult(success=True, data={"date": str(target_date), "slots": available})

    except ValueError as e:
        logger.error(f"[Tool] get_available_slots date parse error: {e}")
        return ToolResult(success=False, error="invalid_date_format")
    except Exception as e:
        logger.error(f"[Tool] get_available_slots error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 3: book_appointment
# ---------------------------------------------------------------------------
def book_appointment(
    db: Session,
    patient_id: str,
    doctor_id: str,
    date_str: str,
    time_str: str,
) -> ToolResult:
    """
    Books an appointment for a patient with a doctor at the requested date/time.
    Reuses appointment_service helpers for doctor validation and conflict checking.

    Args:
        db:         Database session.
        patient_id: UUID of the authenticated patient.
        doctor_id:  UUID of the doctor.
        date_str:   e.g., "2026-03-20" or "tomorrow"
        time_str:   e.g., "09:30" or "9:30 AM"

    Returns:
        ToolResult with data={"appointment_id": ..., "message": ...}, or error code.
    """
    logger.info(
        f"[Tool] book_appointment | patient={patient_id} | "
        f"doctor={doctor_id} | date={date_str} | time={time_str}"
    )

    try:
        # Resolve date
        if date_str.lower() == "tomorrow":
            appt_date = date.today() + timedelta(days=1)
        elif date_str.lower() == "today":
            appt_date = date.today()
        else:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Resolve time — handle "9:30 AM" and "09:30" formats
        time_str_clean = time_str.strip().upper()
        if "AM" in time_str_clean or "PM" in time_str_clean:
            appt_time = datetime.strptime(time_str_clean, "%I:%M %p").time()
        else:
            appt_time = datetime.strptime(time_str_clean, "%H:%M").time()

        # Validate doctor and check for slot conflict (service layer)
        validate_doctor_exists(db, doctor_id)
        check_slot_conflict(db, doctor_id, appt_date, appt_time)

        # Create the appointment
        new_appt = create_appointment(db, patient_id, doctor_id, appt_date, appt_time)

        logger.info(f"[Tool] Appointment booked: {new_appt.id}")
        return ToolResult(
            success=True,
            data={
                "appointment_id": new_appt.id,
                "doctor_id": doctor_id,
                "date": str(appt_date),
                "time": str(appt_time)[:5],
                "status": "scheduled",
                "message": f"Appointment booked for {appt_date} at {str(appt_time)[:5]}.",
            },
        )

    except Exception as e:
        err_str = str(e).lower()
        logger.error(f"[Tool] book_appointment error: {e}")
        if "not found" in err_str or "doctor" in err_str:
            return ToolResult(success=False, error="doctor_not_found")
        if "already booked" in err_str or "conflict" in err_str or "409" in err_str:
            return ToolResult(success=False, error="slot_conflict")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 4: cancel_appointment
# ---------------------------------------------------------------------------
def cancel_appointment(db: Session, patient_id: str, appointment_id: str) -> ToolResult:
    """
    Cancels a patient's appointment. Validates that the appointment belongs
    to the requesting patient before cancelling (security check).

    Args:
        db:              Database session.
        patient_id:      UUID of the authenticated patient.
        appointment_id:  UUID of the appointment to cancel.

    Returns:
        ToolResult with data={"status": "cancelled"}, or error code.
    """
    logger.info(
        f"[Tool] cancel_appointment | patient={patient_id} | appointment={appointment_id}"
    )

    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if not appt:
            return ToolResult(success=False, error="appointment_not_found")

        # Security: patient can only cancel their own appointments
        if appt.patient_id != patient_id:
            logger.warning(
                f"[Tool] Unauthorized cancel attempt: patient={patient_id} "
                f"tried to cancel appointment owned by {appt.patient_id}"
            )
            return ToolResult(success=False, error="unauthorized")

        if appt.status == "cancelled":
            return ToolResult(success=False, error="already_cancelled")

        # Cancel via service layer
        svc_cancel(db, appt)

        logger.info(f"[Tool] Appointment {appointment_id} cancelled.")
        return ToolResult(
            success=True,
            data={
                "appointment_id": appointment_id,
                "status": "cancelled",
                "message": "Your appointment has been successfully cancelled.",
            },
        )

    except Exception as e:
        logger.error(f"[Tool] cancel_appointment error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 5: reschedule_appointment
# ---------------------------------------------------------------------------
def reschedule_appointment(
    db: Session,
    patient_id: str,
    appointment_id: str,
    new_date_str: str,
    new_time_str: str,
) -> ToolResult:
    """
    Reschedules an existing appointment to a new date and time.
    Validates ownership and checks for slot conflicts.

    Args:
        db:               Database session.
        patient_id:       UUID of the authenticated patient.
        appointment_id:   UUID of the existing appointment.
        new_date_str:     New date e.g., "2026-03-25" or "tomorrow".
        new_time_str:     New time e.g., "14:00" or "2:00 PM".

    Returns:
        ToolResult with data={"status": "rescheduled", ...}, or error code.
    """
    logger.info(
        f"[Tool] reschedule_appointment | patient={patient_id} | "
        f"appointment={appointment_id} | new_date={new_date_str} | new_time={new_time_str}"
    )

    try:
        appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()

        if not appt:
            return ToolResult(success=False, error="appointment_not_found")

        if appt.patient_id != patient_id:
            return ToolResult(success=False, error="unauthorized")

        # Resolve date
        if new_date_str.lower() == "tomorrow":
            new_date = date.today() + timedelta(days=1)
        else:
            new_date = datetime.strptime(new_date_str, "%Y-%m-%d").date()

        # Resolve time
        time_str_clean = new_time_str.strip().upper()
        if "AM" in time_str_clean or "PM" in time_str_clean:
            new_time = datetime.strptime(time_str_clean, "%I:%M %p").time()
        else:
            new_time = datetime.strptime(time_str_clean, "%H:%M").time()

        # Reschedule via service layer (checks slot conflict internally)
        updated = svc_reschedule(db, appt, new_date, new_time)

        logger.info(f"[Tool] Appointment {appointment_id} rescheduled to {new_date} {new_time}")
        return ToolResult(
            success=True,
            data={
                "appointment_id": appointment_id,
                "new_date": str(new_date),
                "new_time": str(new_time)[:5],
                "status": "rescheduled",
                "message": f"Appointment rescheduled to {new_date} at {str(new_time)[:5]}.",
            },
        )

    except Exception as e:
        err_str = str(e).lower()
        logger.error(f"[Tool] reschedule_appointment error: {e}")
        if "already booked" in err_str or "409" in err_str:
            return ToolResult(success=False, error="slot_conflict")
        if "cancelled" in err_str:
            return ToolResult(success=False, error="cannot_reschedule_cancelled")
        return ToolResult(success=False, error="internal_error")
