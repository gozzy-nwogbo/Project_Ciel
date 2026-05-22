# Skill: registry-audit

Detects drift between `.claude/skills/` (runtime filesystem) and `03-skills/registry.md` (human-facing index), classifying mismatches as orphan skills, stale registry rows, or path mismatches, and producing a dated audit report at `01-projects/open-brain/reports/registry-audit-[YYYY-MM-DD].md` with per-issue fix proposals requiring explicit operator approval.

---

## When to use

- Before milestone completions or phase transitions
- After adding, renaming, or moving skills
- On demand: "audit the skill registry", "check for skill drift", "registry audit", "verify registry", "find orphan skills"

## When NOT to use

- To validate skill content quality (use skill-authoring)
- To check audit status drift (audit status exists only in registry, no filesystem counterpart)
- To modify or delete SKILL.md files (filesystem is authoritative)

## Input

| Input | Required | Description |
|---|---|---|
| Filesystem scan | Yes | `.claude/skills/**/SKILL.md` — all skill files found recursively |
| Registry file | Yes | `03-skills/registry.md` — all active (non-struck-through) rows |

## Process

1. **Snapshot filesystem:** Glob `.claude/skills/**/SKILL.md`. Group results by parent directory. If any parent directory contains more than one SKILL.md, flag as structural error, exclude both from all subsequent drift checks, and skip to step 6 reporting. Remaining results form the filesystem set (category from first directory under `skills/`, name from second).
2. **Snapshot registry:** Parse `03-skills/registry.md`. For each row in a category table, extract skill name, path, and audit status. A row is struck-through if the **skill name cell** contains the `~~text~~` pattern. Other cells may or may not be struck-through. The skill name cell is the canonical indicator. Exclude all struck-through rows from the registry set.
3. **Detect orphan skills:** Filesystem skills with no matching active registry row. Propose: add row with detected category, path, DRAFT status.
4. **Detect stale rows:** Active registry rows whose path resolves to no SKILL.md in the filesystem. Propose: remove row or rename to match (operator picks).
5. **Detect path mismatches:** Skills in both sets where registry path differs from filesystem path. Propose: update registry path.
6. **Detect structural errors:** Report any parent directories flagged in step 1 (multiple SKILL.md). Report any skill-category folders with no SKILL.md inside. Do not produce duplicate orphan flags for structurally invalid folders.
7. **Detect header drift:** Count active rows vs. "Total registered skills: N" header. Flag if mismatched.
8. **Detect empty categories:** Registry sections with zero active rows. Report as informational.
9. **Compile report** to `01-projects/open-brain/reports/registry-audit-[YYYY-MM-DD].md`.
10. **Present findings.** Each fix requires explicit operator approval before any registry write.

## Output Contract

**Produces:** `01-projects/open-brain/reports/registry-audit-[YYYY-MM-DD].md`

**Structure:**

```markdown
# Registry Audit Report — [YYYY-MM-DD]

## Summary
- Skills in filesystem: N
- Rows in registry (active): M
- Struck-through rows (excluded): S
- Drift detected: K issues

## Orphan skills (filesystem → registry)
[per-issue: path, proposed row]

## Stale registry rows (registry → filesystem)
[per-issue: row content, fix options]

## Path mismatches
[per-issue: registry path vs filesystem path]

## Structural errors
[multiple SKILL.md folders, incomplete folders]

## Header drift
[count mismatches]

## Informational
[empty categories, observations]
```

**Does NOT produce:** filesystem modifications, automatic registry writes, skill quality assessments, audit status drift checks, struck-through row deletions.

## Constraints

1. Never write to registry without explicit operator approval per fix.
2. Never delete a SKILL.md file. Filesystem is authoritative.
3. Struck-through rows are identified by the `~~text~~` pattern in the skill name cell only. Exclude from all drift checks.
4. Operate on point-in-time snapshot. If sources change mid-audit, halt and re-run.
5. Audit status drift is out of scope. No filesystem-side audit status exists to drift against.
6. Reports are append-only. Each run produces a separate dated file. Never overwrite prior reports.

## Edge Cases

1. **Empty registry category:** Not drift. Report as informational: "Consider folding or removing the section header."
2. **Multiple SKILL.md files in one folder:** Structural error flagged in step 1, excluded from drift checks. Do not auto-resolve.
3. **Skill folder exists but no SKILL.md:** Flag as orphan-pending: "Folder at [path] has no SKILL.md. Complete the skill or remove the folder."
4. **Registry total count mismatch:** Header says N, actual count is M. Flag as header drift with proposed fix.

## Handoff

After this skill completes:
- **Artifact:** Dated audit report at `01-projects/open-brain/reports/registry-audit-[YYYY-MM-DD].md`
- **Condition:** All drift issues reported and operator has approved/declined each fix
- **Routing:** Approved fixes applied to `03-skills/registry.md`. Declined fixes remain in report. Structural errors route to manual resolution.
