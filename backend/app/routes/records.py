from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.prescription import Prescription
from app.models.lab_report import LabReport
from app.models.bill import Bill
from app.schemas.hospital import PrescriptionResponse, LabReportResponse, BillResponse, BillPayment
from app.services.deps import get_current_patient
from app.services.billing_service import get_pending_bills, pay_bill as process_payment
from app.services.report_service import get_report_by_id

router = APIRouter(prefix="/records", tags=["Patient Records"])

@router.get("/prescriptions", response_model=List[PrescriptionResponse])
def get_my_prescriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch all prescriptions for the currently logged-in patient."""
    return db.query(Prescription).filter(Prescription.patient_id == current_user.linked_id).all()

@router.get("/prescriptions/latest", response_model=PrescriptionResponse)
def get_my_latest_prescription(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch the most recent prescription for the currently logged-in patient."""
    prescription = db.query(Prescription).filter(
        Prescription.patient_id == current_user.linked_id
    ).order_by(Prescription.created_at.desc()).first()
    
    if not prescription:
        raise HTTPException(status_code=404, detail="No prescriptions found")
    return prescription

@router.get("/reports", response_model=List[LabReportResponse])
def get_my_lab_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch all medical lab reports for the currently logged-in patient."""
    return db.query(LabReport).filter(LabReport.patient_id == current_user.linked_id).all()

@router.get("/reports/{report_id}", response_model=LabReportResponse)
def get_report(report_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch a specific lab report by its ID. Only returns if it belongs to the logged-in patient."""
    report = db.query(LabReport).filter(
        LabReport.id == report_id,
        LabReport.patient_id == current_user.linked_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/bills", response_model=List[BillResponse])
def get_my_bills(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch all billing statements and payment statuses."""
    return db.query(Bill).filter(Bill.patient_id == current_user.linked_id).all()

@router.get("/bills/pending", response_model=List[BillResponse])
def get_my_pending_bills(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch only unpaid/pending bills for the currently logged-in patient."""
    return get_pending_bills(db, current_user.linked_id)

@router.post("/bills/pay")
def pay_my_bill(payment_in: BillPayment, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Pay a specific bill."""
    bill = process_payment(db, payment_in.bill_id, current_user.linked_id, payment_in.payment_method)
    return {"message": "Payment successful", "bill_id": bill.id, "status": bill.payment_status}