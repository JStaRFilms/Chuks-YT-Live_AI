# 🎯 Task: Phase 4 — OBS Avatar Overlay

**Objective:** Build an animated SVG avatar that renders in OBS via Browser Source. It syncs with the orchestrator via WebSocket to show idle, thinking, and talking states.
**Priority:** Medium (enhances the stream but voice loop works without it)
**Scope:** FR-008 (OBS Avatar Overlay), FR-009 (WebSocket Avatar Sync)

---

## 🔧 Agent Setup (DO THIS FIRST)

### Prime Agent Context
> **MANDATORY:** Read these files before writing ANY code:
> 1. `docs/Project_Requirements.md` — Full PRD
> 2. `docs/Coding_Guidelines.md` — Overlay section specifically
> 3. `docs/Builder_Prompt.md` — Stack-specific patterns
> 4. `docs/issues/FR-008.md` — Detailed overlay specification

### Required Skills
> | Skill | Path | Why |
> |-------|------|-----|
> | frontend-design | `~/.gemini/antigravity/skills/frontend-design/SKILL.md` | For crafting a visually stunning, production-quality avatar design |
> | ui-ux-pro-max | `~/.gemini/antigravity/skills/ui-ux-pro-max/SKILL.md` | Color palettes, animation principles, premium feel |
> | webapp-testing | `~/.gemini/antigravity/skills/webapp-testing/SKILL.md` | Test the overlay in a browser to verify it renders correctly |

### Check Additional Skills
> Scan `~/.gemini/antigravity/skills/` for anything related to `css`, `animation`, `svg`, or `design`.

---

## 📋 Requirements

### Functional Requirements
- **[REQ-001]** HTML page at `overlay/index.html` with SVG avatar — transparent background
- **[REQ-002]** CSS animations at `overlay/styles.css` — 3 states: idle (breathing), thinking (pulsing), talking (energized)
- **[REQ-003]** WebSocket client at `overlay/avatar.js` — connects to `ws://localhost:8000/ws/avatar`, toggles CSS classes
- **[REQ-004]** FastAPI WebSocket endpoint at `/ws/avatar` in `src/main.py`
- **[REQ-005]** Orchestrator sends state messages at each pipeline stage
- **[REQ-006]** Static file serving — FastAPI mounts `overlay/` directory

### Design Requirements
- **[DESIGN-001]** The avatar should look premium and modern — NOT a basic circle
- **[DESIGN-002]** Use SVG with gradients, glow effects, and smooth animations
- **[DESIGN-003]** Think: a stylized AI entity — geometric shapes, neon accents, glass morphism
- **[DESIGN-004]** Color palette: dark theme with cyan/purple/electric blue accents
- **[DESIGN-005]** Animations should feel alive — subtle constant motion, not static when idle
- **[DESIGN-006]** Talking state should be visually dramatic — audience should clearly see when Chuks is speaking

---

## 🏗️ Implementation Plan

### Step 1: WebSocket Endpoint
- [x] Add to `src/main.py`:
  - `WebSocket` endpoint at `/ws/avatar`
  - Keep a set of connected WebSocket clients
  - `broadcast_avatar_state(state: str)` function
  - Mount `overlay/` as static files at `/overlay`

### Step 2: Orchestrator Integration
- [x] Update `src/orchestrator.py`:
  - Before LLM call → broadcast `{"state": "thinking"}`
  - When TTS audio starts playing → broadcast `{"state": "talking"}`
  - When audio finishes → broadcast `{"state": "idle"}`

### Step 3: SVG Avatar Design
- [x] Create `overlay/index.html`:
  - Full viewport, transparent background
  - Inline SVG avatar (geometric AI entity design)
  - Link to `styles.css` and `avatar.js`

### Step 4: CSS Animations
- [x] Create `overlay/styles.css`:
  - `body { background: transparent; }` (CRITICAL for OBS)
  - `.idle` — gentle floating/breathing animation
  - `.thinking` — pulsing glow effect, faster rhythm
  - `.talking` — energized animation, mouth/shape morphing, glow intensifies
  - Use `@keyframes` with `transform`, `opacity`, `filter` for smooth GPU-accelerated animations

### Step 5: WebSocket Client
- [x] Create `overlay/avatar.js`:
  - Connect to `ws://localhost:8000/ws/avatar`
  - On message: parse JSON, set `avatar.className = state`
  - Auto-reconnect on disconnect (retry every 2 seconds)
  - Default to `idle` state on connection

### Step 6: Verify
- [x] Open `http://localhost:8000/overlay/index.html` in Chrome
- [x] Verify transparent background (should show browser checker pattern)
- [x] Speak into mic → verify avatar transitions: idle → thinking → talking → idle
- [x] Add as OBS Browser Source — verify it composites correctly over your scene
- [x] Use the `webapp-testing` skill to capture a screenshot for visual review

---

## 📁 Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `overlay/index.html` | Create | Avatar page with SVG |
| `overlay/styles.css` | Create | State animations |
| `overlay/avatar.js` | Create | WebSocket client |
| `src/main.py` | Modify | Add WebSocket + static mount |
| `src/orchestrator.py` | Modify | Broadcast state changes |

---

## ✅ Success Criteria

- [x] Overlay renders with transparent background at `localhost:8000/overlay/index.html`
- [x] Avatar looks premium — not a basic placeholder shape
- [x] Idle animation runs continuously (subtle, alive feel)
- [x] Thinking state is visibly distinct from idle
- [x] Talking state is dramatic and clearly visible
- [x] State transitions are smooth (no harsh class-swap flashes)
- [x] WebSocket reconnects automatically on disconnect
- [x] Works in OBS Browser Source with transparent compositing
- [x] Code follows `docs/Coding_Guidelines.md`

---

## 🔗 Dependencies

**Depends on:** Phase 1 (needs FastAPI running), Phase 2+3 (needs orchestrator pipeline for state signals)
**Used by:** Nothing — this is the visual layer
