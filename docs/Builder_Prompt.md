# Builder Prompt — Chuks AI Stream Companion

## Stack-Specific Instructions

This is a **Python-only** backend using **FastAPI**. The OBS overlay is vanilla HTML/CSS/JS served as static files by FastAPI.

### Key APIs
- **Groq SDK** (`groq` Python package) — for both LLM chat completions AND Whisper STT
- **Kokoro TTS** — local Docker container at `http://localhost:8880`, standard OpenAI-compatible `/v1/audio/speech` endpoint
- **sounddevice** — for mic capture and audio playback (NOT pyaudio)
- **WebSocket** — FastAPI native WebSocket for avatar state sync

### Critical Patterns
1. **Mic capture runs in a background thread** — not async. `sounddevice` is blocking.
2. **Groq API calls are async** — use `AsyncGroq` client
3. **Audio playback is blocking** — runs in a thread pool executor
4. **Whisper model rotation** — alternate between `whisper-large-v3` and `whisper-large-v3-turbo` on each request to double the effective rate limit
5. **Silence detection** — use RMS (root mean square) of audio buffer. Threshold ~0.01. Only send chunks that contain speech followed by silence.

### Audio Routing
- Mic audio → `sounddevice.InputStream` → buffer → Groq Whisper API
- TTS audio → `sounddevice.play()` on VB-Cable device index → OBS picks it up
- The builder MUST use `scripts/list_devices.py` to find device indices before testing audio

## MUS Priority Order

1. **FR-001**: Core LLM Chat Loop
2. **FR-002**: Persona System
3. **FR-003**: Kokoro TTS Integration
4. **FR-004**: Audio Routing (VB-Cable)
5. **FR-005**: Groq Whisper STT
6. **FR-006**: Whisper Model Rotation
7. **FR-007**: Silence Detection & Turn-Taking
8. **FR-012**: Conversation History (In-Memory)
9. **FR-008**: OBS Avatar Overlay
10. **FR-009**: WebSocket Avatar Sync
11. **FR-010**: Cooldown & Queue
12. **FR-011**: Startup Script

## Special Considerations

- **GTX 1650** — Not used for inference in MVP (all inference is via Groq API / Kokoro Docker CPU). Don't assume GPU availability.
- **VB-Cable must be installed** — The startup script should check for it and warn if missing
- **Kokoro Docker must be running** — The startup script should ping `localhost:8880` before launching
- **Groq rate limits** — 20 req/min per Whisper model. Model rotation doubles this. If still hit, increase chunk duration from 5s to 8s.
- **No database for MVP** — In-memory list for conversation history. DB comes in Future phase.
