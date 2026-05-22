# Session Start Hook

**Script:** `.claude/scripts/session-start.py`

## What it does
- Loads memory layer files (soul.md, user.md, memory.md, index.md) into context
- Displays token budget limits (50 turns, 150k input tokens)
- Checks `04-reflections/voice-evolution-log.md` next_review_date against today; if due, surfaces a non-blocking review prompt before loading anything else
- Queries `act_now` table for open items older than 24 hours; if found, surfaces them as an informational list before any other work begins (Phase 6.2)

## Prerequisites
- The Open Brain MCP server should be available for Supabase-backed tools.
  It is configured in `.mcp.json` and starts automatically when Claude Code connects.
- Environment variables must be set: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `OPENAI_API_KEY`
  (loaded from `.env` at vault root)
- `01-projects/open-brain/scripts/write_act_now.py` must exist for the ACT NOW query

## ACT NOW surfacing (Phase 6.2)
The unresolved items surface is **informational only**. No action is required at session start. The items are shown so the user has context about pending commitments from previous sessions.
