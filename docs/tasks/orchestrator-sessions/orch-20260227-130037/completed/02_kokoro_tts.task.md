# 🎯 Task: Phase 2 — Kokoro TTS + Audio Routing

**Objective:** Make Chuks speak. Text goes in, voice comes out through VB-Cable into OBS.
**Priority:** High (core audio pipeline)
**Scope:** FR-003 (Kokoro TTS), FR-004 (Audio Routing via VB-Cable)

---

## 🔧 Agent Setup (DO THIS FIRST)

### Prime Agent Context
> **MANDATORY:** Read these files before writing ANY code:
> 1. `docs/Project_Requirements.md` — Full PRD
> 2. `docs/Coding_Guidelines.md` — Python style rules
> 3. `docs/Builder_Prompt.md` — Stack-specific patterns and gotchas
> 4. `docs/issues/FR-003.md` — Detailed TTS specification

### Required Skills
> | Skill | Path | Why |
> |-------|------|-----|
> | context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | Look up `sounddevice` and `httpx` docs for correct API usage |

### Check Additional Skills
> Scan `~/.gemini/antigravity/skills/` for anything related to `audio`, `python`, or `streaming`.

---

## 📋 Requirements

### Functional Requirements
- **[REQ-001]** TTS wrapper at `src/tts.py` — send text to Kokoro, receive audio bytes
- **[REQ-002]** Audio utility at `src/audio.py` — play audio buffer to a specific output device by index
- **[REQ-003]** Device lister at `scripts/list_devices.py` — print all input/output audio devices with indices
- **[REQ-004]** `.env` additions: `KOKORO_BASE_URL`, `KOKORO_VOICE`, `OUTPUT_DEVICE_INDEX`
- **[REQ-005]** Wire TTS into orchestrator: LLM response text → TTS → audio playback

### Technical Requirements
- **[TECH-001]** Use `httpx.AsyncClient` for Kokoro API calls (POST to `/v1/audio/speech`)
- **[TECH-002]** Request `pcm` format from Kokoro (`response_format: "pcm"`) — raw audio, no decoding needed
- **[TECH-003]** Use `sounddevice.play()` for audio output — this is BLOCKING, must run in `asyncio.to_thread()`
- **[TECH-004]** Sample rate: 24000 Hz (Kokoro default for PCM)
- **[TECH-005]** Audio data: convert raw PCM bytes to `numpy.float32` array before playback

---

## 🏗️ Implementation Plan

### Step 1: Device Discovery Script
- [ ] Create `scripts/list_devices.py` — prints `sounddevice.query_devices()` in a readable format
- [ ] Run it, note the VB-Cable output device index (or regular speakers for initial testing)

### Step 2: Audio Utility
- [ ] Create `src/audio.py` with:
  - `list_devices() -> list` — wraps `sounddevice.query_devices()`
  - `play_audio(audio_bytes: bytes, device_index: int, sample_rate: int = 24000)` — converts PCM bytes to numpy array, plays via `sd.play()`, waits until done

### Step 3: TTS Wrapper
- [ ] Create `src/tts.py` with:
  - `async def text_to_speech(text: str) -> bytes` — POST to Kokoro, return raw audio bytes
  - Handle errors: Kokoro down, timeout, empty response
  - Load `KOKORO_BASE_URL` and `KOKORO_VOICE` from env

### Step 4: Wire Into Orchestrator
- [ ] Update `src/orchestrator.py`:
  - After getting LLM response, call `text_to_speech(response_text)`
  - Play the returned audio via `play_audio()` in a thread
  - Return both the text response and a signal that audio is playing

### Step 5: Update Main App
- [ ] Update `src/main.py`:
  - Add `OUTPUT_DEVICE_INDEX` env loading
  - Ensure the `/chat` endpoint now also triggers TTS + audio playback

### Step 6: Verify
- [ ] Ensure Kokoro Docker is running: `docker ps` should show the container
- [ ] If not running: `docker run -d -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest`
- [ ] Test TTS in isolation: `curl -X POST http://localhost:8880/v1/audio/speech -H "Content-Type: application/json" -d "{\"input\": \"Hello, I am Chuks!\", \"voice\": \"af_heart\", \"response_format\": \"pcm\"}" --output test.pcm`
- [ ] Test full loop: POST to `/chat` → hear Chuks speak the response

---

## 📁 Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/list_devices.py` | Create | Audio device discovery |
| `src/audio.py` | Create | Audio playback utility |
| `src/tts.py` | Create | Kokoro TTS wrapper |
| `src/orchestrator.py` | Modify | Add TTS call after LLM |
| `src/main.py` | Modify | Add output device config |
| `.env` | Modify | Add Kokoro + audio vars |

---

## ✅ Success Criteria

- [x] `scripts/list_devices.py` lists all audio devices with indices ✅ Completed
- [x] TTS wrapper converts text to audio bytes via Kokoro ✅ Completed
- [x] Audio plays through the specified output device ✅ Completed
- [x] Full loop: type message → Chuks speaks the response aloud ✅ Completed
- [x] No crashes when Kokoro is slow or returns errors ✅ Completed
- [x] Code follows `docs/Coding_Guidelines.md` ✅ Completed

---

## 🔗 Dependencies

**Depends on:** Phase 1 (Core LLM Loop must work first)
**Used by:** Phase 3 (STT wires into this), Phase 4 (Overlay syncs with audio)
**External:** Kokoro Docker container must be running at `localhost:8880`
