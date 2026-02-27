# 🎯 Task: Phase 1 — Core LLM Loop + Persona System

**Objective:** Build the foundational chat loop. User types text → Chuks responds with personality.
**Priority:** High (everything depends on this)
**Scope:** FR-001 (Core LLM Chat Loop), FR-002 (Persona System), FR-012 (In-Memory History)

---

## 🔧 Agent Setup (DO THIS FIRST)

### Prime Agent Context
> **MANDATORY:** Read these files before writing ANY code:
> 1. `docs/Project_Requirements.md` — Full PRD
> 2. `docs/Coding_Guidelines.md` — Python style rules
> 3. `docs/Builder_Prompt.md` — Stack-specific patterns and gotchas

### Required Skills
> | Skill | Path | Why |
> |-------|------|-----|
> | context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | Look up FastAPI and Groq SDK docs for correct API usage |
> | ai-sdk | `~/.gemini/antigravity/skills/ai-sdk/SKILL.md` | Reference for LLM integration patterns (even though we use Groq directly, patterns apply) |

### Check Additional Skills
> Scan `~/.gemini/antigravity/skills/` — look for anything related to `python`, `fastapi`, or `llm`.

---

## 📋 Requirements

### Functional Requirements
- **[REQ-001]** FastAPI app at `src/main.py` with POST `/chat` endpoint accepting `{"text": "..."}` and returning `{"response": "..."}`
- **[REQ-002]** Groq LLM wrapper at `src/llm.py` using `AsyncGroq` with `llama-3.3-70b-versatile`
- **[REQ-003]** Persona config at `config/persona.json` with Chuks' personality (name: "Chuks", witty tech co-host, short punchy responses, max 40 words)
- **[REQ-004]** Context assembler at `src/orchestrator.py` that builds: system prompt (from persona) + rolling history (last 30 messages) + user message
- **[REQ-005]** `.env` file with `GROQ_API_KEY` and `GROQ_MODEL` variables
- **[REQ-006]** `requirements.txt` with all dependencies

### Technical Requirements
- **[TECH-001]** Use `python-dotenv` for env loading
- **[TECH-002]** Use `async def` for all Groq API calls
- **[TECH-003]** Max 150 tokens per LLM response
- **[TECH-004]** Temperature 0.8 for creative but grounded responses
- **[TECH-005]** Rolling history maintained in-memory (simple list, no DB)

---

## 🏗️ Implementation Plan

### Step 1: Project Setup
- [ ] Create `requirements.txt`: `fastapi`, `uvicorn[standard]`, `groq`, `python-dotenv`, `httpx`, `sounddevice`, `numpy`, `scipy`
- [ ] Create `.env` with `GROQ_API_KEY`, `GROQ_MODEL=llama-3.3-70b-versatile`
- [ ] Run `pip install -r requirements.txt`

### Step 2: Persona Config
- [ ] Create `config/persona.json` with Chuks' full personality definition

### Step 3: LLM Wrapper
- [ ] Create `src/llm.py` with `async def chat_completion(messages: list[dict]) -> str`
- [ ] Load model from env, handle errors gracefully

### Step 4: Orchestrator
- [ ] Create `src/orchestrator.py` with:
  - `load_persona()` — reads `config/persona.json`, builds system prompt string
  - `build_context(user_text: str) -> list[dict]` — system prompt + history + user message
  - `process_text_input(text: str) -> str` — full pipeline: build context → call LLM → append to history → return response
  - In-memory `conversation_history: list[dict]` (rolling, max 30)

### Step 5: FastAPI App
- [ ] Create `src/main.py` with:
  - FastAPI app
  - POST `/chat` endpoint
  - Startup event that loads persona
  - Run with `uvicorn`

### Step 6: Verify
- [ ] Start the server: `python -m uvicorn src.main:app --reload`
- [ ] Test with: `curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d "{\"text\": \"Hey Chuks, what do you think about Python?\"}"`
- [ ] Verify Chuks responds in character (witty, concise, tech-savvy)
- [ ] Send 3-4 follow-up messages, verify history is maintained

---

## 📁 Files to Create

| File | Action | Purpose |
|------|--------|---------|
| `requirements.txt` | Create | Python dependencies |
| `.env` | Create | API keys and config |
| `config/persona.json` | Create | Chuks' personality |
| `src/llm.py` | Create | Groq LLM wrapper |
| `src/orchestrator.py` | Create | Core brain + context assembly |
| `src/main.py` | Create | FastAPI entry point |

---

## ✅ Success Criteria

- [ ] Server starts without errors
- [ ] POST `/chat` returns personality-appropriate response from Chuks
- [ ] Multiple messages maintain conversation context
- [ ] Response is under 40 words
- [ ] No hardcoded API keys (all from `.env`)
- [ ] Code follows `docs/Coding_Guidelines.md`

---

## 🔗 Dependencies

**Depends on:** Nothing (first phase)
**Used by:** Phase 2 (TTS), Phase 3 (STT), Phase 4 (Overlay)

---

## 🚀 Getting Started

1. Read the Agent Setup section above
2. Read `docs/issues/FR-001.md` for detailed specification
3. Look up Groq SDK docs via the `context7` skill
4. Begin with Step 1 (Project Setup)
5. Verify at the end with curl tests
