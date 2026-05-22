# Skill Audit: prd-generator
_Evaluated: 2026-04-16 | Standard: skill-authoring v1_

## Verdict: PASS

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | PASS | Line 3: single unbroken line containing trigger context ("invoke when starting any new project... or when the user says 'I want to build'"), action ("Generates a project planning document"), and output artifact names ("PRD.md or spec-contract.md at 01-projects/[project-name]/") |
| C2 | Output Contract | PASS | Output Contract section (line 19-24) names three artifacts with paths, formats, and conditions. Out of scope explicitly declared: "Implementation planning, phase execution, code generation, skill creation." |
| C3 | Input Contract | PASS | Inputs table (line 9-14) lists 4 inputs, each named with path and purpose. Required/optional marked. No implicit dependencies. |
| C4 | Constraints as Rules | PASS | Constraints table (line 79-87) contains 7 binary constraints, each with a specific verification method. No "should" or "ideally" language. |
| C5 | Edge Cases Declared | PASS | 5 edge cases documented (lines 91-97): wall-of-text input, skip-request refusal, classification disagreement, seed-answers-all, existing-project-folder. Each has explicit handling. |
| C6 | Worked Example Exists | PASS | `example-single-scope.md` exists in folder, shows realistic input (user answers to 6 questions), classification step, and abbreviated spec contract output matching declared contract. |
| C7 | Core File Under 150 Lines | PASS | SKILL.md is 119 lines (verified via wc -l). |
| C8 | Handoff Defined | PASS | Handoff section (lines 101-104) names the artifact ("PRD.md or spec-contract.md"), location ("01-projects/[project-name]/"), and three routing conditions (PRD → phase planning, spec → execution, exploratory → elicitation Mode 2). |
| C9 | Test Basket Exists | PASS | `test-basket.md` exists with 5 test cases, each with defined input, expected classification, expected output, and expected side artifacts. Exceeds minimum of 3. |

## Failing Criteria — Required Fixes
None.

## Classification
- **PASS (all 9 criteria):** Skill is production-ready. Eligible for promotion gate.
