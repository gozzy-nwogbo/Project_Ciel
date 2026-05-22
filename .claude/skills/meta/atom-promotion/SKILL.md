# Skill: atom-promotion

Validates knowledge atoms in `00-inbox/staging/framework-atoms/[domain]/` against the atom front-matter standard, promotes passing atoms to `02-knowledge/[domain]/`, and flags failing atoms in place. Invoke when staging atoms are ready for promotion. Produces a promotion report at `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md`.

---

## When to Trigger

- Staging atoms exist in `00-inbox/staging/framework-atoms/` and are ready for promotion
- After a notebook-builder run populates staging with new atoms
- Periodic quality gate before knowledge layer grows stale

Do NOT trigger as part of remediation. Remediation is a future, separate skill — flagged atoms remain in staging until that workflow exists.

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Staging directory | Yes | `00-inbox/staging/framework-atoms/` containing domain subfolders |
| Front-matter standard | Yes | `.claude/standards/atom-front-matter.md` (D1-D7 rules) |
| Target directory | Yes | `02-knowledge/` where promoted atoms land |
| Domain filter | No | Single domain name to run on one domain only (default: all) |

---

## Constraints

| # | Rule | Binary test |
|---|------|-------------|
| H1 | Never delete a staging atom without first writing it to its destination | Copy to destination verified before source removal |
| H2 | Never promote an atom that fails any disqualification rule (D1-D7) | All 7 rules pass = promote; any fail = flag |
| H3 | Never write to `02-knowledge/` if the file already exists at the destination | Halt entire run and report collision |
| H4 | Never modify atom body content during promotion | Only YAML front matter fields (`status`, `flag_reasons`, `quality_flags`) may be added |
| H5 | Never proceed past verification if file counts do not reconcile | promoted + flagged + errors = total staged |
| H6 | Approval-first on first run | After pre-flight, propose summary and wait for explicit "yes" |

---

## Procedure

### Phase 1 — Pre-flight

1. Scan all domain folders in staging. Count atoms per domain.
2. For each atom, run D1-D7 validation. Classify as `pass`, `flag`, or `error`.
3. For each passing atom, run soft-flag checks (see Soft-Flag Logic below). Record any quality warnings.
4. Check every passing atom's destination path for collisions (H3).
5. Produce an in-memory classification list: atom path, verdict (pass/flag/error), D-rule failures (if any), quality flags (if any). Phases 2-3 read from this list. Do not re-validate in later phases. Single classification per run.
6. Present summary: "About to promote N atoms across M domains. K will be flagged. E have errors. Q atoms have quality warnings. Proceed?"
7. Wait for explicit approval before any file writes.

### Phase 2 — Promote

For each passing atom, in alphabetical order by domain then filename:
1. Create domain folder in `02-knowledge/` if it does not exist.
2. If the atom has quality flags, prepare a modified copy in memory with `quality_flags` added to the YAML frontmatter. Do NOT modify the source file in staging.
3. Write the in-memory copy (with `quality_flags` if applicable) to `02-knowledge/[domain]/[filename]`.
4. Verify destination file exists. Verify destination content equals the source content with the `quality_flags` field added (if applicable). If verification fails, halt — do not remove source.
5. Remove source file from staging.

### Phase 3 — Flag

For each failing atom:
1. Set YAML front matter on the file in place (in staging). If the file already has a `---` front matter block, replace it entirely. Do not append a second block. The atom must end the run with exactly one YAML front matter block at the top.
   ```yaml
   ---
   status: flagged
   flag_reasons:
     - "D1: invalid YAML frontmatter"
     - "D4: source_date not ISO 8601"
   ---
   ```
2. Do not move the file. It stays in staging.

### Phase 4 — Reconcile

1. Sum of promoted + flagged + errors at end of run must equal total atom count observed at pre-flight start.
2. If counts do not reconcile, halt and report discrepancy (H5).

### Phase 5 — Report

Write report to `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md`.

---

## Disqualification Rules (D1-D7)

These are defined in `.claude/standards/atom-front-matter.md` v2.0. Reproduced here for operational reference:

