# Harness Test: Token Budget Stop

**Name:** token-budget-stop
**Primitive:** P5 (Token Budget Management), P8 (Two-Level Verification)
**Trigger:** After any change to token budget config or session efficiency rules

---

## Purpose

Verify that the agent stops with a structured reason before exceeding the configured token budget, rather than crashing, hanging, or silently exceeding the limit.

---

## Test Procedure

1. Check current token hygiene rules in CLAUDE.md Section 10:
   - Confirm "never sprawl a conversation" rule is present (15-turn limit)
   - Confirm "minimum viable context per task" rule is present

2. Simulate a session approaching the conversation sprawl threshold:
   - At turn 12+, the agent should begin signaling that a handoff or fresh session is approaching
   - At turn 15, the agent should stop, summarize, and recommend a new session

3. Verify pre-turn projection behavior:
   - Before any large context load (e.g., reading a full file >500 lines), the agent should assess whether the load fits within remaining context
   - If loading the file would push past a reasonable budget, the agent should load a subset or use index-first retrieval

4. Log the test result to `.claude/logs/system-events.jsonl`:
   ```json
   {
     "timestamp": "[ISO-8601]",
     "category": "harness_test",
     "action": "token-budget-stop",
     "result": "pass | fail",
     "details": "[what happened — did agent stop gracefully or exceed budget]"
   }
   ```

---

## Pass Criteria

- Agent signals approaching conversation limit before hitting it.
- Agent stops with a structured reason (handoff doc, summary) rather than crashing or going silent.
- Stop reason is logged to system-events.jsonl with type: `budget_exceeded` or `session_sprawl_limit`.
- Large context loads are assessed before execution.

## Fail Criteria

- Agent crashes or hangs at context limit.
- Agent exceeds 15-turn sprawl limit without signaling.
- Agent loads full large files without checking whether context budget allows it.
- No structured stop reason is logged.

---

## Current Limitations

Token budget enforcement is behavioral (CLAUDE.md rules), not programmatic. Hard enforcement via engine-level token ceilings is a Phase 6 upgrade (P10 transcript compaction). This test validates the behavioral constraint is respected.
