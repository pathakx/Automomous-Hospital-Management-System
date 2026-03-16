"""
appointment_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for all appointment operations:
  - get_doctors_by_specialization
  - get_available_slots
  - book_appointment
  - cancel_appointment
  - reschedule_appointment

All functions accept a SQLAlchemy database session and return ToolResult.
"""
import logging
from sqlalchemy.orm import Session
from app.schemas.tool_result import ToolResult

logger = logging.getLogger(__name__)

# Implementations added in Part 2
