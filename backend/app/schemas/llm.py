from pydantic import BaseModel, Field
from typing import Optional

class IntentEntities(BaseModel):
    """
    Flexible container for entities extracted from a user message.
    All fields are optional since different intents require different entities.
    """
    specialization: Optional[str] = None   # e.g., "cardiology"
    doctor_name: Optional[str] = None      # e.g., "Dr Sharma"
    date: Optional[str] = None             # e.g., "tomorrow", "2024-03-20"
    time: Optional[str] = None             # e.g., "11:30 AM", "morning"
    report_type: Optional[str] = None      # e.g., "blood", "xray"
    bill_id: Optional[str] = None          # e.g., a UUID of a bill
    symptoms: Optional[list[str]] = None   # e.g., ["chest pain", "fatigue"]
    appointment_id: Optional[str] = None   # e.g., UUID for cancellation
    doctor_id: Optional[str] = None        # e.g., UUID of a specific doctor

class IntentResponse(BaseModel):
    """
    Strict schema that the LLM must return in JSON format.
    """
    intent: str = Field(
        description="The classified intent. Must be one of the allowed values."
    )
    entities: IntentEntities = Field(
        default_factory=IntentEntities,
        description="Extracted parameters from the user message."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Model confidence in the classified intent (0.0 to 1.0)."
    )