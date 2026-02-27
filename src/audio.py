import asyncio
import logging
import sounddevice as sd
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

def list_devices() -> list:
    """List all available audio devices."""
    return list(sd.query_devices())

def _play_audio_blocking(audio_bytes: bytes, device_index: int, sample_rate: int = 24000) -> None:
    """
    Play audio buffer out to the specified device index.
    This is blocking, run in a thread.
    """
    try:
        # Expected from Kokoro: raw 16-bit PCM bytes at 24000Hz.
        audio = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Configure output device
        sd.default.device = (None, device_index)
        
        logger.info(f"Playing audio on device {device_index} ({len(audio_bytes)} bytes)")
        sd.play(audio, samplerate=sample_rate)
        sd.wait() # Block until done
        logger.debug("Playback finished.")
    except Exception as e:
        logger.error(f"Failed to play audio on device {device_index}: {e}")

async def play_audio(audio_bytes: bytes, device_index: Optional[int] = None, sample_rate: int = 24000) -> None:
    """Async wrapper around the blocking _play_audio_blocking function."""
    if not audio_bytes:
        logger.warning("Empty audio buffer received, skipping playback.")
        return
        
    if device_index is None:
        logger.warning("No output device index provided, using default.")
        
    await asyncio.to_thread(_play_audio_blocking, audio_bytes, device_index, sample_rate)
