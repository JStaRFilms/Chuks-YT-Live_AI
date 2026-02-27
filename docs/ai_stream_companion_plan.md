# AI Live Stream Companion
## Full System Build Plan — Agent-Ready Technical Specification v1.0

---

## 1. Project Overview

This system adds a live AI co-host to your YouTube streams. It listens to your microphone in real time, optionally reads your YouTube live chat, generates contextual responses using a fast LLM, converts those responses to speech using Kokoro TTS, and displays an animated avatar overlay in OBS via a browser source. A persistent memory layer lets the AI build context across multiple streams or start fresh for each session.

---

## 2. Full Technology Stack

| Component | Choice / Notes |
|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` (ultra low latency, ~200ms avg) |
| TTS | Kokoro — run locally via `kokoro-fastapi` Docker OR `kokoro-onnx` Python package |
| Speech-to-Text | Whisper — `faster-whisper` (local, your mic audio) |
| Audio Routing | VB-Cable (Windows) or BlackHole (Mac) — virtual audio cable into OBS |
| Avatar / Overlay | Browser Source in OBS — React/HTML + CSS animations, served locally |
| YouTube Chat | YouTube Data API v3 — live chat polling every 3–5 seconds |
| Backend Runtime | Node.js (Express) or Python (FastAPI) — your choice |
| Database (local) | PostgreSQL (local) — memory, sessions, chat logs |
| Database (prod) | Neon (serverless Postgres) — one line swap in `.env` |
| OBS Integration | OBS Browser Source pointed at `localhost:3000` |
| Config / Secrets | `.env` file — API keys, persona config, stream settings |
| Process Manager | PM2 or separate terminals per service in dev |

---

## 3. System Architecture

### 3.1 Data Flow

Three parallel input streams feed into a central orchestrator:

- Your Microphone → Whisper STT → Transcript buffer → **Orchestrator**
- YouTube Live Chat API → Chat poller → Message queue → **Orchestrator**
- Manual Trigger (hotkey / `!ai` command) → **Orchestrator**

The Orchestrator then:

1. Assembles context: system prompt + persona + memory summary + recent conversation history
2. Sends assembled context to Groq API (LLM)
3. Receives LLM text response
4. Sends text to Kokoro TTS → returns audio buffer
5. Plays audio through virtual cable into OBS stream audio
6. Simultaneously signals the browser source overlay to animate the avatar (talking state)
7. Saves the exchange to PostgreSQL for memory

### 3.2 Services / Processes

**Service 1 — whisper-listener**
- Continuously captures mic audio in chunks (e.g. 5-second rolling window)
- Transcribes with faster-whisper
- Emits transcript events via WebSocket or shared message queue

**Service 2 — orchestrator**
- Core brain. Subscribes to transcript events and chat messages
- Applies turn-taking logic (see Section 6)
- Calls Groq, calls Kokoro, plays audio, signals avatar

**Service 3 — kokoro-tts-server**
- Runs `kokoro-fastapi` Docker image or the Python package as a local API
- Accepts text, returns audio stream
- Lives at `http://localhost:8880` by default

**Service 4 — overlay-server**
- Serves the HTML/React avatar page at `http://localhost:3000`
- Exposes a WebSocket endpoint the orchestrator pings to control avatar state

**Service 5 — youtube-chat-poller**
- Polls YouTube Live Chat API every 3–5 seconds
- Filters messages and pushes them to the orchestrator queue

---

## 4. Recommended Project Structure

```
ai-stream-companion/
├── services/
│   ├── orchestrator/        # Core brain — handles all coordination
│   │   ├── index.js
│   │   ├── llm.js           # Groq API wrapper
│   │   ├── tts.js           # Kokoro TTS wrapper
│   │   ├── memory.js        # DB read/write
│   │   ├── context.js       # Assembles prompts + history
│   │   └── avatar.js        # WebSocket signals to overlay
│   ├── whisper-listener/    # Mic capture + STT
│   │   ├── listener.py
│   │   └── requirements.txt
│   ├── youtube-chat/        # YT chat polling
│   │   ├── poller.js
│   │   └── auth.js          # OAuth2 flow for YT API
│   └── overlay/             # OBS browser source
│       ├── index.html
│       ├── avatar.js        # Animation state machine
│       └── styles.css
├── db/
│   ├── schema.sql           # Postgres schema
│   └── migrations/
├── scripts/
│   ├── start-stream.sh      # Start all services
│   └── manage-memory.js     # CLI: view/clear/export memory
├── config/
│   └── persona.json         # AI name, personality, context
├── .env
└── docker-compose.yml       # Kokoro + (optional) Postgres
```

