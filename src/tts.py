import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

# Singleton HTTP client — reuse connections instead of opening new ones each time
_client: Optional[httpx.AsyncClient] = None

def _get_client() -> httpx.AsyncClient:
    """Get or create the singleton httpx client for Kokoro."""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

async def text_to_speech(text: str) -> Optional[bytes]:
    """
    Sends text to the local Kokoro TTS engine and returns raw PCM bytes.
    Uses a persistent connection pool for lower latency.
    """
    if not text.strip():
        return None

    kokoro_url = os.getenv("KOKORO_BASE_URL", "http://localhost:8880")
    kokoro_voice = os.getenv("KOKORO_VOICE", "af_heart")
    
    endpoint = f"{kokoro_url}/v1/audio/speech"
    
    payload = {
        "input": text,
        "voice": kokoro_voice,
        "response_format": "pcm"
    }

    try:
        client = _get_client()
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        
        audio_bytes = response.content
        logger.info(f"Generated TTS for text ({len(text)} chars) -> {len(audio_bytes)} bytes")
        return audio_bytes
    except httpx.RequestError as e:
        logger.error(f"Error communicating with Kokoro TTS: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Kokoro TTS returned error status {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error in TTS: {e}")

    return None
