---
description: Generate or transition a LinkedIn post draft from the second-brain atom graph
allowed-tools: Bash
---

# /draft-post

Generate or transition LinkedIn post drafts. See `01-projects/linkedin/docs/command-reference.md` for full flag reference.

## Behavior

When the user types `/draft-post [args]`:

1. **Resolve paths.** Set environment so the CLI knows where atoms, project, and brand-spec live:
   - `LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge`
   - `LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin`
   - `LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md`

2. **Invoke the Python CLI** with the user's flags appended:

   ```bash
   cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
   PYTHONPATH=src \
   LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
   LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
   LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
   python -m cli.draft_post $ARGS
   ```

3. **After invocation:**
   - Read the bundle's `text.md` and `meta.json` from `01-projects/linkedin/backlog/<slug>/` to surface the result.
   - Report: the slug, the angle, the strategy used, and any voice-linter annotations.

## Conversational fallback

If the user gives natural-language instructions instead of flags (e.g., "kill the third one because the angle was too abstract"):
1. Read `01-projects/linkedin/backlog/` to identify the target slug.
2. Construct the equivalent `--kill <slug> --reason "..."` invocation.
3. Confirm the intended action with the user before running.

## Permission logging

This command writes state. Log to `01-projects/linkedin/logs/state.jsonl` (the CLI does this automatically) AND to `.claude/logs/system-events.jsonl` per CLAUDE.md §15. Include `reason` field.
