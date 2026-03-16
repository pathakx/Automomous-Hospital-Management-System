"""
billing_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for billing and payments:
  - get_pending_bills
  - get_bill_details
  - pay_bill
  - generate_invoice

All functions accept a SQLAlchemy database session and return ToolResult.
Reuses billing_service.py helpers from Week 2 where applicable.
"""
import logging
import uuid
from sqlalchemy.orm import Session

from app.schemas.tool_result import ToolResult
from app.models.bill import Bill
from app.services.billing_service import (
    get_pending_bills as svc_get_pending,
    pay_bill as svc_pay_bill,
)

logger = logging.getLogger(__name__)


def _bill_to_dict(b: Bill) -> dict:
    """Converts a Bill ORM object to a serializable dict."""
    return {
        "bill_id": b.id,
        "service_type": b.service_type,
        "amount": float(b.amount),
        "payment_status": b.payment_status,
        "created_at": str(b.created_at.date()) if b.created_at else None,
    }


# ---------------------------------------------------------------------------
# Tool 1: get_pending_bills
# ---------------------------------------------------------------------------
def get_pending_bills(db: Session, patient_id: str) -> ToolResult:
    """
    Returns all unpaid bills for a patient.

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.

    Returns:
        ToolResult with data={"bills": [...]}, or error="no_pending_bills".
    """
    logger.info(f"[Tool] get_pending_bills | patient={patient_id}")

    try:
        bills = svc_get_pending(db, patient_id)

        if not bills:
            logger.info(f"[Tool] No pending bills for patient={patient_id}")
            return ToolResult(success=False, error="no_pending_bills")

        bill_list = [_bill_to_dict(b) for b in bills]
        total = sum(b["amount"] for b in bill_list)

        logger.info(f"[Tool] Found {len(bill_list)} pending bill(s) totalling ${total:.2f}")
        return ToolResult(
            success=True,
            data={"bills": bill_list, "count": len(bill_list), "total_due": round(total, 2)},
        )

    except Exception as e:
        logger.error(f"[Tool] get_pending_bills error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 2: get_bill_details
# ---------------------------------------------------------------------------
def get_bill_details(db: Session, patient_id: str, bill_id: str) -> ToolResult:
    """
    Returns the full details of a specific bill.
    Validates that the bill belongs to the requesting patient.

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.
        bill_id:      UUID of the target bill.

    Returns:
        ToolResult with data={"bill": {...}}, or error code.
    """
    logger.info(f"[Tool] get_bill_details | patient={patient_id} | bill={bill_id}")

    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()

        if not bill:
            return ToolResult(success=False, error="bill_not_found")

        if bill.patient_id != patient_id:
            logger.warning(
                f"[Tool] Unauthorized: patient={patient_id} tried to access "
                f"bill owned by patient={bill.patient_id}"
            )
            return ToolResult(success=False, error="unauthorized")

        return ToolResult(success=True, data={"bill": _bill_to_dict(bill)})

    except Exception as e:
        logger.error(f"[Tool] get_bill_details error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 3: pay_bill
# ---------------------------------------------------------------------------
def pay_bill(db: Session, patient_id: str, bill_id: str) -> ToolResult:
    """
    Processes payment for a specific bill. Validates ownership and status.
    Reuses billing_service.pay_bill which handles the DB update.

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.
        bill_id:      UUID of the bill to pay.

    Returns:
        ToolResult with data={"payment_confirmation": True, "transaction_id": ...}, or error.
    """
    logger.info(f"[Tool] pay_bill | patient={patient_id} | bill={bill_id}")

    try:
        # billing_service.pay_bill validates ownership and paid status internally
        paid_bill = svc_pay_bill(db, bill_id, patient_id, payment_method="chatbot")

        transaction_id = str(uuid.uuid4())
        logger.info(f"[Tool] Bill {bill_id} paid. Transaction: {transaction_id}")
        return ToolResult(
            success=True,
            data={
                "payment_confirmation": True,
                "transaction_id": transaction_id,
                "bill_id": bill_id,
                "amount_paid": float(paid_bill.amount),
                "message": f"Payment of ${paid_bill.amount:.2f} processed successfully.",
            },
        )

    except Exception as e:
        err_str = str(e).lower()
        logger.error(f"[Tool] pay_bill error: {e}")
        if "not found" in err_str or "404" in err_str:
            return ToolResult(success=False, error="bill_not_found")
        if "already paid" in err_str or "400" in err_str:
            return ToolResult(success=False, error="already_paid")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 4: generate_invoice
# ---------------------------------------------------------------------------
def generate_invoice(db: Session, patient_id: str, bill_id: str) -> ToolResult:
    """
    Generates invoice data for a specific bill.
    Returns the full bill record formatted as invoice data.
    (PDF generation is out of scope for Week 5.)

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.
        bill_id:      UUID of the bill.

    Returns:
        ToolResult with data={"invoice": {...}}, or error code.
    """
    logger.info(f"[Tool] generate_invoice | patient={patient_id} | bill={bill_id}")

    try:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()

        if not bill:
            return ToolResult(success=False, error="bill_not_found")

        if bill.patient_id != patient_id:
            return ToolResult(success=False, error="unauthorized")

        invoice = {
            "invoice_number": f"INV-{bill_id[:8].upper()}",
            "bill_id": bill.id,
            "service_type": bill.service_type,
            "amount": float(bill.amount),
            "payment_status": bill.payment_status,
            "issued_date": str(bill.created_at.date()) if bill.created_at else None,
        }

        logger.info(f"[Tool] Invoice generated: {invoice['invoice_number']}")
        return ToolResult(success=True, data={"invoice": invoice})

    except Exception as e:
        logger.error(f"[Tool] generate_invoice error: {e}")
        return ToolResult(success=False, error="internal_error")
