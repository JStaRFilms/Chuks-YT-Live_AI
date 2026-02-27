# Post-MUS Orchestrator Master Plan

**Session:** `orch-20260227-154400`
**Scope:** FR-013 through FR-018 (6 Future Features)

## Skills Registry

| Skill | Tasks | Why |
|-------|-------|-----|
| `ai-sdk` | T4 (Dashboard) | If using Next.js for dashboard |
| `frontend-design` | T4 (Dashboard) | Premium dashboard UI |
| `ui-ux-pro-max` | T4 (Dashboard) | Design system, colors, typography |
| `context7` | T1 (Neon DB), T3 (YouTube API) | Library docs lookup |

## Workflows Registry

| Workflow | Tasks |
|----------|-------|
| `/vibe-primeAgent` | ALL tasks |
| `/mode-code` | T1, T2, T3, T4 |
| `/vibe-build` | T4 (Dashboard) |

## Task Table

| # | Task | FRs | Mode | Dependencies | Est. |
|---|------|-----|------|-------------|------|
| T1 | PostgreSQL Memory | FR-013 | code | None | 2h |
| T2 | Memory CLI + Hotkey + Greeting | FR-014, FR-016, FR-017 | code | T1 | 1.5h |
| T3 | YouTube Chat Integration | FR-015 | code | None | 2h |
| T4 | Dashboard / Monitor UI | FR-018 | code | T1, T2, T3 | 3h |

## Dependency Graph

```
T1 (DB Memory) ──► T2 (CLI + Hotkey + Greeting)
                                          │
T3 (YouTube Chat) ─────────────────────── ▼
                                     T4 (Dashboard)
```

**T1 and T3 are independent — can run in parallel.**
**T2 depends on T1 (needs DB for memory ops).**
**T4 depends on all others (dashboard shows everything).**

## Execution Order

1. **T1** + **T3** (parallel)
2. **T2** (after T1)
3. **T4** (after all)
