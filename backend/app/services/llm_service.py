import json
import logging
from groq import Groq
from app.config import settings
from app.prompts.system_prompt import CHAT_SYSTEM_PROMPT
from app.schemas.llm import IntentResponse

logger = logging.getLogger(__name__)

# Initialize Groq client once at module load time
client = Groq(api_key=settings.GROQ_API_KEY)

def build_messages(user_message: str, history: list[dict]) -> list[dict]:
    """
    Builds the message list for the Groq API.
    - Adds the system prompt first.
    - Appends the last N turns of conversation history.
    - Appends the current user message.
    
    Args:
        user_message: The current message from the patient.
        history: A list of past messages, each with 'role' and 'text' keys.
    
    Returns:
        A list of dicts in OpenAI message format.
    """
    messages = [
        {"role": "system", "content": CHAT_SYSTEM_PROMPT}
    ]

    # Include only the last 6 messages from history to limit token usage
    recent_history = history[-6:] if len(history) > 6 else history

    for msg in recent_history:
        role = msg.get("role")  # "user" or "assistant"
        text = msg.get("text", "")
        # Only include recognized roles
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": text})

    # Finally, append the current incoming message
    messages.append({"role": "user", "content": user_message})

    return messages


async def parse_user_message(user_message: str, history: list[dict] = []) -> dict:
    """
    Sends the user's message to Groq (Llama 3 70B) and returns
    the parsed intent, entities, and confidence.

    Args:
        user_message: The text the patient typed in the chat.
        history: Previous conversation messages for context.

    Returns:
        A dictionary with keys: intent, entities (dict), confidence (float).
    """
    messages = build_messages(user_message, history)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # Groq model ID
            messages=messages,
            temperature=0.0,                    # Zero temp for deterministic, consistent output
            max_tokens=512,                     # Intent+entities JSON needs very few tokens
            response_format={"type": "json_object"}  # Force JSON-only output
        )

        raw_content = response.choices[0].message.content

        # Parse the JSON string into a Python dictionary
        parsed = json.loads(raw_content)

        # Log the parsed result for debugging
        logger.info(
            f"LLM parsed | message='{user_message}' | "
            f"intent={parsed.get('intent')} | "
            f"entities={parsed.get('entities')} | "
            f"confidence={parsed.get('confidence')}"
        )

        return parsed

    except Exception as e:
        logger.error(f"LLM service error: {e}")
        # Return fallback on any error
        return {
            "intent": "GENERAL_MEDICAL_QUERY",
            "entities": {},
            "confidence": 1.0
        }
