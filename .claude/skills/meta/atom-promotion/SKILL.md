# Skill: atom-promotion

Validates knowledge atoms in `00-inbox/staging/framework-atoms/[domain]/` against the atom front-matter standard, promotes passing atoms to `02-knowledge/[domain]/`, and flags failing atoms in place -- invoke when staging atoms are ready for promotion, produces a promotion report at `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md`.

---

## When to Trigger

- Staging atoms exist in `00-inbox/staging/framework-atoms/` and are ready for promotion
- After a notebook-builder run populates staging with new atoms
- Periodic quality gate before knowledge layer grows stale

Do NOT trigger as part of remediation. Remediation is a separate skill.

---

## Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Staging directory | Yes | `00-inbox/staging/framework-atoms/` containing domain subfolders |
| Front-matter standard | Yes | `.claude/standards/atom-front-matter.md` (D1-D10 rules) |
| Target directory | Yes | `02-knowledge/` where promoted atoms land |
| Domain filter | No | Single domain name to run on one domain only (default: all) |

---

## Constraints

| # | Rule | Binary test |
|---|------|-------------|
| H1 | Never delete a staging atom without first writing it to its destination | Copy to destination verified before source removal |
| H2 | Never promote an atom that fails any disqualification rule (D1-D10) | All 10 rules pass = promote; any fail = flag |
| H3 | Never write to `02-knowledge/` if the file already exists at the destination | Halt entire run and report collision |
| H4 | Never modify atom body content during promotion | Only YAML front matter (`status` field) may be added |
| H5 | Never proceed past verification if file counts do not reconcile | promoted + flagged + errors = total staged |
| H6 | Approval-first on first run | After pre-flight, propose summary and wait for explicit "yes" |

---

## Procedure

### Phase 1 — Pre-flight
1. Scan all domain folders in staging. Count atoms per domain.
2. For each atom, run D1-D10 validation. Classify as `pass`, `flag`, or `error`.
3. Check every passing atom's destination path for collisions (H3).
4. Produce an in-memory classification list: atom path, verdict (pass/flag/error), and reasons. Phases 2-3 read from this list. Do not re-validate in later phases. Single classification per run.
5. Present summary: "About to promote N atoms across M domains. K will be flagged. E have errors. Proceed?"
6. Wait for explicit approval before any file writes.

### Phase 2 — Promote
For each passing atom, in alphabetical order by domain then filename:
1. Create domain folder in `02-knowledge/` if it does not exist.
2. Copy atom file to `02-knowledge/[domain]/[filename]`.
3. Verify destination file exists and content matches source.
4. Remove source file from staging.

### Phase 3 — Flag
For each failing atom:
1. Set YAML front matter on the file in place (in staging). If the file already has a `---` front matter block, replace it entirely. Do not append a second block. The atom must end the run with exactly one YAML front matter block at the top.
   ```yaml
   ---
   status: flagged
   flag_reasons:
     - "D2: missing domain field"
   ---
   ```
2. Do not move the file. It stays in staging.

### Phase 4 — Reconcile
1. Sum of promoted + flagged + errors at end of run must equal total atom count observed at pre-flight start.
2. If counts do not reconcile, halt and report discrepancy (H5).

### Phase 5 — Report
Write report to `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md`.

---

## Edge Cases

1. **Domain folder missing in `02-knowledge/`** — Create it before first promotion to that domain. Log creation in the report under "New domain folders created."
2. **Atom with broken YAML or unreadable file** — Classify as error, not flag. Surface in report under "Errors requiring attention." Do not attempt promotion or flagging.
3. **Collision (file exists at destination)** — Halt the entire skill run immediately. Do not continue past the collision. Report which file collided. This indicates a logic error or partial prior run.
4. **Empty staging folder for a domain** — Skip silently. Note in report as "[domain]: 0 atoms staged."
5. **Atom already has YAML front matter with `status: flagged`** — Re-validate from scratch. Previous flag status does not carry forward. If it now passes, promote it.

---

## Output Contract

| Artifact | Location | Content |
|----------|----------|---------|
| Promoted atoms | `02-knowledge/[domain]/[filename]` | Atom files, body unchanged |
| Flagged atoms | `00-inbox/staging/framework-atoms/[domain]/[filename]` | Original file with YAML front matter added |
| Promotion report | `01-projects/open-brain/reports/atom-promotion-[YYYY-MM-DD].md` | Per-domain counts, flag reasons, errors, reconciliation |

**Out of scope:**
- Does NOT generate `cross_links` automatically
- Does NOT enrich `useful_for` / "When to use it" fields
- Does NOT query NotebookLM
- Does NOT update `02-knowledge/index.md` (flush handles that)
- Does NOT delete flagged atoms
- Does NOT update `notebook-registry.md` (Task 5 handles that separately)

---

## Report Structure

```markdown
# Atom Promotion Report — [YYYY-MM-DD]

## Summary
- Total staged: N
- Promoted: N
- Flagged: N
- Errors: N
- Reconciliation: PASS / FAIL

## Per-Domain Results
| Domain | Staged | Promoted | Flagged | Errors |
|--------|--------|----------|---------|--------|

## New Domain Folders Created
- [list or "None"]

## Flagged Atoms
| Domain | File | Flag Reasons |
|--------|------|--------------|

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
