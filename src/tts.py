import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

async def text_to_speech(text: str) -> Optional[bytes]:
    """
    Sends text to the local Kokoro TTS engine and returns raw PCM bytes.
    Expects KOKORO_BASE_URL and KOKORO_VOICE to be set in the environment.
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
        async with httpx.AsyncClient(timeout=30.0) as client:
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
