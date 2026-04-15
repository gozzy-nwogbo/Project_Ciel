# Session Start Hook

**Script:** `.claude/scripts/session-start.py`

## What it does
- Loads memory layer files (soul.md, user.md, memory.md, index.md) into context
- Displays token budget limits (50 turns, 150k input tokens)
- Checks `03-reflections/voice-evolution-log.md` next_review_date against today; if due, surfaces a non-blocking review prompt before loading anything else

## Prerequisites
- The Open Brain MCP server should be available for Supabase-backed tools.
  It is configured in `.mcp.json` and starts automatically when Claude Code connects.
- Environment variables must be set: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `OPENAI_API_KEY`
  (loaded from `.env` at vault root)
