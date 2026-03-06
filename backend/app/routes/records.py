from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.prescription import Prescription
from app.models.lab_report import LabReport
from app.models.bill import Bill
from app.schemas.hospital import PrescriptionResponse, LabReportResponse, BillResponse, BillPayment
from app.services.deps import get_current_patient

router = APIRouter(prefix="/records", tags=["Patient Records"])

@router.get("/prescriptions", response_model=List[PrescriptionResponse])
def get_my_prescriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch all prescriptions for the currently logged-in patient."""
    return db.query(Prescription).filter(Prescription.patient_id == current_user.linked_id).all()

@router.get("/reports", response_model=List[LabReportResponse])
def get_my_lab_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch all medical lab reports for the currently logged-in patient."""
    return db.query(LabReport).filter(LabReport.patient_id == current_user.linked_id).all()

@router.get("/bills", response_model=List[BillResponse])
def get_my_bills(db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Fetch all billing statements and payment statuses."""
    return db.query(Bill).filter(Bill.patient_id == current_user.linked_id).all()

@router.post("/bills/pay")
def pay_bill(payment_in: BillPayment, db: Session = Depends(get_db), current_user: User = Depends(get_current_patient)):
    """Pay a specific bill."""
    bill = db.query(Bill).filter(Bill.id == payment_in.bill_id, Bill.patient_id == current_user.linked_id).first()
    if not bill:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Bill not found")
    
    bill.payment_status = f"paid via {payment_in.payment_method}"
    db.commit()
    db.refresh(bill)
    return {"message": "Payment successful", "bill": bill}