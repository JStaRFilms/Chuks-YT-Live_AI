import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Load env vars before importing other modules that might use them
load_dotenv()

from src.orchestrator import process_text_input, load_persona

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Chuks AI Stream Companion")

class ChatRequest(BaseModel):
    text: str

class ChatResponse(BaseModel):
    response: str

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Chuks AI Stream Companion...")
    # Verify persona loads correctly
    persona = load_persona()
    logger.info(f"Loaded persona. System prompt preview: {persona[:100]}...")

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
