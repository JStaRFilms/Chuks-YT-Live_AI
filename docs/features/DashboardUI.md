# Feature: Dashboard UI

## Goal
Build a web-based dashboard that gives the streamer real-time visibility into Chuks' internal state. This includes the trigger queue, conversation history, memory stats, avatar state, and system health status. It must be a premium dark-themed UI built with vanilla HTML/CSS/JS, optimized for a secondary monitor without any heavy frameworks.

## Components (Client vs Server)

### Server (FastAPI)
- **`src/dashboard_api.py` (New):**
  - Contains a `/api/status` endpoint to return the current system state (history, queue, mem stats, system health).
  - Contains a `/ws/dashboard` WebSocket endpoint for real-time state pushes (events like `message_added`, `queue_updated`, `avatar_state_changed`, `memory_updated`).
- **`src/ws.py` (Modified):**
  - Extract the general logic or create a secondary `ConnectionManager` instance named `dashboard_manager` separate from the avatar overlay manager.
- **`src/main.py` (Modified):**
  - Mount the `dashboard/` directory as a static folder at `/dashboard`.
  - Include the routers/endpoints from `dashboard_api.py`.
- **`src/orchestrator.py` (Modified):**
  - Inject dashboard WebSocket broadcasts at key lifecycle events (when an item is added to the queue, when conversation history updates, when avatar state changes).

### Client (Web Dashboard)
- **`dashboard/index.html`:** The HTML structure dividing the layout into semantic sections (System Status, Avatar Preview, Queue Monitor, Conversation Feed, YouTube Chat, Memory Panel).
- **`dashboard/styles.css`:** Tailored dark theme using css variables for primary/secondary colors (cyan/purple/electric blue), CSS Grid/Flexbox for layout, and subtle CSS animations for data updates.
- **`dashboard/dashboard.js`:** Vanilla JavaScript to fetch the initial state from `/api/status`, establish the `/ws/dashboard` WebSocket connection, and mutate the DOM dynamically upon receiving broadcast events.

## Data Flow
1. **Initial Load:** 
   - User opens `http://localhost:8000/dashboard/`.
   - `dashboard.js` fetches `/api/status` and populates the UI with the initial state.
2. **Real-time Synchronisation:**
   - `dashboard.js` connects to `ws://localhost:8000/ws/dashboard`.
   - When the orchestrator processes new audio/chat:
     - `trigger_queue` changes -> Broadcast `queue_update` -> Dashboard updates Queue Monitor.
     - `chat_completion` runs -> Broadcast `conversation_update` -> Dashboard updates Conversation Feed.
     - `avatar_state` changes -> Broadcast `state_change` -> Dashboard updates Avatar Preview.
3. **Throttling:**
   - Instead of broadcasting on every tiny change, the server may batch updates or limit push frequency to avoid flooding the frontend.

## Database Schema
This feature is predominantly read-only regarding the database. 
It might query `src/db.py` to retrieve the current session's memory stats (e.g., total pinned memories, current session ID) but introduces no new tables or schemas.
