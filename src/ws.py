from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Avatar WebSocket client connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("Avatar WebSocket client disconnected")

    async def broadcast_state(self, state: str):
        message = {"state": state}
        await self.broadcast_json(message)

    async def broadcast_json(self, data: dict):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                dead_connections.append(connection)
                
        # Cleanup broken connections
        for dead in dead_connections:
            self.disconnect(dead)

# Global singletons
manager = ConnectionManager() # For Avatar Overlay
dashboard_manager = ConnectionManager() # For Dashboard UI
