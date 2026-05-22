# Session End Hook

**Script:** `.claude/scripts/summarize-session.py` (background daily log write, unchanged)

## What it does (Python hook)
- Reads conversation transcript from stdin
- Spawns detached background process to call Anthropic API (Haiku)
- Writes structured summary to `06-daily/[YYYY-MM-DD].md`
- Exits immediately so the hook does not block

## ACT NOW Capture Protocol (Phase 6.2)

Before ending any session, Claude executes this protocol in-session. This is behavioral, not automated. The Python hook handles the daily log; this protocol handles ACT NOW items.

### Step 1: Identify candidates

Read these two sources:
1. Today's daily log at `06-daily/[YYYY-MM-DD].md` (if it exists from earlier sessions)
2. `.claude/memory.md` for any decisions flagged as needing follow-up

Scan for ACT NOW candidates matching this definition:
- Commitments made in the session ("I'll fix X", "we need to...")
- Open questions not resolved by session end
- Decisions flagged for revisiting
- Blockers identified but not cleared

**Exclusions (do NOT flag these):**
- Tasks already tracked in Asana
- Items already written to a handoff doc (`.continue-here.md`)
- Fully resolved decisions with no pending action
- Routine captures that are just informational

### Step 2: Surface or exit

**If no candidates found:** Print "No ACT NOW items identified." and proceed with normal session end. No prompt.

**If candidates found:** Surface them as a numbered list:

```
ACT NOW candidates from this session:
1. [high] Fix broken test in auth module
2. [medium] Review PR feedback on digest workflow
3. [low] Research alternative to current cron approach

Approve all, edit, or dismiss?
```

Each item gets a proposed priority:
- **high** — commitment with a deadline or blocker affecting other work
- **medium** — open question or decision needing follow-up
- **low** — nice-to-have, no time pressure

### Step 3: Wait for approval

**Hard constraint: Never write to act_now without explicit user approval.**

Accept these responses:
- "approve" / "approve all" / "yes" — write all items as proposed
- "edit" — user modifies the list (add/remove/change priority), then re-approve
- "dismiss" / "no" / "skip" — write nothing, exit cleanly
- Specific edits like "remove 2, change 1 to medium" — apply and re-surface for final approval

### Step 4: Write approved items

For each approved item, run:
```bash
python3 01-projects/open-brain/scripts/write_act_now.py --write --item "<item text>" --priority <high|medium|low>
```

Add `--due YYYY-MM-DD` if a specific deadline was identified in the session.

### Step 5: Confirm and proceed

After writing, confirm:
```
[N] ACT NOW items written to Supabase.
```

Then proceed with normal session end (daily log, handoff doc per CLAUDE.md Section 11).