---

## 5. Database Schema (PostgreSQL)

### sessions
```sql
id            SERIAL PRIMARY KEY
stream_title  TEXT
started_at    TIMESTAMP DEFAULT NOW()
ended_at      TIMESTAMP
summary       TEXT        -- LLM-generated summary at end of session
carry_forward BOOLEAN DEFAULT true  -- include in next session context?
```

### messages
```sql
id          SERIAL PRIMARY KEY
session_id  INTEGER REFERENCES sessions(id)
role        TEXT  -- 'user_mic', 'youtube_chat', 'ai', 'system'
speaker     TEXT  -- e.g. 'You', 'ChatUser123', 'AI Name'
content     TEXT
created_at  TIMESTAMP DEFAULT NOW()
```

### long_term_memory
```sql
id          SERIAL PRIMARY KEY
key         TEXT UNIQUE  -- e.g. 'recurring_topic', 'viewer_name'
value       TEXT
updated_at  TIMESTAMP DEFAULT NOW()
```

---

## 6. Turn-Taking & Trigger Logic

This is the most important design decision — without it the AI will interrupt constantly or never speak. Recommended approach: layered triggers.

### Priority 1 — Direct Commands (Always triggers)
- You say "Hey [AI Name]" or a configurable wake phrase (detected in transcript)
- A viewer types `!ai [question]` in YouTube chat
- You press a configurable hotkey (sends manual trigger to orchestrator)

### Priority 2 — Question Detection (High confidence triggers)
- Whisper transcript ends with a question mark AND silence > 1.5 seconds
- A question is addressed to the AI by name

### Priority 3 — Passive Commentary (Throttled, off by default)
- AI may optionally interject at most once every N minutes (configurable)
- Triggered only when transcript activity is low (you stopped talking)

### Cooldown
- After the AI speaks, enforce a mandatory cooldown (default: 15 seconds) where no new AI response can start
- Queue up to 2 pending triggers during cooldown; discard the rest

---

## 7. Memory Management System

### 7.1 Session Memory (Short-term)
During a stream, the last N messages (default: 30) are kept in a rolling buffer and injected as conversation history into every LLM prompt. This gives the AI awareness of what was just said.

### 7.2 Session Summary (End-of-Stream)
When you stop the stream (or run the stop script), the orchestrator automatically sends the full session transcript to the LLM and asks it to produce a ~300-word summary of key topics, memorable moments, and viewer names. This summary is saved to the `sessions` table.

### 7.3 Long-term Memory (Cross-stream)
At the start of each stream, the system fetches: the last 3 session summaries where `carry_forward = true`, and any `long_term_memory` key-value pairs. These are injected into the system prompt so the AI feels like it remembers past streams.

### 7.4 Memory Management CLI
```bash
node scripts/manage-memory.js list        # View all sessions and summaries
node scripts/manage-memory.js clear       # Wipe all session history
node scripts/manage-memory.js keep 3      # Keep only last 3 sessions
node scripts/manage-memory.js pin 'fact'  # Add to long_term_memory
node scripts/manage-memory.js export      # Export transcript as .txt
```

---

## 8. Persona Configuration

The AI persona lives in `config/persona.json` and is injected as the system prompt:

```json
{
  "name": "Nova",
  "personality": "Witty, curious, speaks casually. Loves tech and gaming.",
  "speaking_style": "Short punchy sentences. Max 2-3 sentences per response.",
  "knowledge_context": "You co-host a tech/gaming stream. The host is [Your Name].",
  "rules": [
    "Never claim to be human.",
    "Do not repeat what the host just said.",
    "If unsure, say so — don't hallucinate facts.",
    "Keep responses under 40 words unless specifically asked to elaborate."
  ]
}
```

---

