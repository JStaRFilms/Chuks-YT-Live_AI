import os
from groq import AsyncGroq
import logging

logger = logging.getLogger(__name__)

async def chat_completion(messages: list[dict]) -> str:
    """
    Call Groq API with the given messages.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.error("GROQ_API_KEY is not set or is invalid.")
        return "Error: GROQ_API_KEY is not configured properly."

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = AsyncGroq(api_key=api_key)

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=150,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        return f"Error: Failed to get response from LLM."
