from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.models.user import User
from app.services.deps import get_current_patient
import time

router = APIRouter(prefix="/chat", tags=["AI Chatbot"])

@router.post("/message", response_model=ChatResponse)
def send_message(
    chat_in: ChatRequest, 
    current_user: User = Depends(get_current_patient)
):
    """
    Mocked Chat Endpoint for Week 3 Frontend testing.
    Accepts a message, waits briefly to simulate AI thinking, and returns a dummy response.
    """
    
    # Simulate AI processing delay
    time.sleep(1)
    
    # Return a mocked response
    mock_reply = f"I received your message: '{chat_in.message}'. This is a stub response — real AI will be connected in Week 5!"
    
    return ChatResponse(reply=mock_reply)