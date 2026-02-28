import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.ws import dashboard_manager
from src import orchestrator
from src import db

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_system_status() -> Dict[str, Any]:
    """Return the current complete state of the system."""
    
    # Get memory stats safely
    pinned_memories = []
    if getattr(db, 'pool', None):
        try:
            pinned_memories = await db.get_pinned_memories()
        except Exception:
            pass
            
    return {
        "status": {
            "uptime_ok": True,
            "groq_api": True,
            "kokoro_api": True,
            "mic_active": True
        },
        "session": {
            "session_id": getattr(orchestrator, 'current_session_id', None),
            "pinned_count": len(pinned_memories)
        },
        "queue": {
            "size": len(orchestrator.trigger_queue),
            "max": getattr(orchestrator, 'MAX_QUEUE_SIZE', 5),
            "items": orchestrator.trigger_queue.copy()
        },
        "history": orchestrator.conversation_history.copy(),
        "avatar_state": getattr(orchestrator, '_last_avatar_state', 'idle')
    }

@router.get("/api/status")
async def status_endpoint() -> Dict[str, Any]:
    return await get_system_status()

@router.websocket("/ws/dashboard")
async def websocket_dashboard_endpoint(websocket: WebSocket):
    await dashboard_manager.connect(websocket)
    try:
        # Send initial state immediately upon connection
        initial_state = await get_system_status()
        await websocket.send_json({"type": "full_state", "data": initial_state})
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket)
