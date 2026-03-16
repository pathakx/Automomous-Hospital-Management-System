"""
response_formatter.py  —  Week 5 Service Layer

Converts a ToolResult into a structured dict the chat endpoint returns to the frontend.

Entry point:
    format_tool_result(intent: str, result: ToolResult) -> dict

Return format:
    {
        "reply": str,        # Human-readable text displayed in the chat bubble
        "type":  str,        # "text" | "appointment_options" | "report_list" |
                             # "bill_list" | "symptom_analysis" | "prescription"
        "data":  dict|None   # Structured payload for rich frontend rendering
    }

Design rules:
- Every intent + every error code must have a friendly message.
- Never expose raw error codes or stack traces to the frontend.
- When result.success is False, always check result.error for the message.
- Type determines how the frontend renders the data payload.
"""
import logging
from app.schemas.tool_result import ToolResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Error Code → User-Friendly Message Map
# ---------------------------------------------------------------------------
ERROR_MESSAGES = {
    "no_doctors_found":           "Sorry, I couldn't find any doctors with that specialization. Please try a different specialization.",
    "no_schedule_for_day":        "That doctor doesn't appear to have working hours on that day. Please try another day.",
    "no_available_slots":         "There are no available slots on that day. Would you like to try a different date?",
    "invalid_date_format":        "I couldn't understand that date. Please use a format like 'tomorrow' or 'March 20'.",
    "doctor_not_found":           "I couldn't find that doctor in our system. Please check the details and try again.",
    "slot_conflict":              "That time slot is already booked. Please choose a different time.",
    "appointment_not_found":      "I couldn't find that appointment. Please check the appointment ID.",
    "unauthorized":               "You don't have permission to perform that action.",
    "already_cancelled":          "That appointment has already been cancelled.",
    "cannot_reschedule_cancelled":"A cancelled appointment cannot be rescheduled. Please book a new appointment.",
    "no_reports_found":           "No lab reports were found for your account.",
    "report_not_found":           "I couldn't find that specific report.",
    "no_prescriptions_found":     "No prescriptions were found for your account.",
    "no_pending_bills":           "You have no pending bills. You're all clear! ✅",
    "bill_not_found":             "I couldn't find that bill. Please verify the bill ID.",
    "already_paid":               "This bill has already been paid.",
    "no_symptoms_provided":       "Please describe your symptoms so I can assist you.",
    "no_matching_department":     "I wasn't able to identify a specific department for those symptoms. I recommend visiting General Medicine for an evaluation.",
    "missing_entities":           "I need a bit more information to complete that request.",
    "unauthenticated":            "Your session has expired. Please log in again.",
    "internal_error":             "Something went wrong on our end. Please try again in a moment.",
}


