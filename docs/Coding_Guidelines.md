# Coding Guidelines — Chuks AI Stream Companion

## Language & Runtime
- **Python 3.11+** — All backend code
- **HTML/CSS/JS** — OBS overlay only (no framework, vanilla)
- **No Node.js** — Single-language stack

## Style
- Follow **PEP 8** for all Python code
- Use **type hints** on all function signatures
- Use `snake_case` for functions/variables, `PascalCase` for classes
- Max line length: 100 characters
- Use `f-strings` for string formatting

## Architecture
- **Single process** — FastAPI serves everything (API, WebSocket, static files)
- **Module pattern** — Each concern is one file: `llm.py`, `tts.py`, `stt.py`, `orchestrator.py`, `audio.py`
- **No classes unless necessary** — Prefer functions + module-level state for simplicity
- **Async where it matters** — `async def` for I/O-bound operations (API calls, WebSocket). Threads for blocking operations (mic capture, audio playback)

## File Rules
- **200-line max** per file. If approaching, split
- **No circular imports** — Clear dependency chain: `main.py` → `orchestrator.py` → `llm.py`, `tts.py`, `stt.py`
- **Config via .env** — All secrets, device indices, and tunable values. Never hardcode

## Error Handling
- Wrap all external API calls (Groq, Kokoro) in try/except with logging
- Never crash the main loop — log errors, skip the failed cycle, continue
- Use `logging` module, not `print()`

## Audio
- Use `sounddevice` for mic capture and playback
- All audio buffers are `numpy` arrays, sample rate 24000 (Kokoro default)
- Device indices configured via `.env`, discovered via `scripts/list_devices.py`

## OBS Overlay
- Transparent background (`background: transparent` in CSS)
- All animations via CSS keyframes — no JS animation libraries
- WebSocket reconnects automatically if connection drops
- Avatar states: `idle`, `thinking`, `talking`

## Testing
- Test each module in isolation first (terminal verification)
- No unit test framework required for MVP — manual verification via curl/terminal
- End-to-end test: 10-minute continuous run without crashes

## Git
- Commit after each phase is verified working
- Commit message format: `phase-N: description`
- Never commit `.env` or audio device secrets
