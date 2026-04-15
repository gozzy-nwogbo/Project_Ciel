# Skill Audit: spec-contract
_Evaluated: 2026-04-14 | Standard: skill-authoring v1_

## Verdict: DRAFT

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | FAIL | Header is "# Spec Contract: [Project or Feature Name]" (template placeholder, not skill header). No single-line description with trigger context or output artifact name. File is a template, not a skill. |
| C2 | Output Contract | FAIL | Contains an "Output Contract" section (lines 37-48) but it is a template section for users to fill in, not a declaration of what this skill produces. No "Does NOT produce" declaration. |
| C3 | Input Contract | FAIL | Contains "Explicit Inputs" section (lines 18-29) but as a template for users. No actual input contract for the skill itself. |
| C4 | Constraints as Rules | PASS | Constraints section (lines 53-69) contains binary rules with verification methods. "No 'should,' 'ideally,' 'try to,' or 'where possible'" is explicitly stated. Each constraint requires a verification method. |
| C5 | Edge Cases Declared | FAIL | No edge cases section. Out-of-scope section (lines 73-88) is a template, not declared edge cases. |
| C6 | Worked Example Exists | FAIL | No worked example file in .claude/skills/meta/spec-contract/ folder. |
| C7 | Core File Under 150 Lines | PASS | 139 lines. |
| C8 | Handoff Defined | FAIL | No handoff section. "Consumed By" column in output table is a template field, not a declared handoff. |
| C9 | Test Basket Exists | FAIL | No test basket file in folder. |

## Failing Criteria — Required Fixes
1. **C1:** Convert from template to skill format. Add "# Skill: spec-contract" header with single-line description including trigger context ("before any pipeline stage executes") and output artifact ("approved spec-contract-[name].md").
2. **C2:** Add skill-level output contract declaring what the skill produces (a filled spec contract), its path, and what it does not produce.
3. **C3:** Add skill-level input contract (project brief, PRD section, or feature description as required inputs).
4. **C5:** Add edge cases section (e.g., spec with conflicting constraints, spec with no testable success criteria, spec referencing non-existent dependencies).
5. **C6:** Create worked example showing a completed spec contract for a real feature.
6. **C8:** Add handoff section defining what the next pipeline stage receives.
7. **C9:** Create test basket with minimum 3 spec contract scenarios and expected outcomes.

## Classification
- **DRAFT (2/9 criteria pass):** Skill is not production-ready. Fix 7 failing criteria and re-run.
