import os
import asyncio
from groq import AsyncGroq
import logging
import groq

logger = logging.getLogger(__name__)

async def chat_completion(messages: list[dict]) -> str:
    """
    Call Groq API with the given messages. Retries once on error.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.error("GROQ_API_KEY is not set or is invalid.")
        return "Error: GROQ_API_KEY is not configured properly."

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = AsyncGroq(api_key=api_key)

    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=150,
                temperature=0.8,
            )
            return response.choices[0].message.content
        except (groq.APIConnectionError, groq.APITimeoutError, groq.InternalServerError, groq.RateLimitError) as e:
            if attempt < max_retries:
                logger.warning(f"Groq API error ({type(e).__name__}) on attempt {attempt+1}, retrying... ({e})")
                await asyncio.sleep(1)
            else:
                logger.error(f"Groq API error after {max_retries+1} attempts: {e}")
                return "Error: Failed to get response from LLM (timeout or network error)."
        except Exception as e:
            logger.error(f"Unexpected error calling Groq API: {e}")
            return f"Error: Failed to get response from LLM."
            
    return "Error: Unknown failure."
