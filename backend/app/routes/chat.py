import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.user import User
from app.services.deps import get_current_patient
from app.services.llm_service import parse_user_message
from app.tools.tool_router import route_to_tool
from app.services.response_formatter import format_tool_result

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_in: ChatRequest,
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db),
):
    """
    Week 5 Chat Endpoint — Full Tool Execution Pipeline.

    Pipeline:
        1. Receive user message + conversation history
        2. Call LLM service → detect intent + extract entities
        3. Resolve patient_id from request or JWT user
        4. Call Tool Router → execute the correct tool → get ToolResult
        5. Call Response Formatter → convert ToolResult to chat reply
        6. Return structured ChatResponse to the frontend

    Auth:   JWT Bearer token required.
    Role:   patient only (enforced by get_current_patient dependency).
    """

    # ------------------------------------------------------------------
    # Step 1: Build history list for LLM context
    # ------------------------------------------------------------------
    history_dicts = [
        {"role": msg.role, "text": msg.text}
        for msg in chat_in.history
    ]

    # ------------------------------------------------------------------
    # Step 2: Parse the user message with the LLM
    # ------------------------------------------------------------------
    logger.info(
        f"[Chat] New message | user={current_user.email} | "
        f"message='{chat_in.message[:60]}'"
    )

    llm_result = await parse_user_message(
        user_message=chat_in.message,
        history=history_dicts
    )

    intent = llm_result.get("intent", "GENERAL_MEDICAL_QUERY")
    entities = llm_result.get("entities", {})
    confidence = llm_result.get("confidence", 1.0)

    logger.info(
        f"[Chat] LLM result | intent={intent} | "
        f"confidence={confidence} | entities={entities}"
    )

    # ------------------------------------------------------------------
    # Step 3: Resolve patient_id
    # Priority: request body > JWT linked_id
    # ------------------------------------------------------------------
    patient_id = chat_in.patient_id or getattr(current_user, "linked_id", None)

    if not patient_id:
        logger.warning(
            f"[Chat] patient_id not found for user={current_user.email}. "
            f"Tool execution will be blocked by the router security guard."
        )

    # ------------------------------------------------------------------
    # Step 4: Route to the correct tool and execute
    # ------------------------------------------------------------------
    tool_result = await route_to_tool(
        intent=intent,
        entities=entities,
        patient_id=patient_id or "",
        db=db,
    )

    logger.info(
        f"[Chat] Tool result | success={tool_result.success} | "
        f"error={tool_result.error}"
    )

    # ------------------------------------------------------------------
    # Step 5: Format the tool result into a chat reply
    # ------------------------------------------------------------------
    formatted = format_tool_result(intent=intent, result=tool_result)

    reply = formatted.get("reply", "I'm here to help. How can I assist you?")
    response_type = formatted.get("type", "text")
    response_data = formatted.get("data", None)

    logger.info(
        f"[Chat] Response | type={response_type} | "
        f"reply='{reply[:80]}'"
    )

    # ------------------------------------------------------------------
    # Step 6: Return the structured ChatResponse
    # ------------------------------------------------------------------
    return ChatResponse(
        reply=reply,
        intent=intent,
        type=response_type,
        data=response_data,
        conversation_id=chat_in.conversation_id,
    )
