# 🎯 Task: Phase 3 — Groq Whisper STT + Mic Capture

**Objective:** Make Chuks hear. Capture mic audio, transcribe via Groq Whisper API, feed to the orchestrator. This is the "magic moment" — speak and Chuks responds.
**Priority:** High (completes the voice-to-voice loop)
**Scope:** FR-005 (Groq Whisper STT), FR-006 (Model Rotation), FR-007 (Silence Detection)

---

## 🔧 Agent Setup (DO THIS FIRST)

### Prime Agent Context
> **MANDATORY:** Read these files before writing ANY code:
> 1. `docs/Project_Requirements.md` — Full PRD
> 2. `docs/Coding_Guidelines.md` — Python style rules
> 3. `docs/Builder_Prompt.md` — Stack-specific patterns (CRITICAL: read the audio section)
> 4. `docs/issues/FR-005.md` — Detailed STT specification with code patterns

### Required Skills
> | Skill | Path | Why |
> |-------|------|-----|
> | context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | Look up Groq Python SDK audio transcription API and `sounddevice` InputStream docs |

### Check Additional Skills
> Scan `~/.gemini/antigravity/skills/` for anything related to `audio`, `streaming`, or `realtime`.

---

## 📋 Requirements

### Functional Requirements
- **[REQ-001]** Mic capture via `sounddevice.InputStream` — continuous recording in a background thread
- **[REQ-002]** Silence detection — RMS-based threshold to identify speech vs. silence
- **[REQ-003]** Speech boundary detection — detect when speech ends (silence > 1.5 seconds after speech)
- **[REQ-004]** Groq Whisper transcription — send audio chunk to API, get text back
- **[REQ-005]** Model rotation — alternate `whisper-large-v3` and `whisper-large-v3-turbo` per request
- **[REQ-006]** Wire transcript to orchestrator — trigger LLM → TTS → audio pipeline

### Technical Requirements
- **[TECH-001]** Record at 16000 Hz, mono, int16 (Whisper's expected input format)
- **[TECH-002]** Encode audio as WAV in-memory using `io.BytesIO` + `wave` module before sending to Groq
- **[TECH-003]** Mic capture runs in a **thread** (not async) — `sounddevice` is blocking
- **[TECH-004]** Use `Groq()` sync client for transcription (called from thread), NOT `AsyncGroq`
- **[TECH-005]** Silence RMS threshold: ~0.01 (configurable, needs tuning per mic)
- **[TECH-006]** `.env` additions: `MIC_DEVICE_INDEX`, `SILENCE_THRESHOLD`, `SILENCE_DURATION`

---

## 🏗️ Implementation Plan

### Step 1: Mic Capture Module
- [ ] Create `src/stt.py` with a `MicListener` class or module containing:
  - `start_listening(callback)` — starts a background thread that captures mic audio
  - Audio buffer management — accumulate frames, detect speech boundaries
  - `stop_listening()` — clean shutdown

### Step 2: Silence Detection
- [ ] Implement `is_silent(audio_chunk: np.ndarray, threshold: float) -> bool`
- [ ] Track state: `WAITING_FOR_SPEECH` → `RECORDING_SPEECH` → `SPEECH_ENDED`
- [ ] When speech ends (silence > 1.5s after speech detected), extract the speech segment

### Step 3: Groq Whisper Wrapper
- [ ] `transcribe(audio_bytes: bytes) -> str` — sends WAV bytes to Groq API
- [ ] `get_next_model() -> str` — round-robins between the two Whisper models
- [ ] WAV encoding function: numpy array → WAV bytes in memory

### Step 4: Wire to Orchestrator
- [ ] Update `src/orchestrator.py`:
  - Add `handle_mic_transcript(text: str)` — receives transcript, triggers full pipeline
  - The STT callback calls this when a transcript is ready
- [ ] Update `src/main.py`:
  - Start mic listener on app startup (`@app.on_event("startup")`)
  - Stop mic listener on app shutdown

### Step 5: Verify
- [ ] Run `scripts/list_devices.py` to confirm mic device index
- [ ] Start the app, speak a clear sentence into the mic
- [ ] Verify transcript appears in logs
- [ ] Verify Chuks responds aloud via TTS
- [ ] Test with background noise — verify silence detection doesn't false-trigger
- [ ] Test model rotation — check logs show alternating model names

---

## 📁 Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/stt.py` | Create | Mic capture + silence detection + Whisper |
| `src/orchestrator.py` | Modify | Add `handle_mic_transcript` |
| `src/main.py` | Modify | Start/stop mic listener on app lifecycle |
| `.env` | Modify | Add `MIC_DEVICE_INDEX`, `SILENCE_THRESHOLD` |

---

## ✅ Success Criteria

- [ ] Mic captures audio from the correct device
- [ ] Silence detection correctly separates speech from quiet
- [ ] Groq Whisper returns accurate transcripts
- [ ] Model rotation alternates per request (check logs)
- [ ] Full voice loop: speak → transcribe → LLM → TTS → Chuks speaks back
- [ ] No crashes on extended silence or background noise
- [ ] System handles Groq rate limit errors gracefully (retry/skip)

---

## 🔗 Dependencies

**Depends on:** Phase 1 (LLM Loop) + Phase 2 (TTS + Audio)
**Used by:** Phase 4 (Overlay needs to know when orchestrator is processing)
**External:** Groq API key with Whisper access, working microphone

---

## ⚠️ Known Gotchas

1. **Mic device index = 0 might not be your mic.** Always run `list_devices.py` first.
2. **WAV encoding is required.** Groq won't accept raw PCM — must be a proper WAV file in memory.
3. **Thread safety** — The mic thread calls back into the async orchestrator. Use `asyncio.run_coroutine_threadsafe()` to bridge.
4. **Audio feedback loops** — If your speakers are near your mic, Chuks will hear herself and loop. Use headphones or ensure VB-Cable routing isolates output.
