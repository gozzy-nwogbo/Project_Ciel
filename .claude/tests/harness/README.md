# Harness Test Suite

**Primitive:** P8 (Two-Level Verification)
**Created:** 2026-04-14
**Automation target:** Phase 6

---

## What This Is

Three manual regression tests that verify the agent harness guarantees hold after any configuration change. These tests must be run manually after any change to:

- `CLAUDE.md` (behavioral rules, session types, permission boundaries)
- Any skill config in `.claude/skills/`
- Integration permission tables
- MCP server configuration (`.mcp.json`)

---

## Tests

| Test | File | What It Checks |
|------|------|---------------|
| Destructive Approval Gate | `destructive-approval-gate.md` | Blocked/destructive tools never execute without explicit confirmation |
| Token Budget Stop | `token-budget-stop.md` | Agent stops gracefully at budget limits, does not crash or exceed |
| Permission Log Coverage | `permission-log-coverage.md` | Every MCP tool call produces a compliant system-events.jsonl entry |

---

## How to Run

1. Open each test file and follow the procedure step by step.
2. Log each result to `.claude/logs/system-events.jsonl` with `category: harness_test`.
3. If any test fails, do not advance to the next build phase until the failure is resolved.

---

## When to Run

- After any CLAUDE.md edit that touches Sections 6 (Session Types), 9 (Skill Invocation), or 15 (Permission Logging)
- After adding or modifying any integration skill
- After changing `.mcp.json`
- Before closing any build phase (as part of retrospective)

---

## Automation (Phase 6 Upgrade)

These tests are currently manual. Phase 6 will introduce:
- A post-config-change hook that triggers the test suite automatically
- Structured pass/fail output written to `.claude/tests/harness/results/`
- Integration with the `/review-change` slash command (when built)
