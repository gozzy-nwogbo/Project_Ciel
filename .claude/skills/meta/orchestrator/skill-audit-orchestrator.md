# Skill Audit: orchestrator
_Evaluated: 2026-04-14 | Standard: skill-authoring v1_

## Verdict: PASS

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS | Line 3: single unbroken line with trigger context ("trigger at the start of any pipeline run, after any skill completes, or when project state is unclear") and output artifact ("status report... pipeline-status.md") |
| C2 | Output Contract | PASS | Lines 72-77: artifact named ("status report"), path ("inline or pipeline-status.md"), structure (template shown lines 50-68), out-of-scope declared ("Does NOT produce: skill outputs, file modifications, design decisions, written content, or review reports") |
| C3 | Input Contract | PASS | Lines 8-14: table with 3 named inputs (project directory, routing-tables.md, CLAUDE.md), each with purpose |
| C4 | Constraints as Rules | PASS | Lines 80-88: all binary ("deterministic — identical project state... identical routing decision", "checks file existence on disk — never assumes", "never skips a stage", "review with Needs rework routes back") |
| C5 | Edge Cases Declared | PASS | Lines 92-98: 3 edge cases with explicit handling (both pipelines active, incomplete file on disk, review with no handoff status) |
| C6 | Worked Example Exists | PASS | example.md exists with 2 scenarios showing input project state and expected orchestrator output matching declared format |
| C7 | Core File Under 150 Lines | PASS | 106 lines |
| C8 | Handoff Defined | PASS | Lines 103-106: artifact ("status report"), location ("inline or project root"), condition ("all active pipelines evaluated, all routing decisions stated"), routing ("consumed by human operator who invokes recommended skill") |
| C9 | Test Basket Exists | PASS | test-basket.md exists with 4 test cases, each with defined input (files on disk) and expected output (routing decision) |

## Failing Criteria — Required Fixes
None.

## Classification
- **PASS (all 9 criteria):** Skill is production-ready. Eligible for promotion gate.
