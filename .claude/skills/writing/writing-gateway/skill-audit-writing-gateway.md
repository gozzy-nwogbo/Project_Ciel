# Skill Audit: writing-gateway
_Evaluated: 2026-04-14 | Standard: skill-authoring v1_

## Verdict: DRAFT

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS | Single unbroken line after `# Skill:` header contains trigger context ("any writing request"), both output artifacts named ("finished draft" and "writing-brief-[title]-[date].md") |
| C2 | Output Contract | PASS | Output Contract section names both artifacts, paths (`00-inbox/staging/writing-brief-[title]-[date].md` for deep, in-session for quick), structure (7 required fields for brief), and explicit out-of-scope declarations |
| C3 | Input Contract | PASS | Inputs table lists 3 named inputs (voice-profile.md, platform-rules.md, user request) with exact paths and purposes |
| C4 | Constraints as Rules | PASS | All 7 constraints are binary-testable: "always Personal" (check for non-Personal), "never embedded inline" (search for embedded content), em-dash prohibition (character search), exclamation point count (word count ratio), etc. |
| C5 | Edge Cases Declared | PASS | 5 edge cases documented with explicit handling instructions: short article with no research, LinkedIn requiring research, unknown platform, unspecified format, revision reclassification |
| C6 | Worked Example Exists | FAIL | No example file exists in `.claude/skills/writing/writing-gateway/`. Only SKILL.md is present in the folder. |
| C7 | Core File Under 150 Lines | PASS | SKILL.md is 137 lines (under 150 limit) |
| C8 | Handoff Defined | PASS | Handoff section names artifacts for both paths, locations (in-session for quick, file path for deep), and conditions (calibration test passed for quick, 7 fields populated for deep) |
| C9 | Test Basket Exists | FAIL | No test basket file exists in or alongside the skill folder |

## Failing Criteria — Required Fixes

**C6 — Worked Example Exists:**
Create an example file (e.g., `example-quick-write.md`) in `.claude/skills/writing/writing-gateway/` that shows the skill applied to a realistic input (e.g., "write a LinkedIn post about building AI infrastructure") and producing the declared output (a finished draft that passed the voice calibration test). Must match the skill's quick write output contract.

**C9 — Test Basket Exists:**
Create a test basket file (e.g., `test-basket.md`) in `.claude/skills/writing/writing-gateway/` with a minimum of 3 test cases. Each case must have: (1) a defined input (user request), (2) expected classification (quick or deep), (3) expected output type (in-session draft or writing brief file), and (4) key properties to verify in the output. Suggested cases: a LinkedIn post (quick), an article requiring vault research (deep), an email with no platform specified (edge case requiring clarification).

## Classification
- **DRAFT (2 failures):** Skill is not production-ready. Fix C6 and C9, then re-run audit.