## 9. Kokoro TTS Setup

### Option A — Docker (Recommended)
```bash
docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```
Call it from the orchestrator with a POST to `/v1/audio/speech`, passing text and voice ID. Returns an audio buffer you play immediately.

### Option B — Python Package (Lighter)
```bash
pip install kokoro-onnx sounddevice
```
Run as a small FastAPI wrapper script alongside your other services. Slightly more setup but no Docker needed.

### Audio Routing
- **Windows:** Install VB-Cable. Set Kokoro output device to VB-Cable Input. Set OBS audio source to VB-Cable Output.
- **Mac:** Install BlackHole. Same routing logic.
- The AI voice will now appear in your stream audio automatically when it speaks.

---

## 10. OBS Overlay & Avatar

### Setup
In OBS, add a Browser Source. Set URL to `http://localhost:3000`. Set size to match your canvas (e.g. 1920x1080). Enable "Refresh browser when scene becomes active".

### Avatar States
The avatar has four states controlled by WebSocket messages from the orchestrator:

- `idle` — subtle breathing or floating animation
- `thinking` — loading/processing visual indicator (between LLM call and audio start)
- `talking` — mouth/body animates in sync with audio playing
- `reacting` — quick expression change for specific triggers (laugh, surprise)

### Implementation Options (pick one)
- **CSS sprites** — cheapest to build, 2D PNG frames that swap on state change
- **Rive animation** — web-based, interactive, export from Rive editor, free tier available
- **PNGtuber style** — use veadotube mini as a separate overlay layer (easiest visually)
- **Live2D model** — most expressive, steeper learning curve, free models on Booth.pm

> **Recommendation:** Start with a CSS sprite or Rive for speed. You can upgrade to Live2D later without changing any other part of the system.

---

## 11. YouTube Live Chat Integration

1. Go to Google Cloud Console → create project → enable YouTube Data API v3
2. Create OAuth 2.0 credentials (Desktop App type)
3. Run auth flow once to get refresh token — save to `.env`
4. Poller fetches the active `liveChatId` from your broadcast, then polls `liveChatMessages` every 3–5 seconds

The poller filters out: bot messages, your own messages (by channel ID), messages that are just emojis, and messages shorter than 5 characters. Filtered messages go into the orchestrator queue tagged with the viewer's display name.

---

## 12. Environment Variables (.env)

```env
# LLM
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile

# TTS
KOKORO_BASE_URL=http://localhost:8880
KOKORO_VOICE=af_heart              # or any Kokoro voice ID

# Database
DATABASE_URL=postgresql://localhost:5432/stream_ai
# For prod: DATABASE_URL=postgresql://neon-connection-string

# YouTube
YOUTUBE_CLIENT_ID=...
YOUTUBE_CLIENT_SECRET=...
YOUTUBE_REFRESH_TOKEN=...
YOUTUBE_CHANNEL_ID=...

# Overlay
OVERLAY_PORT=3000
OVERLAY_WS_PORT=3001

# Whisper
WHISPER_MODEL=base.en               # or small.en for better accuracy
MIC_DEVICE_INDEX=0                  # run list_mics.py to find yours

# Behavior
AI_COOLDOWN_SECONDS=15
CHAT_POLL_INTERVAL_MS=4000
MAX_HISTORY_MESSAGES=30
PERSONA_FILE=./config/persona.json
```

---

## 13. Phased Build Plan

Build in this exact order. Each phase is independently testable before moving on.

### Phase 1 — Core LLM Loop (Day 1)
- Set up Groq API key, test a basic chat completion call in isolation
- Build the orchestrator skeleton — accepts text input, returns LLM text output
- Implement context assembly: system prompt from `persona.json` + message history array
- Test in terminal: type a message, get AI response back

> **Exit criteria:** You can have a text-based conversation with the AI in your terminal.

### Phase 2 — Kokoro TTS (Day 1–2)
- Get Kokoro running via Docker or Python package
- Build `tts.js` wrapper: accepts text string, returns audio buffer
- Play audio buffer through speakers
- Wire TTS into orchestrator: LLM response → TTS → audio playback

> **Exit criteria:** You type something, the AI speaks it out loud.

