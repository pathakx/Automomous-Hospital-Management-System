"""
tool_router.py  —  Week 5 Tool Layer

Central router that maps LLM intent output → tool execution.

Entry point: route_to_tool(intent, entities, patient_id, db)

Design rules:
- Returns ToolResult in EVERY code path. Never raises exceptions.
- patient_id must always be present and non-empty (security guard).
- For BOOK_APPOINTMENT: if no doctor_id is given but specialization is,
  show available doctors first (appointment options flow).
- For GENERAL_MEDICAL_QUERY: return a static helpful ToolResult (no DB call).
- Log every routing decision and result.
"""
import logging
from sqlalchemy.orm import Session

from app.schemas.tool_result import ToolResult

# --- Appointment Tools (Part 2) ---
from app.tools.appointment_tools import (
    get_doctors_by_specialization,
    get_available_slots,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
)

# --- Report Tools (Part 3) ---
from app.tools.report_tools import (
    get_lab_reports,
    get_report_details,
)

# --- Prescription Tools (Part 3) ---
from app.tools.prescription_tools import (
    get_last_prescription,
    get_prescription_history,
)

# --- Billing Tools (Part 3) ---
from app.tools.billing_tools import (
    get_pending_bills,
    get_bill_details,
    pay_bill,
    generate_invoice,
)

# --- Symptom Tools (Part 4) ---
from app.tools.symptom_tools import (
    analyze_symptoms,
    recommend_department,
)

logger = logging.getLogger(__name__)


