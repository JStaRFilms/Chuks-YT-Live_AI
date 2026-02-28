# Task 1: PostgreSQL Persistent Memory (FR-013)

## 🔧 Agent Setup (DO THIS FIRST)

### Workflow to Follow
> Load: `cat .agent/workflows/mode-code.md` (or use `/mode-code`)

### Prime Agent Context
> MANDATORY: Run `/vibe-primeAgent` first

### Required Skills
| Skill | Path | Why |
|-------|------|-----|
| context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | Look up Neon Python SDK docs |

### Pre-read
> - `docs/Project_Requirements.md` — FR-013
> - `docs/Coding_Guidelines.md`
> - `docs/Builder_Prompt.md`
> - `src/orchestrator.py` — Current in-memory history implementation

---

## Objective

Add persistent memory to Chuks using Neon PostgreSQL so that session transcripts and summaries survive restarts and can be recalled across streams.

## Scope

### Database Schema
```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    summary TEXT
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    role VARCHAR(20) NOT NULL,  -- 'user' | 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE pinned_memories (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(50),  -- 'fact', 'preference', 'story'
    pinned_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Files to Create/Modify
- **[NEW]** `src/db.py` — Database connection pool (asyncpg), session CRUD, message CRUD
- **[NEW]** `src/memory.py` — Memory retrieval, session summarization (call LLM to summarize), pinned memories
- **[MODIFY]** `src/orchestrator.py` — On startup: create session. On each exchange: persist to DB. Inject last session summary into context.
- **[MODIFY]** `src/main.py` — Init DB pool on startup, close on shutdown
- **[MODIFY]** `.env` — Add `DATABASE_URL`
- **[MODIFY]** `requirements.txt` — Add `asyncpg`

### Implementation Steps
- [x] Add `asyncpg` to requirements
- [x] Create `src/db.py` with connection pool + CRUD functions
- [x] Create `src/memory.py` with get_last_session_summary, get_pinned_memories
- [x] Modify `orchestrator.py`: create session on startup, persist messages, load summary into context
- [x] Modify `main.py`: init/close DB pool
- [x] Add `DATABASE_URL` to `.env`
- [x] Test: restart server, verify messages persist

### Success Criteria
- [x] Messages survive server restart
- [x] New session starts with previous session's summary injected into context
- [x] Pinned memories are included in system prompt
- [x] No regression on existing MUS features

### Gotchas
- Use `asyncpg` not `psycopg2` — we're async everywhere
- Don't block the audio pipeline with DB writes — use `asyncio.create_task()` for fire-and-forget saves
- Session summary should be generated lazily (on shutdown or when context window is pruned)
