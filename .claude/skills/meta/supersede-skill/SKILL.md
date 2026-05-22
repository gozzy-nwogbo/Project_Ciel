# Skill: supersede-skill

Atomically retires a superseded skill in a single approved operation by striking through its registry row, deleting its filesystem folder, and logging the event to memory.md. Invoke on "supersede this skill", "retire skill", "deprecate skill", "supersede [name] with [name]." Output: modified registry at `03-skills/registry.md`, deleted folder, and memory.md entry.

---

## When to use

- When a skill has been replaced by a newer skill and needs formal retirement
- When registry-audit surfaces a supersession that was partially completed (struck-through but folder remains)
- On demand: "supersede this skill", "retire skill", "deprecate skill", "supersede [name] with [name]"

## When NOT to use

- To delete a skill that has no replacement (that's deletion, not supersession)
- To update or rename a skill (use registry-audit or manual edit)
- To change audit status (independent operation)

## Input

| Input | Required | Description |
|---|---|---|
| Superseded skill name | Yes | Name of the skill being retired |
| Superseded skill category | Yes | Category folder (e.g., writing, meta). Required to resolve ambiguity. |
| Replacement skill name | Yes | Name of the skill that replaces it |
| Operator approval | Yes | Explicit confirmation of both names before any modification |

## Process

1. **Verify superseded skill exists.** Check BOTH `03-skills/registry.md` (active, non-struck-through row) AND `.claude/skills/[category]/[superseded-name]/SKILL.md` on filesystem. If either is missing, halt and report which is absent.
2. **Verify replacement skill exists.** Check BOTH `03-skills/registry.md` (active row) AND `.claude/skills/[category]/[replacement-name]/SKILL.md` on filesystem. If either is missing, halt: "Replacement [name] not found in [location]. Cannot supersede with non-existent replacement."
3. **Confirm with operator.** Present: superseded skill name, category, audit status, replacement name. If superseded skill is DRAFT, note: "[skill] is currently DRAFT. Superseding anyway?" Wait for explicit approval.
4. **Strike through registry row.** Wrap each cell of the row individually in `~~text~~` markdown, matching the existing pattern in the Writing table's content-research-writer row (line 58). Do not wrap the entire row in a single `~~...~~` block. Append "Superseded by `[replacement-name]` ([date])" in the notes column. Decrement the category count and global "Total registered skills" count.
5. **Delete filesystem folder.** Remove `.claude/skills/[category]/[superseded-name]/` and all contents. Before deletion, verify folder contains only `.md` and `.json` files. If any other file types are present, halt and report. After deletion, verify the folder no longer exists.
6. **Update memory.md.** Append a one-line entry: "- [date]: superseded [skill-name], replaced by [replacement-name]."
7. **Report.** Inline confirmation: what row was struck, what folder was deleted, what memory entry was logged.

## Output Contract

**Produces:**
- Modified `03-skills/registry.md` (row struck through, counts decremented)
- Deleted folder at `.claude/skills/[category]/[superseded-name]/`
- Appended line in `.claude/memory.md`
- Inline confirmation report

**Does NOT produce:** migration of references from superseded to replacement skill, audit status changes on the replacement, quality comparison between old and new skill, struck-through row deletion (rows persist for history).

## Constraints

1. Never run without explicit operator approval of both the superseded skill name AND the replacement skill name.
2. Verify both skills exist in both registry (active row) and filesystem before any modification. Halt on any absence.
3. Strike-through pattern: wrap each cell individually in `~~text~~`. This matches the convention in registry-audit's detection logic (step 2: skill name cell is the canonical indicator).
4. Filesystem deletion targets folders containing only `.md` and `.json` files. Halt if any other file types are found.
5. If the operation halts mid-way, report which steps completed and which did not. Do not auto-rollback completed steps. Provide explicit recovery instructions.
6. Steps execute sequentially in order. When edge case 1 applies (already struck-through), the registry step is skipped and remaining steps execute in their normal order.

## Edge Cases

1. **Superseded skill is already struck-through but folder still exists.** Detected in step 1 (registry row is struck-through, so it fails the "active row" check). Report: "Skill is already struck-through in registry but folder still exists at [path]. Run filesystem cleanup only?" If operator confirms, skip step 4 (registry), proceed to step 5 (delete folder) and step 6 (memory).
2. **Replacement skill not found in registry.** Halt before any modification. Report: "Replacement [name] not found in registry. Cannot supersede with non-existent replacement. Verify spelling or register the replacement first."
3. **Multiple skills with the same name across categories.** Operator must provide category in input. If category is missing or ambiguous, halt and list all matches with their categories.
4. **Superseded skill has DRAFT audit status.** Allowed. Include in confirmation prompt: "[skill] is currently DRAFT. Superseding anyway?" Supersession is not gated on audit status.
5. **Folder contains non-standard file types** (anything other than `.md` and `.json`). Halt before deletion. Report: "Non-standard files found in [path]: [list]. Review before proceeding."

## Handoff

After this skill completes:
- **Artifact:** Modified registry, deleted folder, memory entry
- **Condition:** All three steps completed and inline report delivered
- **Routing:** Operator verifies the registry diff and confirms no downstream references need updating. If references exist, operator handles migration separately.
