# /close-session

Close the current session with full handoff protocol. Execute all 7 steps in order. Do not skip any step.

---

## Step 1: Session Summary

Write a 3-5 sentence summary of what was accomplished this session. Be specific: name actual deliverables, files created or modified, decisions made, and integrations touched. No generic filler.

## Step 2: Decisions Log

List every decision made this session that affects future sessions. Format each as:

```
Decision: [what was decided]
Reason: [why this decision was made]
Impact: [what changes downstream as a result]
```

If no decisions were made, write "No new decisions this session."

## Step 3: Open Questions

List anything raised but not resolved. These are inputs to the next session, not failures. Format as a bullet list. If nothing is unresolved, write "No open questions."

## Step 4: ACT NOW Protocol

Follow the behavioral protocol defined in `.claude/hooks/session-end.md`. This step is mandatory even if the session was short.

1. Scan the session for ACT NOW candidates: commitments made, open questions not resolved, decisions flagged for revisiting, blockers not cleared.
2. Exclude: tasks already in Asana, items already in `.continue-here.md`, fully resolved decisions, routine informational captures.
3. If no candidates: print "No ACT NOW items identified." and proceed to Step 5.
4. If candidates found: surface them as a numbered list with proposed priority (high/medium/low). Ask the user: "Approve all, edit, or dismiss?"
5. **Wait for explicit user approval before writing anything.** Never write to act_now without approval.
6. For each approved item, run:
   ```bash
   python3 01-projects/open-brain/scripts/write_act_now.py --write --item "<item text>" --priority <high|medium|low>
   ```
   Add `--due YYYY-MM-DD` if a specific deadline was identified.
7. Confirm: "[N] ACT NOW items written to Supabase."

## Step 4b: Permission Log — Session Close Entry

Write a session close entry to permission_log by running:

```bash
python3 01-projects/open-brain/scripts/log_permission.py \
  --integration system \
  --tool session_close \
  --tier read-only \
  --action "session closed" \
  --inputs "session_type: [declared type this session], handoff_written: true" \
  --result success \
  --reason "session close — /close-session invoked" \
  --session-id "[current session ID]"
```

This runs after ACT NOW and before the handoff doc is written. If the script fails, note it but do not block the session close.

## Step 5: Next Session Starting Point

Write one sentence starting with "Next session should start by..." that is specific enough for a fresh Claude instance to know exactly where to pick up. Reference specific files, tasks, or decisions.

## Step 6: Write Handoff Doc

Write to `06-daily/[YYYY-MM-DD].md` using today's date.

**If the file already exists:** Append under a new `## Session [N]` header (increment from the last session number in the file). Never overwrite existing content.

**If the file does not exist:** Create it with this structure:

```markdown
# [YYYY-MM-DD]

## Session 1

### Summary
[From Step 1]

### Decisions
[From Step 2]

### Open Questions
[From Step 3]

### ACT NOW
[Items written, or "No ACT NOW items this session"]

### Next
[From Step 5]
```

**Hard constraint:** The handoff doc must exist and be written before Step 7 runs.

## Step 7: Confirm

Surface this message and then stop:

```
Session closed. Handoff written to 06-daily/[date].md. [N] ACT NOW items logged.
```

Replace [date] with the actual date and [N] with the count of ACT NOW items written (0 if none).

---

## Hard Constraints

- Never skip Step 4 (ACT NOW) even if the session was short
- Never overwrite an existing daily log. Always append.
- Handoff doc must exist before confirming complete (Step 6 before Step 7)
- Never write to act_now table without explicit user approval
- This command writes to: `06-daily/`, Supabase `act_now` table (with approval)
- All other vault paths are read-only during this command
