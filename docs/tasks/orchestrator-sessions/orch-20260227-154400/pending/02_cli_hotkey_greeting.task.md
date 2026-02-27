# Task 2: Memory CLI + Hotkey Trigger + Stream Greeting (FR-014, FR-016, FR-017)

## 🔧 Agent Setup (DO THIS FIRST)

### Workflow to Follow
> Load: `cat .agent/workflows/mode-code.md` (or use `/mode-code`)

### Prime Agent Context
> MANDATORY: Run `/vibe-primeAgent` first

### Required Skills
| Skill | Path | Why |
|-------|------|-----|
| context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | Library docs if needed |

### Pre-read
> - `docs/Project_Requirements.md` — FR-014, FR-016, FR-017
> - `docs/Coding_Guidelines.md`
> - `src/db.py` — DB layer from Task 1 (MUST be completed first)
> - `src/memory.py` — Memory layer from Task 1
> - `src/orchestrator.py`

---

## Objective

Add three small features that enhance Chuks' usability: a CLI for managing memories, a hotkey to force-trigger Chuks, and an auto-greeting when the stream starts.

## Dependencies
> ⚠️ **Requires Task 1 (PostgreSQL Memory) to be completed first.**

## Scope

### Part A: Memory CLI (FR-014)

**[NEW]** `scripts/memory_cli.py` — Standalone CLI tool

Commands:
- `python scripts/memory_cli.py list` — Show last 5 sessions with summaries
- `python scripts/memory_cli.py show <session_id>` — Show all messages from a session
- `python scripts/memory_cli.py pin "Chuks loves Python"` — Pin a memory
- `python scripts/memory_cli.py pins` — List all pinned memories
- `python scripts/memory_cli.py unpin <id>` — Remove a pinned memory
- `python scripts/memory_cli.py clear` — Clear all non-pinned memories (with confirmation)
- `python scripts/memory_cli.py export <session_id>` — Export session as JSON

Implementation:
- [ ] Create `scripts/memory_cli.py` using `argparse`
- [ ] Import DB functions from `src/db.py`
- [ ] Each command maps to a DB query
- [ ] Pretty-print output with colors (use `rich` library if available, else plain text)

### Part B: Hotkey Trigger (FR-017)

**[MODIFY]** `src/main.py` or **[NEW]** `src/hotkey.py`

- Use the `keyboard` library (already in requirements or add it)
- Register a global hotkey (e.g., `F9`) that force-triggers Chuks to respond
- When pressed: inject a prompt like "The host just pressed the hotkey to get your attention. Say something interesting or comment on what's happening." into the queue
- Hotkey should bypass the wake word requirement

Implementation:
- [ ] Create `src/hotkey.py` with hotkey registration
- [ ] On keypress: inject a trigger message into `orchestrator.trigger_queue`
- [ ] Start hotkey listener in `main.py` startup
- [ ] Add `HOTKEY_TRIGGER` to `.env` (default: `f9`)

### Part C: Stream Start Greeting (FR-016)

**[MODIFY]** `src/orchestrator.py`

- On first startup, after mic listener is active, queue a greeting message
- Use a special system message like: "The stream just started. Greet the audience with enthusiasm and introduce yourself."
- Only trigger once per session (use a flag)

Implementation:
- [ ] Add `stream_greeting()` async function in `orchestrator.py`
- [ ] Call it from `main.py` startup after queue loop starts
- [ ] Add `ENABLE_STREAM_GREETING` to `.env` (default: `true`)

### Success Criteria
- [ ] CLI lists sessions and memories correctly
- [ ] Hotkey press triggers Chuks response without wake word
- [ ] Stream greeting fires once on startup
- [ ] No regression on wake word, echo suppression, or queue logic
