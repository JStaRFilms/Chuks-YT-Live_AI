<p align="center">
  <img src="overlay/chuks-avatar.svg" width="120" alt="Chuks Avatar" />
</p>

<h1 align="center">🎙️ Chuks — AI Live Stream Co-Host</h1>

<p align="center">
  <strong>A real-time AI companion that listens, thinks, and speaks on your live streams.</strong>
  <br/>
  Powered by Groq LLM • Kokoro TTS • Whisper STT • FastAPI
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq-LLM%20%2B%20Whisper-orange" />
  <img src="https://img.shields.io/badge/Kokoro-TTS-purple" />
  <img src="https://img.shields.io/badge/OBS-Ready-green?logo=obsstudio&logoColor=white" />
</p>

---

## What is Chuks?

Chuks is an AI co-host for YouTube live streams. He **listens** to your microphone, **thinks** using a Groq-hosted LLM, and **speaks back** through Kokoro text-to-speech — all with an animated avatar in OBS.

Say **"Hey Chuks, what do you think about Python?"** and he'll respond out loud with a witty take, while his avatar animates in your stream overlay.

### ✨ Features

- 🎤 **Real-time Speech-to-Text** — Groq Whisper with model rotation to dodge rate limits
- 🧠 **Streaming LLM** — Sentence-by-sentence responses (starts speaking while still thinking)
- 🔊 **Natural TTS** — 65+ voices via Kokoro (local Docker, zero API cost)
- 🎭 **OBS Avatar** — Animated SVG that syncs idle → thinking → talking states
- 🔇 **Wake Word** — Only responds when addressed ("Hey Chuks", "Yo Chuks")
- 🔁 **Echo Suppression** — Mic mutes during playback to prevent self-loops
- 📝 **Conversation Memory** — Remembers the last 30 messages per session
- ⚡ **Connection Pooling** — Singleton HTTP clients for minimal latency

---

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Your Mic   │────▶│  Whisper STT │────▶│ Wake Word    │
│ (sounddevice)│     │  (Groq API)  │     │   Filter     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  OBS Overlay │◀────│  Orchestrator│◀────│  Trigger     │
│  (WebSocket) │     │  (Queue +    │     │  Queue       │
└──────────────┘     │   Cooldown)  │     └──────────────┘
                     └──────┬───────┘
                            │
                   ┌────────┼────────┐
                   ▼                 ▼
            ┌──────────┐     ┌──────────────┐
            │ Groq LLM │     │  Kokoro TTS  │
            │(streaming)│────▶│  (sentence   │──▶ 🔊 Speakers
            └──────────┘     │   by sentence)│
                             └──────────────┘
```

---

## Quick Start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Runtime |
| Docker | Any | Kokoro TTS server |
| OBS Studio | 28+ | Stream overlay |
| Groq API Key | — | [Get one free](https://console.groq.com) |

### 1. Clone & Install

```bash
git clone https://github.com/JStaRFilms/Chuks-YT-Live_AI.git
cd Chuks-YT-Live_AI
pip install -r requirements.txt
```

### 2. Start Kokoro TTS (Docker)

```bash
docker run -d -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest
```

> 💡 Use `kokoro-fastapi-gpu` if you have an NVIDIA GPU for faster synthesis.

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=moonshotai/kimi-k2-instruct-0905

# TTS
KOKORO_BASE_URL=http://localhost:8880
KOKORO_VOICE=am_adam          # See voice list below
OUTPUT_DEVICE_INDEX=4         # Your speakers/headphones
MIC_DEVICE_INDEX=1            # Your microphone

# Tuning
AI_COOLDOWN_SECONDS=8         # Seconds between responses
SILENCE_DURATION=2.5          # Silence before processing speech
```

### 4. Find Your Audio Devices

```bash
python scripts/list_devices.py
```

Note the index numbers for your mic and output device.

### 5. Launch

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 6. Add to OBS

