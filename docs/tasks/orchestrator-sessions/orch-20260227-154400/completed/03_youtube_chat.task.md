# Task 3: YouTube Chat Integration (FR-015)

## 🔧 Agent Setup (DO THIS FIRST)

### Workflow to Follow
> Load: `cat .agent/workflows/mode-code.md` (or use `/mode-code`)

### Prime Agent Context
> MANDATORY: Run `/vibe-primeAgent` first

### Required Skills
| Skill | Path | Why |
|-------|------|-----|
| context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | YouTube Data API / pytchat docs |

### Pre-read
> - `docs/Project_Requirements.md` — FR-015
> - `docs/Coding_Guidelines.md`
> - `src/orchestrator.py` — Queue and handle_mic_transcript pattern

---

## Objective

Enable Chuks to read and respond to YouTube live chat messages during a stream. Viewers can interact with the AI co-host directly from chat.

## Scope

### Architecture
```
YouTube Live Chat ──► Poller (pytchat) ──► Filter (!ai command) ──► Orchestrator Queue
```

### Library Choice
- **`pytchat`** — Lightweight YouTube live chat scraper. No OAuth needed, just the video URL/ID.
- Alternative: YouTube Data API v3 (requires API key + quota, overkill for MVP)

### Files to Create/Modify
- **[NEW]** `src/youtube_chat.py` — Chat poller service
  - Connect to live stream using video ID
  - Poll for new messages every 2-3 seconds
  - Filter: only process messages starting with `!ai` or `!chuks`
  - Strip the command prefix and queue the viewer's message
  - Include viewer's display name in the message context
- **[MODIFY]** `src/orchestrator.py` — Add `handle_chat_message(viewer_name, text)` function
  - Preface the text with "[YouTube Chat] {viewer_name} asks: {text}"
  - Feed into the same queue as mic transcripts
  - Respect the same cooldown and queue limits
- **[MODIFY]** `src/main.py` — Start YouTube chat poller on startup (if VIDEO_ID is set)
- **[MODIFY]** `.env` — Add `YOUTUBE_VIDEO_ID` (optional, empty = disabled)
- **[MODIFY]** `requirements.txt` — Add `pytchat`

### Implementation Steps
- [x] Add `pytchat` to requirements
- [x] Create `src/youtube_chat.py` with `ChatPoller` class
- [x] Implement message filtering (`!ai` or `!chuks` prefix)
- [x] Add `handle_chat_message()` to orchestrator
- [x] Wire into `main.py` startup (only if VIDEO_ID is provided)
- [ ] Test with a live or unlisted YouTube stream

### Chat Command Design
| Command | Behavior |
|---------|----------|
| `!ai What's your favorite language?` | Chuks responds to the question |
| `!chuks Tell me a joke` | Same as !ai |
| Regular chat message | Ignored (not every chat message should trigger) |

### Success Criteria
- [ ] Chat messages with `!ai` prefix are queued and answered
- [ ] Viewer name is included in the prompt context
- [ ] Regular chat messages are ignored
- [ ] System works without YouTube (graceful disable when VIDEO_ID is empty)
- [ ] No regression on mic-based conversation

### Gotchas
- `pytchat` can break if YouTube changes their chat API — have graceful error handling
- Rate limit chat polling to avoid hammering YouTube
- Chat responses should probably be longer than mic responses (viewers wait longer) — consider a separate max_tokens config
- Don't let chat flood the queue — maybe a separate smaller queue or lower priority
