# YouTube Chat Integration (FR-015)

## Goal
Enable Chuks to read and respond to YouTube live chat messages during a stream. Viewers can interact with the AI co-host directly from the chat by prefixing messages with `!ai` or `!chuks`.

## Components
- **Chat Poller (`src/youtube_chat.py`)**: Runs as a background task. Connects to the YouTube live stream using `pytchat` and the given `YOUTUBE_VIDEO_ID`. Polls for new messages, filters them, and enqueues valid commands.
- **Orchestrator (`src/orchestrator.py`)**: The central hub that exposes a function to handle incoming chat messages and places them into the existing `trigger_queue`.
- **Main App (`src/main.py`)**: Reads `YOUTUBE_VIDEO_ID` from the environment on startup and kicks off the chat poller.

## Data Flow
1. **Initialize**: App starts. `main.py` checks for `YOUTUBE_VIDEO_ID`.
2. **Poll**: `ChatPoller` in `src/youtube_chat.py` polls YouTube for chat messages every few seconds using `pytchat`.
3. **Filter**: `ChatPoller` ignores messages not starting with `!ai` or `!chuks` (case-insensitive).
4. **Queue**: Valid messages are handled via `handle_chat_message` from `orchestrator.py`. The text is prepended with `[YouTube Chat] {viewer_name} asks: {text}` and queued.
5. **Process**: Orchestrator's `process_queue_loop` processes the queued message, queries the LLM, and triggers TTS output.
6. **Graceful Degradation**: If `YOUTUBE_VIDEO_ID` is absent or connection fails, the app continues normal operation (mic + WS).

## Database Schema
No database changes are required. The AI responses to chat inputs will flow through the existing logging/memory mechanisms in `process_text_input`.

## Implementation Steps
1. Add `pytchat` to `requirements.txt`.
2. Add `YOUTUBE_VIDEO_ID=` to `.env.example`.
3. Create `src/youtube_chat.py` and implement the `start_chat_poller(video_id)` function.
4. Modify `src/orchestrator.py` to add `handle_chat_message(viewer_name, text)`.
5. Modify `src/main.py` to invoke `start_chat_poller` during startup if configured.
6. Verify functionality.