### Phase 3 — Whisper Mic Listener (Day 2)
- Build `whisper-listener.py`: captures mic audio in 4-second chunks, transcribes, emits text
- Connect listener to orchestrator via local HTTP POST or WebSocket
- Implement basic turn detection: minimum silence threshold before sending
- Add wake phrase detection

> **Exit criteria:** You say something into your mic, the AI responds out loud.

### Phase 4 — PostgreSQL Memory (Day 2–3)
- Set up local Postgres, run `schema.sql`
- Implement session creation on startup
- Wire message logging: every exchange saved to `messages` table
- Implement session summary generation at shutdown
- Implement context injection: load last 3 session summaries into system prompt
- Build `manage-memory.js` CLI

> **Exit criteria:** The AI remembers things from your last stream.

### Phase 5 — OBS Overlay (Day 3)
- Build static HTML avatar page with CSS idle animation
- Add WebSocket server to overlay
- Add WebSocket client logic: receives state messages and switches CSS class
- Wire orchestrator to send `talking`/`idle` signals
- Add VB-Cable audio routing — test that AI voice appears in OBS
- Add Browser Source in OBS pointing to `localhost:3000`

> **Exit criteria:** Avatar animates in OBS when AI speaks. Audio goes through stream.

### Phase 6 — YouTube Chat (Day 4)
- Complete Google OAuth flow, store refresh token in `.env`
- Build chat poller: fetch `liveChatId`, poll messages, filter and forward
- Add `!ai` command handler
- Test full loop: viewer types `!ai [question]` → AI responds on stream

> **Exit criteria:** Viewers can interact with your AI co-host from chat.

### Phase 7 — Polish & Hardening (Day 4–5)
- Add cooldown logic and queue management
- Add error handling and graceful restarts for each service
- Improve avatar — upgrade to Rive or PNGtuber if desired
- Add stream startup script that prompts: keep memory / start fresh?
- Load test: run for 30 minutes straight, watch for memory leaks or crash loops
- Optional: add a simple web dashboard to monitor AI activity during stream

---

## 14. Production / Hosted Deployment (Optional)

If you want to run this on a server instead of your local PC:

- Swap local Postgres for **Neon** — just change `DATABASE_URL` in `.env`
- Deploy orchestrator + overlay server to Railway, Render, or a small VPS
- Keep Whisper running **locally** on your PC (it needs your mic)
- Keep Kokoro running **locally** OR use a cloud TTS fallback (ElevenLabs API)
- Kokoro can run on a GPU VPS for lower latency if needed

> **Note:** Latency-sensitive parts (mic capture, audio playback, avatar) must stay local. Only the LLM orchestration and DB can move to cloud without impacting feel.

---

## 15. Additional Features Worth Adding

- **Stream start announcement** — AI greets the stream with a line generated from your persona
- **Viewer shoutout** — when someone subscribes or donates, AI gives a personalized shoutout
- **Mood detection** — Whisper can detect tone; feed this to LLM for emotionally-aware responses
- **Multiple voices** — swap Kokoro voice mid-stream for different AI characters/guests
- **Transcript export** — auto-save full stream transcript as `.txt` after each stream
- **AI silence mode** — hotkey to temporarily mute the AI without stopping services
- **Dashboard** — simple localhost web UI to see what the AI is thinking, queue status, memory
- **Custom chat commands** — `!topic`, `!forget`, `!remind` — let viewers influence the AI's context

---

## 16. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| AI talks over you constantly | High if no turn logic | Strict cooldown + wake phrase only mode |
| Whisper latency too high | Medium | Use faster-whisper with `base.en`; or `tiny.en` |
| Kokoro voice sounds robotic | Low — Kokoro is good | Tune via voice ID selection; test all available voices |
| Viewers troll or jailbreak AI | High on public streams | Strict system prompt rules; filter chat keywords |
| Groq rate limits | Low on free tier for this use | Add retry logic with exponential backoff |
| Audio feedback loop | Medium | Route AI audio to virtual cable only, not your speakers |
| YouTube API quota | Low — polling is cheap | Cache `liveChatId`; only poll when live |

---

*Feed this document to your agent as the canonical spec. Build Phase 1 first, validate, then proceed sequentially.*
