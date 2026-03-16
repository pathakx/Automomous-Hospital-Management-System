from pydantic import BaseModel
from typing import Optional, Any

class ChatMessage(BaseModel):
    """Represents a single past message in the conversation history."""
    role: str           # "user" or "assistant"
    text: str           # The text content of the message

class ChatRequest(BaseModel):
    message: str
    patient_id: Optional[str] = None         # Linked patient UUID from frontend
    conversation_id: Optional[str] = None    # For future memory persistence (Week 7)
    history: list[ChatMessage] = []          # Previous messages for LLM context

class ChatResponse(BaseModel):
    reply: str                               # Human-readable text shown in chat bubble
    intent: Optional[str] = None            # The detected intent (for frontend/debug)
    type: str = "text"                      # Response type: "text", "appointment_options", etc.
    data: Optional[Any] = None              # Structured data payload (used from Week 5+)
    conversation_id: Optional[str] = None   # Echo back for frontend to store