from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.user import User
from app.models.prescription import Prescription
from app.models.lab_report import LabReport
from app.schemas.hospital import AppointmentResponse, PrescriptionResponse, PrescriptionCreate, LabReportResponse
from app.services.deps import get_current_doctor
from app.services.storage_service import StorageService

router = APIRouter(prefix="/doctor", tags=["Doctor Portal"])

@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_doctor_appointments(db: Session = Depends(get_db), current_user: User = Depends(get_current_doctor)):
    """Get all appointments booked with the currently logged-in doctor."""
    return db.query(Appointment).filter(
        Appointment.doctor_id == current_user.linked_id
    ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).all()


@router.post("/prescriptions/write", response_model=PrescriptionResponse)
def write_prescription(
    prescription_in: PrescriptionCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_doctor)
):
    """Write a new prescription for a patient."""
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == prescription_in.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    new_prescription = Prescription(
        doctor_id=current_user.linked_id,
        patient_id=prescription_in.patient_id,
        appointment_id=prescription_in.appointment_id,
        medication=prescription_in.medication,
        dosage=prescription_in.dosage,
        instructions=prescription_in.instructions
    )
    
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription


@router.post("/reports/upload", response_model=LabReportResponse)
def upload_medical_report(
    patient_id: str = Form(...),
    report_type: str = Form(...),
    report_name: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_doctor)
):
    """
    Upload a medical report (PDF/Image) for a patient.
    Requires multipart/form-data.
    """
    # 1. Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # 2. Save the physical file using our StorageService
    file_url = StorageService.save_upload_file(file)

    # 3. Save the database record
    new_report = LabReport(
        patient_id=patient_id,
        report_type=report_type,
        report_name=report_name,
        file_url=file_url
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report