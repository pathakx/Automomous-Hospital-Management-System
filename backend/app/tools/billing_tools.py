"""
billing_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for billing and payments:
  - get_pending_bills
  - get_bill_details
  - pay_bill
  - generate_invoice

All functions accept a SQLAlchemy database session and return ToolResult.
"""
import logging
from sqlalchemy.orm import Session
from app.schemas.tool_result import ToolResult

logger = logging.getLogger(__name__)

# Implementations added in Part 3
