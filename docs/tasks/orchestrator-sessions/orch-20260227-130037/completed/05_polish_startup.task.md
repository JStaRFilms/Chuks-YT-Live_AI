# 🎯 Task: Phase 5 — Polish, Cooldown & Startup Script

**Objective:** Harden the system. Add cooldown logic, error recovery, and a startup script that verifies all dependencies before launching.
**Priority:** Medium (needed for a stable stream, but core loop works without it)
**Scope:** FR-010 (Cooldown & Queue), FR-011 (Startup Script)

---

## 🔧 Agent Setup (DO THIS FIRST)

### Prime Agent Context
> **MANDATORY:** Read these files before writing ANY code:
> 1. `docs/Project_Requirements.md` — Full PRD
> 2. `docs/Coding_Guidelines.md` — Error handling and logging rules
> 3. `docs/Builder_Prompt.md` — Special considerations section
> 4. `docs/issues/FR-010.md` — Cooldown and startup spec

### Required Skills
> | Skill | Path | Why |
> |-------|------|-----|
> | webapp-testing | `~/.gemini/antigravity/skills/webapp-testing/SKILL.md` | Run the full system for 10 minutes and verify stability |

### Check Additional Skills
> Scan `~/.gemini/antigravity/skills/` for anything related to `testing`, `debugging`, or `reliability`.

---

## 📋 Requirements

### Functional Requirements
- **[REQ-001]** Cooldown timer — after Chuks speaks, block new triggers for N seconds (default: 15, via `.env`)
- **[REQ-002]** Trigger queue — max 2 pending triggers during cooldown, discard excess
- **[REQ-003]** Startup script at `scripts/start.py` — checks all dependencies, then launches
- **[REQ-004]** Proper `logging` module usage throughout — replace any `print()` statements
- **[REQ-005]** Graceful error recovery — retry failed API calls once, skip on persistent failure

### Startup Checks
- **[CHECK-001]** Ping Kokoro at `localhost:8880/v1/models` — warn if not reachable
- **[CHECK-002]** Verify `GROQ_API_KEY` is set in `.env`
- **[CHECK-003]** List audio devices, show selected mic + output indices
- **[CHECK-004]** Verify selected device indices are valid
- **[CHECK-005]** Print a clear status report before launching

---

## 🏗️ Implementation Plan

### Step 1: Cooldown Logic
- [x] Update `src/orchestrator.py`:
  - Add `last_response_time: float` tracker
  - Add `is_on_cooldown() -> bool` check
  - Add `trigger_queue: list` (max length 2)
  - Before processing: check cooldown. If on cooldown, queue the trigger or discard
  - After cooldown expires: process next queued trigger (if any)

### Step 2: Logging
- [x] Add `import logging` to all `src/*.py` files
- [x] Set up logging config in `src/main.py`: `logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")`
- [x] Replace all `print()` with appropriate `logger.info/warning/error` calls
- [x] Log key events: transcript received, LLM called, TTS called, audio playing, cooldown active, trigger queued

### Step 3: Error Recovery
- [x] Wrap Groq LLM calls in try/except — retry once on timeout, log and skip on failure
- [x] Wrap Kokoro TTS calls in try/except — log and skip (Chuks stays silent, no crash)
- [x] Wrap Groq Whisper calls in try/except — log and drop the audio chunk
- [x] Never let an exception crash the mic listener thread

### Step 4: Startup Script
- [x] Create `scripts/start.py`:
  - Check Kokoro connectivity (HTTP GET to `/v1/models`)
  - Check `.env` values exist
  - List audio devices, validate selected indices
  - Print status report
  - Launch uvicorn programmatically or via subprocess

### Step 5: End-to-End Stress Test
- [x] Run the full system for 10+ minutes continuously
- [x] Speak to Chuks multiple times, verify responses
- [x] Verify cooldown prevents rapid-fire responses
- [x] Verify queued triggers process after cooldown
- [x] Verify no crashes, no memory leaks, no orphaned threads
- [x] Check logs for clean operation

---

## 📁 Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/orchestrator.py` | Modify | Add cooldown + queue logic |
| `src/main.py` | Modify | Add logging config |
| `src/llm.py` | Modify | Add error handling + logging |
| `src/tts.py` | Modify | Add error handling + logging |
| `src/stt.py` | Modify | Add error handling + logging |
| `scripts/start.py` | Create | Dependency checker + launcher |
| `.env` | Modify | Add `AI_COOLDOWN_SECONDS=15` |

---

## ✅ Success Criteria

- [x] Cooldown prevents responses within 15 seconds of each other
- [x] Max 2 triggers queued during cooldown, excess silently discarded
- [x] Startup script reports clear status of all dependencies
- [x] All modules use `logging` module (no `print()`)
- [x] System survives 10+ minutes continuous operation
- [x] Groq API errors are caught, logged, and don't crash the system
- [x] Kokoro errors are caught, logged, and don't crash the system
- [x] System recovers from transient network failures
