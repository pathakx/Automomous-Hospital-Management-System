"""
prescription_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for prescription retrieval:
  - get_last_prescription
  - get_prescription_history

All functions accept a SQLAlchemy database session and return ToolResult.
"""
import logging
from sqlalchemy.orm import Session

from app.schemas.tool_result import ToolResult
from app.models.prescription import Prescription
from app.models.doctor import Doctor

logger = logging.getLogger(__name__)


def _prescription_to_dict(p: Prescription) -> dict:
    """Converts a Prescription ORM object to a serializable dict."""
    return {
        "prescription_id": p.id,
        "medication": p.medication,
        "dosage": p.dosage,
        "instructions": p.instructions,
        "doctor_name": p.doctor.name if p.doctor else "Unknown",
        "date": str(p.created_at.date()) if p.created_at else None,
    }


# ---------------------------------------------------------------------------
# Tool 1: get_last_prescription
# ---------------------------------------------------------------------------
def get_last_prescription(db: Session, patient_id: str) -> ToolResult:
    """
    Returns the most recently issued prescription for a patient.

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.

    Returns:
        ToolResult with data={"prescription": {...}}, or error="no_prescriptions_found".
    """
    logger.info(f"[Tool] get_last_prescription | patient={patient_id}")

    try:
        prescription = (
            db.query(Prescription)
            .filter(Prescription.patient_id == patient_id)
            .order_by(Prescription.created_at.desc())
            .first()
        )

        if not prescription:
            logger.warning(f"[Tool] No prescriptions found for patient={patient_id}")
            return ToolResult(success=False, error="no_prescriptions_found")

        logger.info(f"[Tool] Returning latest prescription id={prescription.id}")
        return ToolResult(
            success=True,
            data={"prescription": _prescription_to_dict(prescription)},
        )

    except Exception as e:
        logger.error(f"[Tool] get_last_prescription error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 2: get_prescription_history
# ---------------------------------------------------------------------------
def get_prescription_history(db: Session, patient_id: str) -> ToolResult:
    """
    Returns the full list of prescriptions for a patient, ordered newest first.

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.

    Returns:
        ToolResult with data={"prescriptions": [...]}, or error="no_prescriptions_found".
    """
    logger.info(f"[Tool] get_prescription_history | patient={patient_id}")

    try:
        prescriptions = (
            db.query(Prescription)
            .filter(Prescription.patient_id == patient_id)
            .order_by(Prescription.created_at.desc())
            .all()
        )

        if not prescriptions:
            return ToolResult(success=False, error="no_prescriptions_found")

        prescription_list = [_prescription_to_dict(p) for p in prescriptions]

        logger.info(
            f"[Tool] Found {len(prescription_list)} prescription(s) for patient={patient_id}"
        )
        return ToolResult(
            success=True,
            data={"prescriptions": prescription_list, "count": len(prescription_list)},
        )

    except Exception as e:
        logger.error(f"[Tool] get_prescription_history error: {e}")
        return ToolResult(success=False, error="internal_error")
