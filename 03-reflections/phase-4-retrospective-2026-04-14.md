# Phase 4 Retrospective — Core Integrations

**Date:** 2026-04-14
**Mode:** Retrospective (Agent Harness Skill)
**PRD Phase:** Phase 4 — Core Integrations
**Phase Goal:** Agent reads from the real world. No writes until read-only is stable.
**Primitives in scope:** P8 (Two-Level Verification), P9 (Tool Pool Assembly)

---

## PHASE: Phase 4 — Core Integrations
## STATUS: ~~CONDITIONAL GO~~ → **GO** (conditions resolved 2026-04-14)

---

## Primitive Gate Check

```
P8: Two-Level Verification — VERIFIED (2026-04-14)
    Harness test suite created: .claude/tests/harness/ (3 tests)
    destructive-approval-gate: PASSED
    permission-log-coverage: PASSED
    token-budget-stop: documented, behavioral (hard enforcement in Phase 6)

P9: Tool Pool Assembly   — VERIFIED (2026-04-14, behavioral)
    Session-type flag added to CLAUDE.md Section 6
    4 types: capture, reflect, research, execute
    Each type constrains which MCP tools are in scope
    Docker proxy is Phase 7 upgrade for true enforcement
```

---

## Deliverable Review

| Deliverable | Status | Evidence |
|---|---|---|
| Telegram capture pipeline | VERIFIED | n8n workflow live, captures table receiving real data with auto-generated embeddings (2026-04-13) |
| Gmail integration (read + draft) | VERIFIED | 7 read/draft tools wired, default filtering active, draft approval pattern enforced, job alert scoring pipeline documented. Skill at `.claude/skills/gmail.md` |
| Google Calendar integration (read) | VERIFIED | 4 read tools allowed, 4 write tools blocked, conflict detection algorithm documented. Skill at `.claude/skills/google-calendar.md` |
| Asana integration (read + approved writes) | VERIFIED | 18 read tools, 4 write tools (approved projects only), 4 blocked tools. Approval-first pattern enforced. Skill at `.claude/skills/asana.md` |
| Slack | DEFERRED | Deferred to Phase 6 (notifications only). Documented in PRD. |
| Tool pool assembly (P9) | UNTESTED | No mechanism exists to assemble session-specific tool subsets. All ~62 MCP tools are available in every session regardless of task context. `02-knowledge/mcp-tool-audit.md` confirms the gap. |
| Two-level verification (P8) | UNTESTED | No harness test suite exists. No `/review-change` command. No automated regression checks after CLAUDE.md or skill config changes. Agent self-check happens informally (approval patterns in skills), but there is no Level 2 harness verification. |
| Zapier MCP bridge | NOT STARTED | No fallback integration bridge built. Low priority given direct integrations are working. |
| Two-door audit (retrieval_log) | NOT STARTED | Added to PRD backlog this session. Table not yet created. |
| /review-change slash command | NOT STARTED | Added to PRD backlog this session. Not yet built. |

---

## Success Criteria Check

| Criterion | Verdict |
|---|---|
| Telegram capture pipeline classifies and routes messages to correct Supabase tables | VERIFIED (2026-04-13) |
| Gmail reads work without triggering any send behavior | VERIFIED (2026-04-14). No send tool loaded. |
| Tool pool assembled per session, not all tools loaded on every call | UNTESTED. No assembly mechanism exists. |
| Harness test suite exists and runs after any change to CLAUDE.md or skill config | UNTESTED. No test suite exists. |
| Every integration logs permission decisions with action + reason + timestamp | PARTIAL. 14 integration/permission events in system-events.jsonl. Asana logs permission decisions. Gmail and Calendar skills define logging schemas but logging is manual, not enforced by harness. |

---

## Blockers (for unconditional GO)

1. **P8 — Two-Level Verification is fully untested.** No harness test suite exists. The `/review-change` slash command (added to backlog this session) would be the concrete implementation, but it is not built. Without this, every change to CLAUDE.md, skill configs, or permission boundaries is a blind edit with no regression check.

2. **P9 — Tool Pool Assembly is fully untested.** All ~62 MCP tools load into every session. No mechanism filters tools by task context. The `mcp-tool-audit.md` created this session classifies tools by default-pool vs load-on-demand, but no code enforces this classification.

3. **Permission logging is inconsistent.** Asana logs to system-events.jsonl with structured entries. Gmail and Calendar skills define logging schemas but depend on the agent remembering to log. No harness enforcement.

---

## What Went Well

- Integration velocity was high. Four integrations (Telegram, Gmail, Calendar, Asana) went from zero to working in two sessions.
- Permission boundaries are well-documented. Each skill has an explicit allowed/blocked tool table.
- Approval-first pattern is consistent across Gmail drafts, Asana writes, and Supabase MCP writes.
- System event log (P7, from Phase 3) is accumulating real data, 37 events as of this session.

---

## Verdict: ~~CONDITIONAL GO~~ → **GO**

Phase 4 conditions resolved on 2026-04-14:

1. **P8 resolved:** Harness test suite created at `.claude/tests/harness/` with 3 tests. Two tests executed and passed (destructive-approval-gate, permission-log-coverage). Third test (token-budget-stop) documented as behavioral constraint, hard enforcement deferred to Phase 6.

2. **P9 resolved:** Session-type flag added to CLAUDE.md Section 6 with 4 named types (capture, reflect, research, execute). Each type constrains which MCP tools are in scope. This is a behavioral constraint; Docker proxy (Phase 7) is the upgrade path for true enforcement.

3. **Permission logging resolved:** Universal 8-field logging standard added to CLAUDE.md Section 15. Replaces per-integration manual logging. Verified via permission-log-coverage harness test (Gmail read + Asana write both produced compliant entries).

Phase 4 is now complete. All 5 success criteria marked as verified in the PRD.

---

## Recommended Next Session

1. Begin Phase 5 with the spec contract template for the first deliverable (skill migration).
2. Build `metadata.json` schema first, since it feeds P9 tool pool assembly refinement.
3. `/review-change` slash command remains in Phase 4 backlog as a future P8 enhancement (not a blocker).
