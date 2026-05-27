---
description: Generate or transition a LinkedIn post draft from the second-brain atom graph
allowed-tools: Bash
---

# /draft-post

Generate or transition LinkedIn post drafts. See `01-projects/linkedin/docs/command-reference.md` for full flag reference.

## Behavior

When the user types `/draft-post [args]`:

1. **Invoke the wrapper.** All env resolution (PYTHONPATH, LINKEDIN_*, vault dotenv) is handled by `01-projects/linkedin/bin/draft-post`. Single source of truth.

   ```bash
   /Users/gozzynwogbo/second-brain/01-projects/linkedin/bin/draft-post $ARGS
   ```

2. **After invocation:**
   - Read the bundle's `text.md` and `meta.json` from `01-projects/linkedin/backlog/<slug>/` to surface the result.
   - Report: the slug, the angle, the strategy used, and any voice-linter annotations.

## Conversational fallback

If the user gives natural-language instructions instead of flags (e.g., "kill the third one because the angle was too abstract"):
1. Read `01-projects/linkedin/backlog/` to identify the target slug.
2. Construct the equivalent `--kill <slug> --reason "..."` invocation.
3. Confirm the intended action with the user before running.

## Permission logging

This command writes state. Log to `01-projects/linkedin/logs/state.jsonl` (the CLI does this automatically) AND to `.claude/logs/system-events.jsonl` per CLAUDE.md §15. Include `reason` field.
