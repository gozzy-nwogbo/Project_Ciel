# Example: Superseding content-research-writer with content-research

## Context

On 2026-04-16, the `content-research` skill was built as a replacement for `content-research-writer` in the Writing category. The registry row was struck through manually, but the filesystem folder at `.claude/skills/writing/content-research-writer/` was not deleted. On 2026-04-29, `registry-audit` detected this as real drift: a struck-through row with a surviving folder. This is exactly the scenario supersede-skill is designed to handle atomically.

## Input

- **Superseded skill name:** content-research-writer
- **Superseded skill category:** writing
- **Replacement skill name:** content-research

## Execution (edge case 1 — already struck-through)

This example demonstrates edge case 1 (already-struck-through partial cleanup) because that was the actual real-world scenario that triggered the skill build. Full happy-path supersession (active skill with no prior strike-through) follows the same flow but includes step 4 (registry strike-through), which this example skips.

### Step 1: Verify superseded skill exists

- Registry check: Row found in Writing table, but skill name cell is wrapped in `~~text~~`. Row is struck-through.
- Filesystem check: `.claude/skills/writing/content-research-writer/SKILL.md` exists.
- **Result:** Edge case 1 detected. Report to operator: "Skill is already struck-through in registry but folder still exists at `.claude/skills/writing/content-research-writer/`. Run filesystem cleanup only?"

### Step 2: Verify replacement skill exists

- Registry check: `content-research` found in Writing table, active row, audit status PASS.
- Filesystem check: `.claude/skills/writing/content-research/SKILL.md` exists.
- **Result:** Replacement verified.

### Step 3: Confirm with operator

Operator confirms filesystem cleanup for already-struck-through skill.

### Step 4: Strike through registry row — SKIPPED

Already struck-through per edge case 1.

### Step 5: Delete filesystem folder

- Verify folder contents: `SKILL.md`, `metadata.json`, `skill-audit-content-research-writer.md` (all `.md` and `.json`).
- Delete `.claude/skills/writing/content-research-writer/`.
- Verify folder no longer exists.

### Step 6: Update memory.md

Append: "- 2026-04-29: superseded content-research-writer, replaced by content-research."

### Step 7: Report

```
Supersession complete (edge case 1 — partial cleanup):
- Registry: already struck-through (no change)
- Filesystem: .claude/skills/writing/content-research-writer/ deleted (3 files)
- Memory: entry appended to .claude/memory.md
```
