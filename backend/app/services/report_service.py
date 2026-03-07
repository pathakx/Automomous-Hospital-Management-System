from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.lab_report import LabReport
from app.models.patient import Patient


def validate_patient_exists(db: Session, patient_id: str) -> Patient:
    """Check that the patient exists, raise 404 if not."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


def get_report_by_id(db: Session, report_id: str) -> LabReport:
    """Get a specific lab report by its ID."""
    report = db.query(LabReport).filter(LabReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


def get_patient_reports(db: Session, patient_id: str):
    """Get all lab reports for a specific patient."""
    return db.query(LabReport).filter(LabReport.patient_id == patient_id).all()