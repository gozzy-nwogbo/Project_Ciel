# Skill Audit: Requesting Code Review

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description names trigger phrases ("review my code", "pre-review check", "ready for review") and output artifact (review request markdown block).

### C2: Output contract (artifact name, path, structure, out-of-scope)
**FAIL** — Review Request Format template defines structure (Changes Summary, Plan Reference, Testing, Concerns). No named file artifact or path. No out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — No formal input contract. Implicit inputs: plan.md, codebase, test results. None are enumerated with required/optional status.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Severity levels have binary actions: Critical = "Stop. Fix before proceeding." Major = "Fix in current session." Minor = "Note for follow-up." All checklist items are binary pass/fail.

### C5: Edge cases declared (>=3 with handling instructions)
**FAIL** — Zero edge cases declared. No handling for: no plan exists, partial implementation, tests are flaky, security checklist not applicable.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 64 lines.

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — Review Request Format is the output but no explicit handoff to a next skill or action. Does not define what happens after review is requested.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (3/9 PASS)
