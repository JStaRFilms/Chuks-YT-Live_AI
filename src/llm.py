import os
import asyncio
from groq import AsyncGroq
import logging
import groq
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Singleton Groq client — reuse connections
_client: AsyncGroq | None = None

def _get_client() -> AsyncGroq:
    """Get or create the singleton Groq client."""
    global _client
    api_key = os.getenv("GROQ_API_KEY")
    if _client is None:
        _client = AsyncGroq(api_key=api_key)
    return _client

async def chat_completion(messages: list[dict]) -> str:
    """
    Call Groq API with the given messages. Retries once on error.
    Non-streaming fallback for /chat endpoint.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.error("GROQ_API_KEY is not set or is invalid.")
        return "Error: GROQ_API_KEY is not configured properly."

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = _get_client()

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

async def chat_completion_stream(messages: list[dict]) -> AsyncGenerator[str, None]:
    """
    Stream Groq API response, yielding complete sentences as they arrive.
    Buffers tokens until a sentence boundary (. ! ?) is hit, then yields.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.error("GROQ_API_KEY is not set or is invalid.")
        yield "Error: GROQ_API_KEY is not configured properly."
        return

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = _get_client()

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=150,
            temperature=0.8,
            stream=True,
        )

        buffer = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                buffer += delta.content
                
                # Check for sentence boundaries
                while any(punct in buffer for punct in ['. ', '! ', '? ', '.\n', '!\n', '?\n']):
                    # Find the earliest sentence boundary
                    earliest_pos = len(buffer)
                    for punct in ['. ', '! ', '? ', '.\n', '!\n', '?\n']:
                        pos = buffer.find(punct)
                        if pos != -1 and pos < earliest_pos:
                            earliest_pos = pos
                    
                    # Split at the boundary (include the punctuation)
                    sentence = buffer[:earliest_pos + 1].strip()
                    buffer = buffer[earliest_pos + 1:].lstrip()
                    
                    if sentence:
                        yield sentence

        # Yield any remaining buffer
        if buffer.strip():
            yield buffer.strip()

    except Exception as e:
        logger.error(f"Error during streaming LLM call: {e}")
        yield f"Error: {e}"