| # | Rule | Test |
|---|------|------|
| D1 | Valid YAML frontmatter | File starts with `---`, contains a closing `---`, and the block parses as valid YAML |
| D2 | Has title | `title` field is present and non-empty |
| D3 | Valid type | `type` field is present and value is one of: `concept`, `framework`, `principle`, `connection` |
| D4 | Has source_date | `source_date` field is present and matches `YYYY-MM-DD` format |
| D5 | Has tags (non-connection) | `tags` field is present (may be `[]`). Exempt for `type: connection`. |
| D6 | Connection has from/to | If `type: connection`, both `from` and `to` fields are present and non-empty |
| D7 | Domain matches folder | If `domain` field is present, its value matches the parent folder name |

---

## Soft-Flag Logic

Soft flags are advisory warnings that do not block promotion. An atom that passes all D-rules but triggers soft flags is still promoted, with the `quality_flags` field added to its frontmatter.

| Flag | Trigger condition |
|------|-------------------|
| `missing-when-to-use` | Atom has `## What it is` section but no `## When to use it` section (structured atom with incomplete sections) |
| `body-shorter-than-frontmatter` | Body content (everything after closing `---`) is shorter in character count than the frontmatter block |
| `structured-shell-thin-content` | Atom has 2+ H2 section headings but at least one section body is empty or contains only whitespace |

Soft flags are recorded in the promotion report under a dedicated section. They are informational for manual review, not blockers.

---

## Edge Cases

1. **Domain folder missing in `02-knowledge/`** — Create it before first promotion to that domain. Log creation in the report under "New domain folders created."
2. **Atom with broken YAML or unreadable file** — Classify as error, not flag. Surface in report under "Errors requiring attention." Do not attempt promotion or flagging.
3. **Collision (file exists at destination)** — Halt the entire skill run immediately. Do not continue past the collision. Report which file collided. This indicates a logic error or partial prior run.
4. **Empty staging folder for a domain** — Skip silently. Note in report as "[domain]: 0 atoms staged."
5. **Atom already has skill-written YAML fields (`status: flagged`, `flag_reasons`, or `quality_flags`)** — Re-validate from scratch. Strip any previously-set `status`, `flag_reasons`, and `quality_flags` fields before re-validating. Previous skill annotations do not carry forward. If the atom now passes D1-D7, promote it (with fresh `quality_flags` evaluation).

---

## Output Contract

| Artifact | Location | Content |
|----------|----------|---------|
| Promoted atoms | `02-knowledge/[domain]/[filename]` | Atom files, body unchanged. `quality_flags` added if applicable. |
| Flagged atoms | `00-inbox/staging/framework-atoms/[domain]/[filename]` | Original file with `status: flagged` and `flag_reasons` in YAML front matter |
| Promotion report | `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md` | Per-domain counts, flag reasons, quality flags, errors, reconciliation |

**Out of scope:**
- Does NOT generate `cross_links` automatically
- Does NOT enrich `useful_for` / "When to use it" fields
- Does NOT query NotebookLM
- Does NOT update `02-knowledge/index.md` (flush handles that)
- Does NOT delete flagged atoms

---

## Report Structure

```markdown
# Atom Promotion Report — [YYYY-MM-DD]

## Summary
- Total staged: N
- Promoted: N (Q with quality warnings)
- Flagged: N
- Errors: N
- Reconciliation: PASS / FAIL

## Per-Domain Results
| Domain | Staged | Promoted | Flagged | Errors | Quality Warnings |
|--------|--------|----------|---------|--------|-----------------|

## New Domain Folders Created
- [list or "None"]

## Flagged Atoms
| Domain | File | Flag Reasons |
|--------|------|--------------|

## Quality Warnings
| Domain | File | Flags |
|--------|------|-------|

## Errors Requiring Attention
| Domain | File | Error |
|--------|------|-------|
```

---

## Handoff

After this skill completes, the next stage receives:
- **Artifact:** Promotion report at `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md`
- **Condition:** Reconciliation passes (promoted + flagged + errors = total staged)
- **Routing:** Flagged atoms remain in staging for the remediation skill. Promoted atoms are available for flush/indexing into `02-knowledge/index.md`.
