# Skill Audit: webapp-testing

**Date:** 2026-04-14

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes what it does, trigger phrases, and names "Test results with screenshots (screenshot.png, failure.png)" as artifact.

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** — Artifact names listed (screenshot.png, failure.png). Test file structure shown (tests/test_homepage.py) but no formal out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — No formal input contract. Implicitly requires a running local web app URL but does not list required inputs.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Instructions are imperative: "Install Playwright if not present", specific code patterns to follow. No hedging language.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** — Covers: async content (wait_for_load_state), console errors (error listener pattern), element not found (failure screenshot + re-raise), form submission with redirect.

### C6: Worked example file exists in same folder
**FAIL** — No separate example file. Inline examples exist but not as a standalone worked example file.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 135 lines (under 150).

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — No explicit handoff section. Test results and screenshots are produced but no defined handoff artifact, location, or condition.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (4/9)
