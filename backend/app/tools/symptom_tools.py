"""
symptom_tools.py  —  Week 5 Tool Layer

Provides AI-callable tools for symptom analysis:
  - recommend_department
  - analyze_symptoms

These tools are rule-based and do NOT require a database session.
"""
import logging
from app.schemas.tool_result import ToolResult

logger = logging.getLogger(__name__)

# Implementations added in Part 4
