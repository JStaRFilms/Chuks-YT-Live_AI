import json
import logging
import os
import asyncio
import time
import re
from src.llm import chat_completion, chat_completion_stream
from src.tts import text_to_speech
from src.audio import play_audio
from src.ws import manager

logger = logging.getLogger(__name__)

# In-memory conversation history
conversation_history: list[dict] = []
MAX_HISTORY = 30

# Cooldown and Queue State
last_response_time: float = 0.0
trigger_queue: list[str] = []
MAX_QUEUE_SIZE = 5
is_playing_audio: bool = False

# Wake word configuration
WAKE_WORDS = ["hey chuks", "yo chuks", "chuks"]

def load_persona() -> str:
    """Load the persona configuration and build the system prompt."""
    persona_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'persona.json')
    try:
        with open(persona_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        prompt = (
            f"Your name is {data.get('name', 'Chuks')}. "
            f"Personality: {data.get('personality', '')} "
            f"Speaking Style: {data.get('speaking_style', '')} "
            f"Context: {data.get('knowledge_context', '')} "
            f"Rules:\n"
        )
        for rule in data.get('rules', []):
            prompt += f"- {rule}\n"
            
        return prompt
    except Exception as e:
        logger.error(f"Failed to load persona: {e}")
        return "You are a helpful AI assistant."

def build_context(user_text: str) -> list[dict]:
    """Build the full context array (system prompt + history + new user message)."""
    system_prompt = load_persona()
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_text})
    return messages

async def play_chunk(audio_bytes: bytes, device_index: int | None):
    """Play a single audio chunk on the output device."""
    try:
        await play_audio(audio_bytes, device_index)
    except Exception as e:
        logger.error(f"Error during audio playback: {e}")

async def process_text_input(text: str) -> str:
    """
    Process a single text input through the streaming pipeline.
    Streams LLM response sentence-by-sentence, converting each to TTS
    and playing audio as soon as the first sentence is ready.
    """
    global conversation_history, last_response_time, is_playing_audio
    
    # Build context
    messages = build_context(text)
    
    # Broadcast thinking state
    await manager.broadcast_state("thinking")
    
    device_idx = os.getenv("OUTPUT_DEVICE_INDEX")
    device_index = int(device_idx) if device_idx else None
    
    full_response = ""
    first_chunk = True
    
    try:
        async for sentence in chat_completion_stream(messages):
            if sentence.startswith("Error:"):
                full_response = sentence
                await manager.broadcast_state("idle")
                return full_response
            
            full_response += sentence + " "
            
            # Generate TTS for this sentence
            audio_bytes = await text_to_speech(sentence)
            if audio_bytes:
                if first_chunk:
                    # First sentence ready — switch to talking state
                    is_playing_audio = True
                    await manager.broadcast_state("talking")
                    first_chunk = False
                
                # Play this chunk (blocking until done, then next chunk plays)
                await play_chunk(audio_bytes, device_index)
    except Exception as e:
        logger.error(f"Error in streaming pipeline: {e}")
        full_response = f"Error: {e}"
    finally:
        last_response_time = time.time()
        is_playing_audio = False
        await manager.broadcast_state("idle")
    
    full_response = full_response.strip()
    
    # Append to history if it's not an error response
    if full_response and not full_response.startswith("Error:"):
        conversation_history.append({"role": "user", "content": text})
        conversation_history.append({"role": "assistant", "content": full_response})
    
        # Prune history if it exceeds max size
        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history = conversation_history[-(MAX_HISTORY * 2):]
        
    return full_response

async def process_queue_loop():
    """Background task to process queued transcripts while respecting cooldown."""
    global last_response_time, trigger_queue, is_playing_audio
    
    while True:
        try:
            if not trigger_queue:
                await asyncio.sleep(0.5)
                continue
                
            if is_playing_audio:
                await asyncio.sleep(0.5)
                continue
                
            cooldown = float(os.getenv("AI_COOLDOWN_SECONDS", 8))
            time_since_last = time.time() - last_response_time
            if time_since_last < cooldown:
                # Wait for remainder of cooldown
                await asyncio.sleep(cooldown - time_since_last)
                continue
                
            # Cooldown passed, not playing audio, and queue has items
            text = trigger_queue.pop(0)
            logger.info(f"🚀 Processing queued transcript: {text} (Queue size: {len(trigger_queue)}/{MAX_QUEUE_SIZE})")
            
            await process_text_input(text)
            
            # Yield to event loop
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error in queue processing loop: {e}")
            await asyncio.sleep(1.0)

# Minimum thresholds for transcript filtering
MIN_WORD_COUNT = 3
MIN_CHAR_COUNT = 15

def strip_wake_word(text: str) -> str | None:
    """
    Check for wake word and strip it from the transcript.
    Returns the cleaned text if wake word found, None otherwise.
    """
    lower = text.lower().strip()
    
    # Sort wake words longest-first so "hey chuks" matches before "chuks"
    for word in sorted(WAKE_WORDS, key=len, reverse=True):
        if lower.startswith(word):
            remainder = text[len(word):].strip(", ").strip()
            return remainder if remainder else None
    
    return None

async def handle_mic_transcript(text: str) -> None:
    """Handle transcriptions coming from the background STT thread."""
    cleaned = text.strip()
    if not cleaned:
        return

    logger.info(f"🎙️ Heard: {cleaned}")

    # Wake word detection — only respond if Chuks is addressed
    result = strip_wake_word(cleaned)
    if result is None:
        logger.info(f"🔇 No wake word detected, ignoring: {cleaned}")
        return
    
    cleaned = result
    logger.info(f"🔊 Wake word detected! Message: {cleaned}")

    # Filter out short fragments and noise
    word_count = len(cleaned.split())
    if word_count < MIN_WORD_COUNT or len(cleaned) < MIN_CHAR_COUNT:
        logger.info(f"🚫 Filtered short transcript ({word_count} words, {len(cleaned)} chars): {cleaned}")
        return

    if len(trigger_queue) < MAX_QUEUE_SIZE:
        trigger_queue.append(cleaned)
        logger.info(f"⏱️ Queued transcript (Size: {len(trigger_queue)}/{MAX_QUEUE_SIZE})")
    else:
        logger.warning(f"⚠️ Queue is full ({MAX_QUEUE_SIZE}). Discarding transcript: {cleaned}")