async def route_to_tool(
    intent: str,
    entities: dict,
    patient_id: str,
    db: Session,
) -> ToolResult:
    """
    Routes the LLM's detected intent to the correct tool function.

    Args:
        intent:     Detected intent string (e.g., "VIEW_REPORT").
        entities:   Extracted entity dict from LLM (e.g., {"report_type": "blood"}).
        patient_id: UUID of the authenticated patient (from JWT, not request body).
        db:         SQLAlchemy database session (injected by FastAPI).

    Returns:
        ToolResult — always. The chat endpoint never receives a raw exception.
    """
    logger.info(
        f"[Router] Routing | intent={intent} | "
        f"patient={patient_id} | entities={entities}"
    )

    # -----------------------------------------------------------------------
    # Security Guard: patient_id must be present
    # -----------------------------------------------------------------------
    if not patient_id or patient_id.strip() == "":
        logger.error("[Router] patient_id is missing — unauthenticated request blocked.")
        return ToolResult(success=False, error="unauthenticated")

    # -----------------------------------------------------------------------
    # Intent Routing
    # -----------------------------------------------------------------------

    # --- BOOK_APPOINTMENT ---
    if intent == "BOOK_APPOINTMENT":
        doctor_id = entities.get("doctor_id")
        specialization = entities.get("specialization")
        date_str = entities.get("date")
        time_str = entities.get("time")

        # If no doctor_id but we have a specialization → show doctor options first
        if not doctor_id and specialization:
            logger.info(
                f"[Router] BOOK_APPOINTMENT: no doctor_id — "
                f"fetching doctors for specialization='{specialization}'"
            )
            return get_doctors_by_specialization(db, specialization)

        # If we have a doctor_id, date, and time → book immediately
        if doctor_id and date_str and time_str:
            return book_appointment(db, patient_id, doctor_id, date_str, time_str)

        # Missing required entities
        logger.warning(
            f"[Router] BOOK_APPOINTMENT: insufficient entities — {entities}"
        )
        return ToolResult(
            success=False,
            error="missing_entities",
            data={
                "required": ["doctor_id or specialization", "date", "time"],
                "received": entities,
                "hint": "Please specify the doctor specialization, date, and time.",
            },
        )

    # --- CHECK_DOCTOR_AVAILABILITY ---
    elif intent == "CHECK_DOCTOR_AVAILABILITY":
        doctor_id = entities.get("doctor_id")
        specialization = entities.get("specialization")
        date_str = entities.get("date")

        # If we have doctor_id + date → get available slots
        if doctor_id and date_str:
            return get_available_slots(db, doctor_id, date_str)

        # If we have specialization but no doctor_id → find doctors first
        if specialization:
            logger.info(
                f"[Router] CHECK_DOCTOR_AVAILABILITY: "
                f"no doctor_id — listing doctors for '{specialization}'"
            )
            return get_doctors_by_specialization(db, specialization)

        # Missing required entities
        return ToolResult(
            success=False,
            error="missing_entities",
            data={
                "required": ["doctor_id + date OR specialization"],
                "received": entities,
            },
        )

    # --- CANCEL_APPOINTMENT ---
    elif intent == "CANCEL_APPOINTMENT":
        appointment_id = entities.get("appointment_id")

        if not appointment_id:
            return ToolResult(
                success=False,
                error="missing_entities",
                data={
                    "required": ["appointment_id"],
                    "received": entities,
                    "hint": "Please provide the appointment ID to cancel.",
                },
            )

        return cancel_appointment(db, patient_id, appointment_id)

    # --- RESCHEDULE_APPOINTMENT ---
    elif intent == "RESCHEDULE_APPOINTMENT":
        appointment_id = entities.get("appointment_id")
        new_date = entities.get("date")
        new_time = entities.get("time")

        if not appointment_id or not new_date or not new_time:
            return ToolResult(
                success=False,
                error="missing_entities",
                data={
                    "required": ["appointment_id", "date", "time"],
                    "received": entities,
                    "hint": "Please provide the appointment ID, new date, and new time.",
                },
            )

        return reschedule_appointment(
            db, patient_id, appointment_id, new_date, new_time
        )

    # --- VIEW_REPORT ---
    elif intent == "VIEW_REPORT":
        report_id = entities.get("report_id")
        report_type = entities.get("report_type")  # Optional filter

        # If a specific report_id is given → fetch its details
        if report_id:
            return get_report_details(db, patient_id, report_id)

        # Otherwise list all reports (optionally filtered by type)
        return get_lab_reports(db, patient_id, report_type=report_type)

    # --- VIEW_PRESCRIPTION ---
    elif intent == "VIEW_PRESCRIPTION":
        # Return the most recent prescription
        return get_last_prescription(db, patient_id)

    # --- VIEW_BILLS ---
    elif intent == "VIEW_BILLS":
        # Return all pending (unpaid) bills
        return get_pending_bills(db, patient_id)

    # --- PAY_BILL ---
    elif intent == "PAY_BILL":
        bill_id = entities.get("bill_id")

        if not bill_id:
            # No specific bill_id — first show pending bills so user can choose
            logger.info(
                "[Router] PAY_BILL: no bill_id in entities — "
                "returning pending bills list for user to select."
            )
            return get_pending_bills(db, patient_id)

        return pay_bill(db, patient_id, bill_id)

    # --- SYMPTOM_ANALYSIS ---
    elif intent == "SYMPTOM_ANALYSIS":
        symptoms = entities.get("symptoms", [])
        age = entities.get("age")          # Optional
        duration = entities.get("duration")  # Optional (LLM may extract this)

        if not symptoms:
            return ToolResult(
                success=False,
                error="missing_entities",
                data={
                    "required": ["symptoms"],
                    "received": entities,
                    "hint": "Please describe your symptoms.",
                },
            )

        return analyze_symptoms(symptoms, age=age, duration=duration)

    # --- GENERAL_MEDICAL_QUERY (fallback + catch-all) ---
    else:
        logger.info(
            f"[Router] GENERAL_MEDICAL_QUERY or unknown intent='{intent}' "
            f"— returning static helpful response."
        )
        return ToolResult(
            success=True,
            data={
                "message": (
                    "I'm here to help! You can ask me to:\n"
                    "• Book, cancel, or reschedule appointments\n"
                    "• Check doctor availability\n"
                    "• View your lab reports or prescriptions\n"
                    "• View or pay your bills\n"
                    "• Analyze your symptoms\n\n"
                    "How can I assist you today?"
                )
            },
        )
