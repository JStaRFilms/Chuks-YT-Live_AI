# Feature: Kokoro TTS + Audio Routing

## Goal
To convert text responses from the LLM into natural-sounding speech using the Kokoro TTS engine running locally in Docker, and play that audio out to a specific virtual audio cable (VB-Cable) index so it can be routed into OBS.

## Components
- **Server (FastAPI App):** 
  - `src/tts.py`: Wrapper for the Kokoro TTS API. Takes text, makes an async HTTP POST request to the local Kokoro endpoint, and returns raw PCM bytes.
  - `src/audio.py`: Audio playback utility. Takes raw PCM bytes, converts them to a numpy array, and plays them via `sounddevice.play()` in a background thread (to avoid blocking the asyncio event loop).
  - `scripts/list_devices.py`: A helper script run by the user to identify device indices.

## Data Flow
1. User provides input text via `/chat`.
2. `src/main.py` passes text to `src/orchestrator.py`.
3. `orchestrator.py` gets an AI response string from `src/llm.py`.
4. `orchestrator.py` passes the AI response string to `tts.py:text_to_speech()`.
5. `tts.py` requests `pcm` audio from Kokoro (at `localhost:8880`) and returns bytes.
6. `orchestrator.py` spawns a background thread running `audio.py:play_audio()` with the bytes and the configured device index.
7. `sounddevice` outputs the audio to the VB-Cable device.
8. `orchestrator.py` returns the text to `main.py` which responds to the user.

## Database Schema
*Not applicable for this feature. Operates fully in-memory and via external HTTP/audio interfaces.*
