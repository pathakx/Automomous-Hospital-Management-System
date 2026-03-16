import logging
from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.user import User
from app.services.deps import get_current_patient
from app.services.llm_service import parse_user_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_in: ChatRequest,
    current_user: User = Depends(get_current_patient)
):
    """
    Week 4 Chat Endpoint.
    Receives a user message + conversation history, passes it to the LLM service,
    and returns the detected intent and entities as a readable reply.
    """

    # Convert ChatMessage objects into plain dicts for llm_service
    history_dicts = [
        {"role": msg.role, "text": msg.text}
        for msg in chat_in.history
    ]

    # Call the LLM service
    result = await parse_user_message(
        user_message=chat_in.message,
        history=history_dicts
    )

    intent = result.get("intent", "GENERAL_MEDICAL_QUERY")
    entities = result.get("entities", {})
    confidence = result.get("confidence", 1.0)

    logger.info(
        f"Chat | user={current_user.email} | "
        f"intent={intent} | confidence={confidence}"
    )

    # Build a human-readable reply for the chat bubble
    # In Week 5, this will be replaced by real tool execution
    readable_entities = ", ".join(
        f"{k}={v}" for k, v in entities.items() if v
    ) if entities else "none"

    reply = (
        f"I understand you want to: **{intent}**.\n"
        f"Extracted details: {readable_entities}.\n\n"
        f"_(Week 4: Intent detection is live! Tool execution coming in Week 5.)_"
    )

    return ChatResponse(
        reply=reply,
        intent=intent,
        type="text",
        data=None
    )
