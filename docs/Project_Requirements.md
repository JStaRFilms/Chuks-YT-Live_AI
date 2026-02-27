# Project Requirements Document

## Project Overview

**Name:** Chuks — AI Live Stream Companion
**Mission:** A real-time AI co-host that listens to your mic, thinks, and speaks back on your YouTube live streams — with an animated avatar in OBS.
**Tech Stack:** Python, FastAPI, Groq API (LLM + Whisper STT), Kokoro TTS (Docker), HTML/CSS/JS (OBS overlay), VB-Cable (audio routing)

## Functional Requirements

| FR ID | Description | User Story | Status |
| :--- | :--- | :--- | :--- |
| FR-001 | Core LLM Chat Loop | As a streamer, I want to send text to the AI and get personality-driven responses, so that Chuks can converse. | MUS |
| FR-002 | Persona System | As a streamer, I want to configure the AI's name, personality, and rules via a JSON file, so that Chuks feels unique. | MUS |
| FR-003 | Kokoro TTS Integration | As a streamer, I want the AI's text responses converted to natural speech, so that Chuks can speak aloud on stream. | MUS |
| FR-004 | Audio Routing (VB-Cable) | As a streamer, I want the AI's voice routed to OBS via a virtual audio cable, so that viewers hear Chuks. | MUS |
| FR-005 | Groq Whisper STT | As a streamer, I want my mic audio transcribed in real-time via Groq's Whisper API, so that Chuks can hear me. | MUS |
| FR-006 | Whisper Model Rotation | As a streamer, I want the system to alternate between whisper-large-v3 and whisper-large-v3-turbo, so that I avoid hitting rate limits on either model. | MUS |
| FR-007 | Silence Detection & Turn-Taking | As a streamer, I want the AI to detect when I stop talking before responding, so that Chuks doesn't interrupt me. | MUS |
| FR-008 | OBS Avatar Overlay | As a streamer, I want an animated SVG avatar in OBS that reacts when Chuks is idle, thinking, or talking. | MUS |
| FR-009 | WebSocket Avatar Sync | As a streamer, I want the avatar state controlled via WebSocket from the orchestrator, so that animations sync with speech. | MUS |
| FR-010 | Cooldown & Queue | As a streamer, I want a cooldown period after Chuks speaks and a small trigger queue, so that responses don't pile up. | MUS |
| FR-011 | Startup Script | As a streamer, I want a single script to launch all services and verify dependencies, so that setup is fast. | MUS |
| FR-012 | Conversation History (In-Memory) | As a streamer, I want Chuks to remember the last 30 messages in the current session, so that conversation flows naturally. | MUS |
| FR-013 | PostgreSQL Persistent Memory | As a streamer, I want session transcripts and summaries saved to a database, so that Chuks remembers past streams. | Future |
| FR-014 | Memory Management CLI | As a streamer, I want CLI commands to list, clear, pin, and export memory, so that I control what Chuks remembers. | Future |
| FR-015 | YouTube Chat Integration | As a streamer, I want Chuks to read and respond to YouTube live chat messages and `!ai` commands. | Future |
| FR-016 | Stream Start Announcement | As a streamer, I want Chuks to auto-greet the stream when it starts. | Future |
| FR-017 | Hotkey Manual Trigger | As a streamer, I want to press a hotkey to force Chuks to respond, bypassing normal trigger logic. | Future |
| FR-018 | Dashboard / Monitor UI | As a streamer, I want a web dashboard showing Chuks' thinking queue, recent responses, and status. | Future |
