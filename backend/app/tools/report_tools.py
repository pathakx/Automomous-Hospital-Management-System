"""
report_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for lab report retrieval:
  - get_lab_reports
  - get_report_details

All functions accept a SQLAlchemy database session and return ToolResult.
Security: patient_id is always validated against the report's owner.
"""
import logging
from sqlalchemy.orm import Session

from app.schemas.tool_result import ToolResult
from app.models.lab_report import LabReport

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool 1: get_lab_reports
# ---------------------------------------------------------------------------
def get_lab_reports(db: Session, patient_id: str, report_type: str = None) -> ToolResult:
    """
    Retrieves all lab reports for a patient, optionally filtered by type.

    Args:
        db:           Database session.
        patient_id:   UUID of the authenticated patient.
        report_type:  Optional filter, e.g., "blood", "xray", "radiology".
                      If None, all reports are returned.

    Returns:
        ToolResult with data={"reports": [...]}, or error="no_reports_found".
    """
    logger.info(
        f"[Tool] get_lab_reports | patient={patient_id} | report_type={report_type}"
    )

    try:
        query = db.query(LabReport).filter(LabReport.patient_id == patient_id)

        if report_type:
            query = query.filter(LabReport.report_type.ilike(f"%{report_type}%"))

        reports = query.order_by(LabReport.upload_date.desc()).all()

        if not reports:
            logger.warning(f"[Tool] No reports found for patient={patient_id}")
            return ToolResult(success=False, error="no_reports_found")

        report_list = [
            {
                "report_id": r.id,
                "report_name": r.report_name,
                "report_type": r.report_type,
                "file_url": r.file_url,
                "upload_date": str(r.upload_date.date()) if r.upload_date else None,
            }
            for r in reports
        ]

        logger.info(f"[Tool] Found {len(report_list)} report(s) for patient={patient_id}")
        return ToolResult(success=True, data={"reports": report_list, "count": len(report_list)})

    except Exception as e:
        logger.error(f"[Tool] get_lab_reports error: {e}")
        return ToolResult(success=False, error="internal_error")


# ---------------------------------------------------------------------------
# Tool 2: get_report_details
# ---------------------------------------------------------------------------
def get_report_details(db: Session, patient_id: str, report_id: str) -> ToolResult:
    """
    Retrieves the full details of a specific lab report.
    Verifies that the report belongs to the requesting patient.

    Args:
        db:          Database session.
        patient_id:  UUID of the authenticated patient.
        report_id:   UUID of the target report.

    Returns:
        ToolResult with data={"report": {...}}, or error code.
    """
    logger.info(
        f"[Tool] get_report_details | patient={patient_id} | report={report_id}"
    )

    try:
        report = db.query(LabReport).filter(LabReport.id == report_id).first()

        if not report:
            return ToolResult(success=False, error="report_not_found")

        # Security: patient can only view their own reports
        if report.patient_id != patient_id:
            logger.warning(
                f"[Tool] Unauthorized access: patient={patient_id} tried to "
                f"access report owned by patient={report.patient_id}"
            )
            return ToolResult(success=False, error="unauthorized")

        return ToolResult(
            success=True,
            data={
                "report": {
                    "report_id": report.id,
                    "report_name": report.report_name,
                    "report_type": report.report_type,
                    "file_url": report.file_url,
                    "upload_date": str(report.upload_date.date()) if report.upload_date else None,
                }
            },
        )

    except Exception as e:
        logger.error(f"[Tool] get_report_details error: {e}")
        return ToolResult(success=False, error="internal_error")
