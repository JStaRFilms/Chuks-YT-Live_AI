import asyncio
import logging
import pytchat
import os

logger = logging.getLogger(__name__)

class ChatPoller:
    def __init__(self, video_id: str, handle_message_cb):
        self.video_id = video_id
        self.handle_message_cb = handle_message_cb
        self.chat = None
        self.is_running = False

    async def poll_loop(self):
        try:
            self.chat = pytchat.create(video_id=self.video_id)
            logger.info(f"Started YouTube chat poller for video ID: {self.video_id}")
            self.is_running = True

            while self.chat.is_alive() and self.is_running:
                for c in self.chat.get().sync_items():
                    message = c.message
                    author = c.author.name
                    
                    # Log all messages at debug level if needed
                    # logger.debug(f"[YT Chat] {author}: {message}")

                    # Filter for !ai or !chuks commands
                    lower_msg = message.lower().strip()
                    if lower_msg.startswith("!ai ") or lower_msg.startswith("!chuks "):
                        logger.info(f"🎯 YT Command triggered by {author}: {message}")
                        
                        # Strip the command prefix to get the actual query
                        query = message.split(" ", 1)[1] if " " in message else ""
                        if query.strip():
                            # Call the callback (orchestrator.handle_chat_message)
                            await self.handle_message_cb(author, query.strip())

                await asyncio.sleep(2) # Avoid aggressive polling

        except Exception as e:
            logger.error(f"Error in YouTube chat poller: {e}")
        finally:
            self.is_running = False
            logger.info("YouTube chat poller stopped.")

    def stop(self):
        self.is_running = False
        if self.chat:
            self.chat.terminate()

def start_chat_poller(video_id: str, handle_message_cb):
    """
    Helper function to instantiate and start the poller as an asyncio task.
    Returns the ChatPoller instance so it can be stopped later if needed.
    """
    poller = ChatPoller(video_id, handle_message_cb)
    loop = asyncio.get_running_loop()
    loop.create_task(poller.poll_loop())
    return poller
