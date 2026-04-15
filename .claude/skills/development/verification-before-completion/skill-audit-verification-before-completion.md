# Skill Audit: verification-before-completion

**Date:** 2026-04-14

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes what it does, trigger phrases, and names "Completed verification checklist (pass/fail per item)" as artifact.

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** — Artifact named in header. Checklist structure is defined inline but no output path or out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — No formal input contract. Implicitly requires a completed fix/implementation but does not list inputs.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Final rule is binary: "Do not declare completion. Fix the issue and run the checklist again." All checklist items are yes/no checkboxes. No hedging.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** — Checklist covers 4 edge case categories: empty/null input, boundary values, concurrent access, service unavailability. Each is a verification item.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 52 lines (well under 150).

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — No explicit handoff. States "do not declare completion" if checks fail, but no artifact/location/condition for successful completion handoff.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (4/9)
