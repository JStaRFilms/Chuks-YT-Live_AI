import os
import sys
import time
import httpx
import logging
import asyncio
import subprocess
from dotenv import load_dotenv
import sounddevice as sd

# Configure logging for startup script
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] STARTUP: %(message)s")
logger = logging.getLogger(__name__)

async def check_kokoro():
    logger.info("Checking Kokoro TTS connectivity...")
    kokoro_url = os.getenv("KOKORO_BASE_URL", "http://localhost:8880")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{kokoro_url}/v1/models")
            if response.status_code == 200:
                logger.info("✅ Kokoro TTS is reachable.")
                return True
            else:
                logger.warning(f"⚠️ Kokoro TTS returned unexpected status: {response.status_code}")
                return False
    except Exception as e:
        logger.warning(f"⚠️ Kokoro TTS is NOT reachable at {kokoro_url}. Error: {e}")
        logger.warning("Make sure Kokoro is running, or TTS will fail.")
        return False

def check_env():
    logger.info("Checking environment variables...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.error("❌ GROQ_API_KEY is not set or is invalid in .env")
        return False
    logger.info("✅ GROQ_API_KEY is configured.")
    return True

def check_audio_devices():
    logger.info("Checking audio devices...")
    try:
        devices = sd.query_devices()
        
        mic_idx_str = os.getenv("MIC_DEVICE_INDEX")
        out_idx_str = os.getenv("OUTPUT_DEVICE_INDEX")
        
        mic_valid = False
        out_valid = False
        
        logger.info("--- Available Audio Devices ---")
        for i, dev in enumerate(devices):
            logger.info(f"[{i}] {dev['name']} (In: {dev['max_input_channels']}, Out: {dev['max_output_channels']})")
            
        if mic_idx_str is not None:
            try:
                mic_idx = int(mic_idx_str)
                if 0 <= mic_idx < len(devices) and devices[mic_idx]['max_input_channels'] > 0:
                    logger.info(f"✅ MIC_DEVICE_INDEX={mic_idx} is valid: {devices[mic_idx]['name']}")
                    mic_valid = True
                else:
                    logger.error(f"❌ MIC_DEVICE_INDEX={mic_idx} is INVALID (index out of range or no input channels).")
            except ValueError:
                logger.error(f"❌ MIC_DEVICE_INDEX={mic_idx_str} is not an integer.")
        else:
            logger.info("⚠️ MIC_DEVICE_INDEX not set, using default audio input.")
            mic_valid = True  # Assuming default works
            
        if out_idx_str is not None:
            try:
                out_idx = int(out_idx_str.split()[0]) # handle trailing comments if any
                if 0 <= out_idx < len(devices) and devices[out_idx]['max_output_channels'] > 0:
                    logger.info(f"✅ OUTPUT_DEVICE_INDEX={out_idx} is valid: {devices[out_idx]['name']}")
                    out_valid = True
                else:
                    logger.error(f"❌ OUTPUT_DEVICE_INDEX={out_idx} is INVALID (index out of range or no output channels).")
            except ValueError:
                logger.error(f"❌ OUTPUT_DEVICE_INDEX={out_idx_str} is not an integer.")
        else:
            logger.info("⚠️ OUTPUT_DEVICE_INDEX not set, using default audio output.")
            out_valid = True

        return mic_valid and out_valid
    except Exception as e:
        logger.error(f"❌ Error checking audio devices: {e}")
        return False

async def main():
    logger.info("=========================================")
    logger.info("      Chuks AI Stream Companion          ")
    logger.info("          Pre-flight Checks              ")
    logger.info("=========================================")
    
    load_dotenv()
    
    env_ok = check_env()
    kokoro_ok = await check_kokoro()
    audio_ok = check_audio_devices()
    
    logger.info("=========================================")
    if not env_ok:
        logger.error("🛑 Cannot start: GROQ_API_KEY is missing.")
        sys.exit(1)
        
    if not audio_ok:
        logger.warning("⚠️ Audio devices might be misconfigured. Continuing anyway, but you may experience issues.")
        
    if not kokoro_ok:
        logger.warning("⚠️ Kokoro TTS not reachable. The AI will not speak.")
        
    logger.info("🚀 All critical checks passed. Launching orchestrator...")
    logger.info("=========================================")
    
    # Launch uvicorn
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"], check=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error running uvicorn: {e}")

if __name__ == "__main__":
    asyncio.run(main())
