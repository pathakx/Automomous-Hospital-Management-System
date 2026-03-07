from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.bill import Bill


def get_patient_bills(db: Session, patient_id: str):
    """Get all bills for a patient."""
    return db.query(Bill).filter(Bill.patient_id == patient_id).all()


def get_pending_bills(db: Session, patient_id: str):
    """Get only unpaid/pending bills for a patient."""
    return db.query(Bill).filter(
        Bill.patient_id == patient_id,
        Bill.payment_status == "pending"
    ).all()


def pay_bill(db: Session, bill_id: str, patient_id: str, payment_method: str) -> Bill:
    """Process payment for a specific bill."""
    bill = db.query(Bill).filter(
        Bill.id == bill_id,
        Bill.patient_id == patient_id
    ).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    if bill.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Bill is already paid.")

    bill.payment_status = "paid"
    db.commit()
    db.refresh(bill)
    return bill