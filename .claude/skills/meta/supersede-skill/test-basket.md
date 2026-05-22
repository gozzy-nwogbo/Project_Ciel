# Test Basket: supersede-skill

## T1 — Clean supersession (happy path)

**Input:** Supersede `invoice-organizer` (productivity) with a hypothetical `expense-tracker` (productivity). Both exist in registry (active rows) and filesystem.
**Expected:** Registry row for invoice-organizer struck through cell-by-cell, "Superseded by `expense-tracker` (2026-04-29)" in notes. Productivity count decremented. Global count decremented. Folder `.claude/skills/productivity/invoice-organizer/` deleted. Memory.md entry appended.

## T2 — Already struck-through, folder remains (edge case 1)

**Input:** Supersede `content-research-writer` (writing) with `content-research`. Registry row is already struck-through. Folder `.claude/skills/writing/content-research-writer/` still exists.
**Expected:** Step 1 detects struck-through row. Operator prompted: "Run filesystem cleanup only?" On approval, step 4 skipped. Folder deleted. Memory entry appended. No registry modification.

## T3 — Replacement skill does not exist (edge case 2)

**Input:** Supersede `file-organizer` (productivity) with `smart-sorter`. `smart-sorter` does not exist in registry or filesystem.
**Expected:** Halt before any modification. Report: "Replacement smart-sorter not found in registry. Cannot supersede with non-existent replacement. Verify spelling or register the replacement first." No files changed.

## T4 — Ambiguous category (edge case 3)

**Input:** Supersede a skill named `validator` without specifying category. Hypothetically, `validator` exists in both `meta/` and `n8n/`.
**Expected:** Halt. Report: "Multiple skills named 'validator' found: meta/validator, n8n/validator. Specify category to resolve ambiguity." No files changed.

## T5 — DRAFT audit status (edge case 4)

**Input:** Supersede `file-organizer` (productivity, DRAFT status) with a hypothetical replacement.
**Expected:** Confirmation prompt includes: "file-organizer is currently DRAFT. Superseding anyway?" On operator approval, proceeds normally. DRAFT status does not block supersession.

## T6 — Non-standard files in folder (edge case 5)

**Input:** Supersede a skill whose folder contains `SKILL.md`, `metadata.json`, and `debug.py`.
**Expected:** Halt before deletion. Report: "Non-standard files found in [path]: debug.py. Review before proceeding." No deletion occurs until operator resolves.

## T7 — Partial failure recovery

**Input:** Supersede a valid skill. Registry strike-through succeeds (step 4). Filesystem deletion fails (step 5, e.g., permission error).
**Expected:** Report: "Step 4 (registry strike-through) completed. Step 5 (filesystem deletion) failed: [error]. Step 6 (memory update) not attempted. Recovery: manually delete `.claude/skills/[category]/[name]/` and append memory entry, or re-run supersede-skill which will trigger edge case 1 (already struck-through)."

## T8 — Superseded skill missing from filesystem

**Input:** Supersede a skill that has an active registry row but no folder on disk.
**Expected:** Halt in step 1. Report: "Skill [name] found in registry (active row) but `.claude/skills/[category]/[name]/SKILL.md` not found on filesystem. This may indicate a partial supersession or manual deletion. Investigate before proceeding."
