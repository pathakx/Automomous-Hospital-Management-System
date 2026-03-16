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

logger = logging.getLogger(__name__)

# Implementations added in Part 3