1. Add a **Browser Source** in OBS
2. URL: `http://localhost:8000/overlay/index.html`
3. Width: `300`, Height: `400`
4. Check "Shutdown source when not visible"

---

## Talking to Chuks

Chuks uses a **wake word** system — he only responds when addressed:

| Trigger | Example |
|---------|---------|
| `"Hey Chuks, ..."` | "Hey Chuks, what's the best programming language?" |
| `"Yo Chuks, ..."` | "Yo Chuks, tell me something interesting" |
| `"Chuks, ..."` | "Chuks, explain async await" |

Everything else is ignored — background noise, side conversations, coughs. 🔇

---

## Customizing Chuks

### Persona

Edit `config/persona.json` to change Chuks' personality:

```json
{
    "name": "Chuks",
    "personality": "Witty, curious, speaks casually. Loves tech and gaming.",
    "speaking_style": "Short punchy sentences. Max 2-3 sentences per response.",
    "knowledge_context": "You co-host a tech/coding live stream...",
    "rules": [
        "Never claim to be human.",
        "Keep responses under 40 words unless asked to elaborate."
    ]
}
```

### Voice

Set `KOKORO_VOICE` in `.env`. Popular choices:

| Voice | Style |
|-------|-------|
| `am_adam` | Deep, confident male |
| `am_puck` | Playful, energetic male |
| `am_eric` | Casual, friendly male |
| `af_heart` | Warm female (default) |
| `bf_emma` | British female |
| `bm_george` | British male |

> Full list: 65 voices across English, British, French, Hindi, Japanese, Spanish, Chinese. Query `GET /v1/audio/voices` on your Kokoro instance.

---

## Project Structure

```
├── src/
│   ├── main.py           # FastAPI app + lifecycle
│   ├── orchestrator.py    # Queue, context, streaming pipeline
│   ├── llm.py            # Groq LLM (streaming + non-streaming)
│   ├── tts.py            # Kokoro TTS client (connection pooled)
│   ├── stt.py            # Mic capture + Whisper transcription
│   ├── audio.py          # Audio playback via sounddevice
│   └── ws.py             # WebSocket manager for avatar state
├── overlay/
│   ├── index.html        # OBS browser source
│   ├── styles.css        # Avatar animations
│   └── chuks-avatar.svg  # SVG avatar
├── config/
│   └── persona.json      # Chuks' personality config
├── scripts/
│   ├── start.py          # Service launcher
│   └── list_devices.py   # Audio device scanner
└── requirements.txt
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send text, get response (triggers TTS) |
| `/ws/avatar` | WebSocket | Avatar state updates (`idle` / `thinking` / `talking`) |
| `/overlay/` | GET | OBS avatar overlay page |

### Example

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey Chuks, what do you think about AI?"}'
```

---

## Roadmap

- [x] Core LLM chat loop with persona
- [x] Kokoro TTS + audio playback
- [x] Groq Whisper STT with model rotation
- [x] OBS avatar overlay with WebSocket
- [x] Wake word detection
- [x] Streaming LLM → sentence-by-sentence TTS
- [x] Echo suppression + transcript filtering
- [ ] PostgreSQL persistent memory (cross-session)
- [ ] YouTube live chat integration (`!ai` commands)
- [ ] Hotkey manual trigger
- [ ] Stream start auto-greeting
- [ ] Real-time monitoring dashboard
- [ ] Memory management CLI

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Runtime | Python 3.11 |
| Web Framework | FastAPI + Uvicorn |
| LLM | Groq API (any model) |
| Speech-to-Text | Groq Whisper (v3 + v3-turbo rotation) |
| Text-to-Speech | Kokoro TTS (Docker, 65+ voices) |
| Audio I/O | sounddevice + numpy |
| OBS Integration | Browser Source + WebSocket |
| Real-time Comms | FastAPI WebSockets |

---

## License

MIT — do whatever you want with it.

---

<p align="center">
  Built with ❤️ and a lot of vibe coding by <a href="https://github.com/JStaRFilms">JStaR Films</a>
</p>
