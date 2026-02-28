import keyboard
import os
import logging

logger = logging.getLogger(__name__)

def register_hotkey(trigger_queue: list, max_queue_size: int):
    hotkey = os.getenv("HOTKEY_TRIGGER", "f9")
    
    def on_hotkey_pressed():
        logger.info(f"🔑 Hotkey {hotkey} pressed!")
        prompt = "The host just pressed the hotkey to get your attention. Say something interesting or comment on what's happening."
        
        if len(trigger_queue) < max_queue_size:
            trigger_queue.append(prompt)
            logger.info(f"⏱️ Queued hotkey trigger (Size: {len(trigger_queue)}/{max_queue_size})")
        else:
            logger.warning("⚠️ Queue full, dropping hotkey trigger")
            
    try:
        keyboard.add_hotkey(hotkey, on_hotkey_pressed)
        logger.info(f"Registered hotkey listener for: {hotkey}")
    except Exception as e:
        logger.error(f"Failed to register hotkey {hotkey}: {e}")
