# Skill Audit: systematic-debugging

**Date:** 2026-04-14

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes what it does, trigger phrases, and names "Root cause diagnosis with regression test" as artifact.

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** — Artifact named in header but no explicit output path, structure, or out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — Phase 1 (Observe) lists questions to gather but no formal input contract stating what the skill requires to begin.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Rules are binary: "Do not touch code in this phase", "Write the hypothesis down before testing it", "Do not fix yet". No hedging language.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** — Common Pitfalls section covers 4 failure modes with handling: fixing symptoms, changing multiple things, skipping observation, not writing regression test.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 67 lines (well under 150).

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — Related Techniques section references other skills but no explicit handoff with artifact, location, or completion condition.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (4/9)
