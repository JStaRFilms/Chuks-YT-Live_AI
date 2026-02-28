import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env vars before importing other modules that might use them
load_dotenv()

from src.db import init_db, close_db
from src.orchestrator import process_text_input, load_persona, handle_mic_transcript, setup_session, cleanup_session
import asyncio
from src.stt import MicListener
from src.ws import manager
# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Chuks AI Stream Companion")

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str

# Global listener instance
mic_listener = MicListener()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Chuks AI Stream Companion...")
    await init_db()
    await setup_session()
    # Verify persona loads correctly
    persona = load_persona()
    logger.info(f"Loaded persona. System prompt preview: {persona[:100]}...")
    
    # Start Mic Listener
    loop = asyncio.get_running_loop()
    mic_listener.start_listening(handle_mic_transcript, loop)
    
    # Start Background Queue Processor
    from src.orchestrator import process_queue_loop, stream_greeting, trigger_queue, MAX_QUEUE_SIZE
    from src.hotkey import register_hotkey

    loop.create_task(process_queue_loop())
    
    # Fire stream greeting
    await stream_greeting()
    
    # Register hotkey
    register_hotkey(trigger_queue, MAX_QUEUE_SIZE)


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Chuks AI Stream Companion...")
    await cleanup_session()
    await close_db()
    mic_listener.stop_listening()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    try:
        response_text = await process_text_input(request.text)
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.websocket("/ws/avatar")
async def websocket_avatar_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.mount("/overlay", StaticFiles(directory="overlay", html=True), name="overlay")
