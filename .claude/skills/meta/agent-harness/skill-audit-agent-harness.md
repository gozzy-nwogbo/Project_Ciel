# Skill Audit: agent-harness
_Evaluated: 2026-04-14 | Standard: skill-authoring v1_

## Verdict: DRAFT

| # | Criterion | Result | Evidence |
|---|---|---|---|
| C1 | Single-Line Description | FAIL | Header is "# Agent Harness Skill" (not "# Skill: agent-harness"). Description at lines 9-11 spans multiple lines. Trigger phrases listed separately at lines 14-23. No single unbroken description line with trigger context and output artifact. |
| C2 | Output Contract | FAIL | Output formats defined per mode (Design lines 138-155, Evaluation lines 176-204, Retrospective lines 221-234) but no unified "Output Contract" section. No "Does NOT produce" declaration. |
| C3 | Input Contract | FAIL | No input table. Design mode asks questions interactively (lines 130-136). Evaluation mode says "Ask the user to provide" (line 164). No formal input contract with named dependencies. |
| C4 | Constraints as Rules | FAIL | "Opinionated Defaults" section (lines 238-249) uses interpretive language: "clear case" (line 241), "Complexity is a cost, not a feature" (line 246), "push back explicitly" (line 247). Not all binary-testable. |
| C5 | Edge Cases Declared | FAIL | No edge cases section exists. |
| C6 | Worked Example Exists | FAIL | No example file in .claude/skills/meta/agent-harness/ folder. Only SKILL.md present. |
| C7 | Core File Under 150 Lines | FAIL | 264 lines (114 over limit). |
| C8 | Handoff Defined | FAIL | "Vault Integration" section (lines 254-264) names output locations per mode but no formal handoff with condition and routing to next stage. |
| C9 | Test Basket Exists | FAIL | No test basket file in folder. |

## Failing Criteria — Required Fixes
1. **C1:** Rename header to "# Skill: agent-harness". Write single unbroken description line with trigger context and output artifact name.
2. **C2:** Add unified Output Contract section with artifact name, path, structure, and "Does NOT produce" declaration.
3. **C3:** Add input table listing all required inputs by name with purposes.
4. **C4:** Rewrite opinionated defaults as binary testable rules. Replace "clear case" with specific criteria.
5. **C5:** Add edge cases section with minimum 3 cases and explicit handling.
6. **C6:** Create worked example file showing one mode applied to real input with expected output.
7. **C7:** Split into core SKILL.md (≤150 lines) and reference files for the 12 primitives detail.
8. **C8:** Add formal Handoff section with artifact, location, condition, and routing.
9. **C9:** Create test basket file with minimum 3 test cases.

## Classification
- **DRAFT (0/9 criteria pass):** Skill is not production-ready. Fix all 9 failing criteria and re-run.
