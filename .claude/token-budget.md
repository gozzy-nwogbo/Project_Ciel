# Token Budget

**Primitive:** 5 (Token Budget)
**Phase:** 2 (Context Persistence)
**Status:** Limits defined. Enforcement deferred to Phase 3.

---

## Current Limits

| Limit | Value | Rationale |
|---|---|---|
| Max turns per session | 50 | Prevents context sprawl. CLAUDE.md says fresh conversation every 10-15 turns, 50 is the hard ceiling. |
| Max input tokens per session | 150,000 | Leaves headroom within model context window for output and tool results. |

## Where Limits Are Defined

Limits live in `.claude/scripts/session-start.py` as the `TOKEN_BUDGET` dict. This is the single source of truth. The session-start hook outputs these limits in the memory layer banner so they are visible at the start of every session.

## How to Adjust

Edit the `TOKEN_BUDGET` dict in `.claude/scripts/session-start.py`:

```python
TOKEN_BUDGET = {
    "max_turns": 50,
    "max_input_tokens": 150_000,
}
```

Changes take effect on the next session start.

## Enforcement Roadmap

**Current (Phase 2):** Limits are displayed at session start as a behavioral instruction. The agent is expected to self-enforce by summarizing and handing off before hitting limits.

**Phase 3:** Pre-turn token projection. Before each API call, estimate whether the call will exceed the budget. If it will, emit a structured stop event and write a handoff doc instead of making the call.

**Phase 6:** Transcript compaction integration. Auto-compact triggers before the token ceiling, preserving the original session goal. If compaction is needed twice in one session, force a fresh session with handoff.
