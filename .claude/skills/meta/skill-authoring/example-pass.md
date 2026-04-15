# Worked Example — PASS

This example shows the skill-authoring meta-skill evaluating a hypothetical skill (`format-check`) that passes all nine criteria.

---

## The Skill Being Evaluated

**File:** `/skills/format-check/SKILL.md` (42 lines)

```markdown
# Skill: format-check

Validates that any markdown file conforms to the project formatting standard — trigger when a pipeline stage produces a .md output file, returns a format-audit-[filename].md report listing every violation with line numbers.

---

## Inputs

| Input | Required | Description |
|---|---|---|
| The target .md file | Yes | The file being validated |
| `/shared/format-rules.md` | Yes | The formatting standard rules |

## Output Contract

**Produces:** `format-audit-[filename].md` in the same directory as the target file.
**Structure:** Table of violations with line number, rule ID, and violation description.
**Does NOT produce:** Fixed files, prose summaries, or style suggestions beyond the declared rules.

## Constraints

- Every rule in format-rules.md is evaluated. No rule is skipped.
- Each violation cites the exact line number. "Somewhere in the file" is not a citation.
- A file with zero violations gets a CLEAN report, not an empty file.

## Edge Cases

1. **Empty file:** Report CLEAN with note: "File is empty — 0 lines evaluated."
2. **File contains only frontmatter:** Evaluate frontmatter formatting rules only. Do not flag absence of body content — that is not a formatting violation.
3. **Rule in format-rules.md is ambiguous:** Flag the ambiguous rule in the report under a "## Rule Ambiguities" section. Do not skip the rule.

## Handoff

- **Artifact:** `format-audit-[filename].md` at the target file's directory
- **Condition:** Audit is complete when every rule has been evaluated against every line
- **Routing:** If violations exist, return to the author of the target file. If CLEAN, target file proceeds to the next pipeline stage.
```

**Folder also contains:**
- `example-usage.md` — shows format-check run against a sample file with 3 violations and the resulting audit report
- `test-basket.md` — 4 test cases: clean file, file with heading violations, file with link formatting errors, empty file

---

## The Audit Report

```markdown
# Skill Audit: format-check
_Evaluated: 2026-03-31 | Standard: skill-authoring v1_

## Verdict: PASS

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS | Line 3 is a single unbroken line containing trigger ("when a pipeline stage produces a .md output file") and output artifact ("format-audit-[filename].md report") |
| C2 | Output Contract | PASS | Output Contract section names artifact (format-audit-[filename].md), path (same directory as target), structure (table of violations), and out-of-scope ("Does NOT produce: fixed files, prose summaries, or style suggestions") |
| C3 | Input Contract | PASS | Inputs table lists two required inputs with names and descriptions. No implicit dependencies. |
| C4 | Constraints as Rules | PASS | Three constraints, all binary: every rule evaluated (true/false), line numbers cited (present/absent), clean report for zero violations (exists/doesn't) |
| C5 | Edge Cases Declared | PASS | Three edge cases with explicit handling: empty file, frontmatter-only, ambiguous rule. Each has a specific instruction. |
| C6 | Worked Example Exists | PASS | `example-usage.md` exists in folder, shows input file and resulting audit output matching declared format |
| C7 | Core File Under 150 Lines | PASS | 42 lines |
| C8 | Handoff Defined | PASS | Handoff section names artifact, location, completion condition, and routing for both violation and clean outcomes |
| C9 | Test Basket Exists | PASS | `test-basket.md` contains 4 test cases (>= 3), each with defined input and expected output |

## Failing Criteria — Required Fixes
None.

## Classification
PASS — Skill is production-ready. Eligible for promotion gate.
```
