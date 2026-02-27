# Task 4: Dashboard / Monitor UI (FR-018)

## 🔧 Agent Setup (DO THIS FIRST)

### Workflow to Follow
> Load: `cat .agent/workflows/vibe-build.md` (or use `/vibe-build`)

### Prime Agent Context
> MANDATORY: Run `/vibe-primeAgent` first

### Required Skills
| Skill | Path | Why |
|-------|------|-----|
| frontend-design | `~/.gemini/antigravity/skills/frontend-design/SKILL.md` | Premium dashboard UI |
| ui-ux-pro-max | `~/.gemini/antigravity/skills/ui-ux-pro-max/SKILL.md` | Design system, colors, UX |

### Pre-read
> - `docs/Project_Requirements.md` — FR-018
> - `docs/Coding_Guidelines.md`
> - `src/orchestrator.py` — Queue state, conversation history
> - `src/ws.py` — WebSocket manager pattern

---

## Objective

Build a web-based dashboard that gives the streamer real-time visibility into Chuks' internal state: what's in the queue, recent conversation history, avatar state, memory stats, and system health.

## Dependencies
> ⚠️ **Requires Tasks 1, 2, 3 to be completed first** (dashboard shows data from all features).
> Can be started without them but will have placeholder sections.

## Scope

### Architecture
```
FastAPI ──► /dashboard (HTML/CSS/JS)
         ──► /ws/dashboard (WebSocket for real-time updates)
         ──► /api/status (REST endpoint for current state)
```

### Dashboard Sections

1. **System Status Bar** — Server uptime, Kokoro status, Groq API status, mic active
2. **Avatar Preview** — Live mirror of the OBS overlay showing current state
3. **Conversation Feed** — Scrolling list of recent user→assistant exchanges
4. **Queue Monitor** — Current queue contents, cooldown timer countdown
5. **Memory Panel** — Session count, pinned memories count, current session ID
6. **YouTube Chat Feed** — Recent chat messages and which ones Chuks responded to

### Design Requirements
- Dark theme matching the overlay aesthetic (cyan/purple/electric blue)
- Real-time updates via WebSocket (no polling)
- Responsive but optimized for desktop (streamer's second monitor)
- No framework — vanilla HTML/CSS/JS (same pattern as overlay)

### Files to Create/Modify
- **[NEW]** `dashboard/index.html` — Dashboard structure
- **[NEW]** `dashboard/styles.css` — Dark theme, grid layout, animations
- **[NEW]** `dashboard/dashboard.js` — WebSocket client, DOM updates
- **[NEW]** `src/dashboard_api.py` — REST + WebSocket endpoints for dashboard data
- **[MODIFY]** `src/main.py` — Mount dashboard, add WS endpoint, add status API
- **[MODIFY]** `src/orchestrator.py` — Broadcast queue state changes to dashboard WS
- **[MODIFY]** `src/ws.py` — Add separate ConnectionManager for dashboard clients

### Implementation Steps
- [ ] Design the dashboard layout (wireframe in markdown or mockup)
- [ ] Create `dashboard/` directory with HTML, CSS, JS
- [ ] Create `/api/status` endpoint returning JSON system state
- [ ] Create `/ws/dashboard` WebSocket for real-time pushes
- [ ] Wire orchestrator to push events (queue change, new message, state change)
- [ ] Style with premium dark theme
- [ ] Mount at `/dashboard` in FastAPI
- [ ] Test: open dashboard while talking to Chuks

### Success Criteria
- [ ] Dashboard loads at `http://localhost:8000/dashboard/`
- [ ] Real-time updates when speaking to Chuks
- [ ] Queue contents visible and update live
- [ ] Conversation history scrolls with new messages
- [ ] System status shows green/red indicators
- [ ] No regression on overlay or audio pipeline

### Gotchas
- Dashboard WS and overlay WS are separate — use different ConnectionManagers
- Don't broadcast sensitive info (API keys) through the dashboard WS
- Keep the dashboard lightweight — no React/Vue, just vanilla JS
- Dashboard updates should be throttled (max 2 pushes/sec) to avoid flooding
