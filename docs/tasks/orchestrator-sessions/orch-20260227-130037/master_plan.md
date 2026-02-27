# Orchestrator Master Plan — Chuks AI Stream Companion

**Session ID:** `orch-20260227-130037`
**Created:** 2026-02-27T13:00:37+01:00
**Objective:** Build the MUS (Minimum Usable State) for Chuks, an AI live stream co-host.

---

## Skills Registry

| Skill | Path | Used By |
|-------|------|---------|
| context7 | `~/.gemini/antigravity/skills/context7/SKILL.md` | Tasks 01, 02, 03 — API docs lookup |
| ai-sdk | `~/.gemini/antigravity/skills/ai-sdk/SKILL.md` | Task 01 — LLM integration patterns |
| frontend-design | `~/.gemini/antigravity/skills/frontend-design/SKILL.md` | Task 04 — Avatar visual design |
| ui-ux-pro-max | `~/.gemini/antigravity/skills/ui-ux-pro-max/SKILL.md` | Task 04 — Color, animation, premium feel |
| webapp-testing | `~/.gemini/antigravity/skills/webapp-testing/SKILL.md` | Tasks 04, 05 — Browser + stability testing |

## Workflows Registry

| Workflow | Used By |
|----------|---------|
| `/vibe-genesis` | This session (project initialization) |
| `/vibe-primeAgent` | All tasks (loads coding guidelines + project context) |
| `/vibe-build` | Execution of tasks 01-05 |

---

## Task Table

| # | Task | File | Mode | Skills | Depends On | Status |
|---|------|------|------|--------|------------|--------|
| 01 | Core LLM Loop | `pending/01_core_llm_loop.task.md` | code | context7, ai-sdk | — | ⏳ Pending |
| 02 | Kokoro TTS | `pending/02_kokoro_tts.task.md` | code | context7 | Task 01 | ⏳ Pending |
| 03 | Whisper STT | `pending/03_whisper_stt.task.md` | code | context7 | Tasks 01, 02 | ⏳ Pending |
| 04 | OBS Overlay | `pending/04_obs_overlay.task.md` | code | frontend-design, ui-ux-pro-max, webapp-testing | Tasks 01, 02, 03 | ⏳ Pending |
| 05 | Polish & Startup | `pending/05_polish_startup.task.md` | code | webapp-testing | Tasks 01-04 | ⏳ Pending |

## Dependency Graph

```
01 Core LLM ──► 02 TTS ──► 03 STT ──► 04 Overlay ──► 05 Polish
                                  │
                                  └── THE MAGIC MOMENT
                                      (speak → Chuks responds)
```

**All tasks are sequential.** Each phase depends on the previous.

---

## Execution Instructions

For each task, the agent MUST:
1. Read the **Agent Setup** section at the top of the task file
2. Load the assigned skills by reading their `SKILL.md` files
3. Read `docs/Coding_Guidelines.md` and `docs/Builder_Prompt.md`
4. Execute the implementation steps in order
5. Run the verification steps before marking complete
6. Move the task file from `pending/` to `completed/` when done

---

## Progress Checklist

- [ ] Task 01 — Core LLM Loop
- [ ] Task 02 — Kokoro TTS
- [ ] Task 03 — Whisper STT
- [ ] Task 04 — OBS Overlay
- [ ] Task 05 — Polish & Startup
- [ ] End-to-end verification (10 min stability test)