def _get_error_reply(result: ToolResult, default: str = None) -> str:
    """Returns a user-friendly error message for the given ToolResult."""
    error_code = result.error or "internal_error"
    reply = ERROR_MESSAGES.get(error_code, default or "Something went wrong. Please try again.")

    # Append a hint if the tool provided one in result.data
    if result.data and isinstance(result.data, dict):
        hint = result.data.get("hint")
        if hint:
            reply = f"{reply}\n\n💡 {hint}"

    return reply


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def format_tool_result(intent: str, result: ToolResult) -> dict:
    """
    Converts a ToolResult into a structured response dict for the chat endpoint.

    Args:
        intent: The LLM-detected intent string.
        result: The ToolResult returned by the tool router.

    Returns:
        dict with keys: "reply" (str), "type" (str), "data" (dict|None).
    """
    logger.info(
        f"[Formatter] Formatting | intent={intent} | "
        f"success={result.success} | error={result.error}"
    )

    # -----------------------------------------------------------------------
    # APPOINTMENT intents
    # -----------------------------------------------------------------------
    if intent in ("BOOK_APPOINTMENT", "CHECK_DOCTOR_AVAILABILITY"):

        if not result.success:
            return {
                "reply": _get_error_reply(result),
                "type": "text",
                "data": None,
            }

        data = result.data or {}

        # Case 1: Result contains a list of doctors (specialization search)
        if "doctors" in data:
            doctor_list = data["doctors"]
            count = len(doctor_list)
            reply = (
                f"I found **{count} doctor(s)** matching your request. "
                "Please select one and confirm the date and time to book:"
            )
            return {
                "reply": reply,
                "type": "appointment_options",
                "data": {"doctors": doctor_list},
            }

        # Case 2: Result contains available slots
        if "slots" in data:
            slots = data["slots"]
            date = data.get("date", "the selected date")
            reply = (
                f"Here are the available slots for **{date}**:\n"
                + "\n".join(f"- {s}" for s in slots[:10])  # Show max 10 slots
            )
            return {"reply": reply, "type": "text", "data": {"slots": slots, "date": date}}

        # Case 3: Appointment was successfully booked
        if "appointment_id" in data:
            reply = (
                f"✅ **Appointment booked successfully!**\n"
                f"📅 Date: {data.get('date')}\n"
                f"🕐 Time: {data.get('time')}\n"
                f"🆔 Appointment ID: `{data.get('appointment_id')}`"
            )
            return {"reply": reply, "type": "text", "data": data}

        return {"reply": "Your appointment request was processed.", "type": "text", "data": data}

    # -----------------------------------------------------------------------
    if intent == "CANCEL_APPOINTMENT":
        if not result.success:
            return {"reply": _get_error_reply(result), "type": "text", "data": None}
        return {
            "reply": "✅ Your appointment has been **successfully cancelled**.",
            "type": "text",
            "data": result.data,
        }

    # -----------------------------------------------------------------------
    if intent == "RESCHEDULE_APPOINTMENT":
        if not result.success:
            return {"reply": _get_error_reply(result), "type": "text", "data": None}
        data = result.data or {}
        reply = (
            f"✅ **Appointment rescheduled!**\n"
            f"📅 New Date: {data.get('new_date')}\n"
            f"🕐 New Time: {data.get('new_time')}"
        )
        return {"reply": reply, "type": "text", "data": data}

    # -----------------------------------------------------------------------
    if intent == "VIEW_REPORT":
        if not result.success:
            return {"reply": _get_error_reply(result), "type": "text", "data": None}
        data = result.data or {}

        # Single report details
        if "report" in data:
            r = data["report"]
            reply = (
                f"📄 **{r.get('report_name')}**\n"
                f"Type: {r.get('report_type')} | Date: {r.get('upload_date')}\n"
                f"[View Report]({r.get('file_url')})"
            )
            return {"reply": reply, "type": "text", "data": data}

        # List of reports
        reports = data.get("reports", [])
        count = data.get("count", len(reports))
        if not reports:
            return {"reply": ERROR_MESSAGES["no_reports_found"], "type": "text", "data": None}

        reply = f"I found **{count} report(s)** on your account:"
        return {"reply": reply, "type": "report_list", "data": {"reports": reports}}

    # -----------------------------------------------------------------------
    if intent == "VIEW_PRESCRIPTION":
        if not result.success:
            return {"reply": _get_error_reply(result), "type": "text", "data": None}
        data = result.data or {}
        p = data.get("prescription", {})
        reply = (
            f"💊 **Latest Prescription**\n"
            f"Medication: **{p.get('medication')}** — {p.get('dosage')}\n"
            f"Instructions: {p.get('instructions') or 'As directed'}\n"
            f"Prescribed by: Dr. {p.get('doctor_name')} on {p.get('date')}"
        )
        return {"reply": reply, "type": "prescription", "data": data}

    # -----------------------------------------------------------------------
    if intent == "VIEW_BILLS":
        if not result.success:
            return {"reply": _get_error_reply(result), "type": "text", "data": None}
        data = result.data or {}
        bills = data.get("bills", [])
        count = data.get("count", len(bills))
        total = data.get("total_due", 0)
        reply = (
            f"🧾 You have **{count} pending bill(s)** totalling **${total:.2f}**.\n"
            "Which bill would you like to pay?"
        )
        return {"reply": reply, "type": "bill_list", "data": {"bills": bills}}

    # -----------------------------------------------------------------------
    if intent == "PAY_BILL":
        if not result.success:
            return {"reply": _get_error_reply(result), "type": "text", "data": None}
        data = result.data or {}

        # If the result contains a bills list (no bill_id was given)
        if "bills" in data:
            bills = data["bills"]
            count = data.get("count", len(bills))
            total = data.get("total_due", 0)
            reply = (
                f"🧾 You have **{count} pending bill(s)** totalling **${total:.2f}**.\n"
                "Please specify which bill you'd like to pay."
            )
            return {"reply": reply, "type": "bill_list", "data": {"bills": bills}}

        # Payment was completed
        amount = data.get("amount_paid", 0)
        tx_id = data.get("transaction_id", "N/A")
        reply = (
            f"✅ **Payment successful!**\n"
            f"💰 Amount paid: **${amount:.2f}**\n"
            f"🆔 Transaction ID: `{tx_id}`"
        )
        return {"reply": reply, "type": "text", "data": data}

    # -----------------------------------------------------------------------
    if intent == "SYMPTOM_ANALYSIS":
        if not result.success:
            # Soft error: no_matching_department still has data
            if result.error == "no_matching_department" and result.data:
                dept = result.data.get("department", "General Medicine")
                reply = (
                    f"Based on your symptoms, I recommend visiting **{dept}**.\n\n"
                    f"{result.data.get('disclaimer', '')}"
                )
                return {"reply": reply, "type": "symptom_analysis", "data": result.data}
            return {"reply": _get_error_reply(result), "type": "text", "data": None}

        data = result.data or {}
        severity = data.get("severity", "unknown")
        dept = data.get("recommended_department", "General Medicine")
        conditions = data.get("possible_conditions", [])
        disclaimer = data.get("disclaimer", "")

        severity_emoji = {"mild": "🟡", "moderate": "🟠", "severe": "🔴"}.get(severity, "⚪")

        conditions_text = "\n".join(f"- {c}" for c in conditions[:5])
        reply = (
            f"{severity_emoji} **Severity: {severity.capitalize()}**\n\n"
            f"**Recommended Department:** {dept}\n\n"
            f"**Possible Conditions:**\n\n{conditions_text}\n\n"
            f"*{disclaimer}*"
        )
        return {"reply": reply, "type": "symptom_analysis", "data": data}

    # -----------------------------------------------------------------------
    # GENERAL_MEDICAL_QUERY and all unknown intents
    # -----------------------------------------------------------------------
    if not result.success:
        return {"reply": _get_error_reply(result), "type": "text", "data": None}

    data = result.data or {}
    message = data.get("message", "How can I assist you today?")
    return {"reply": message, "type": "text", "data": None}
