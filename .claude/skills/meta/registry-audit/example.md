# Registry Audit — Constructed Example

> This example is constructed to demonstrate all drift categories. It does not reflect the actual current state of the vault.

## Scenario

Filesystem contains these SKILL.md files:
- `.claude/skills/meta/skill-creator/SKILL.md`
- `.claude/skills/meta/skill-authoring/SKILL.md`
- `.claude/skills/meta/new-unregistered-skill/SKILL.md`
- `.claude/skills/writing/content-research/SKILL.md`
- `.claude/skills/n8n/n8n-code-javascript/SKILL.md`
- `.claude/skills/n8n/credential-pin/SKILL.md`

Registry contains these active rows:
- `skill-creator` at `.claude/skills/meta/skill-creator/` — matches filesystem
- `skill-authoring` at `.claude/skills/meta/skill-authoring/` — matches filesystem
- `content-research` at `.claude/skills/writing/content-research/` — matches filesystem
- `n8n-code-javascript` at `.claude/skills/n8n/n8n-code-javascript/` — matches filesystem
- `credential-pin` at `.claude/skills/n8n/credential-pin/` — matches filesystem
- `old-removed-skill` at `.claude/skills/meta/old-removed-skill/` — no filesystem match
- `voice-matcher` at `.claude/skills/design/voice-matcher/` — no filesystem match

Registry contains one struck-through row:
- ~~`content-research-writer`~~ at ~~`.claude/skills/writing/content-research-writer/`~~ — Superseded by `content-research`

Registry header says: "Total registered skills: 8"

## Audit Output

```markdown
# Registry Audit Report — 2026-04-29

## Summary
- Skills in filesystem: 6
- Rows in registry (active): 7
- Struck-through rows (excluded): 1
- Drift detected: 3 issues

## Orphan skills (filesystem → registry)
1. `.claude/skills/meta/new-unregistered-skill/SKILL.md`
   - Proposed fix: Add registry row — Category: Meta, Path: `.claude/skills/meta/new-unregistered-skill/`, Audit: DRAFT

## Stale registry rows (registry → filesystem)
1. `old-removed-skill` at `.claude/skills/meta/old-removed-skill/`
   - No SKILL.md found at this path
   - Fix option A: Remove row from registry
   - Fix option B: Update path if skill was moved (operator to confirm new location)

2. `voice-matcher` at `.claude/skills/design/voice-matcher/`
   - No SKILL.md found at this path
   - Fix option A: Remove row from registry
   - Fix option B: Update path if skill was moved (operator to confirm new location)

## Path mismatches
None detected.

## Structural errors
None detected.

## Header drift
Registry header says 8 skills, actual active count is 7. Update header to 7.

## Informational
No empty categories detected.
Struck-through row preserved: `content-research-writer` (Superseded by content-research) — not flagged as drift.
```

## Key Observations

- `new-unregistered-skill` was detected as an orphan because it exists in filesystem but has no registry row.
- `old-removed-skill` and `voice-matcher` are stale because their registry paths point to nonexistent SKILL.md files.
- The struck-through `content-research-writer` row was correctly excluded from drift checks.
- Header count (8) does not match active row count (7), flagged as header drift.
- All fixes require explicit operator approval before any registry write occurs.
