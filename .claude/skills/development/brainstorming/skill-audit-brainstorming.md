# Skill Audit: Brainstorming

**Date:** 2026-04-14
**Auditor:** Phase 5 Track A migration

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block names trigger phrases ("I want to build...", "let's brainstorm", "help me design", "before we code") and output artifact (`design.md`).

### C2: Output contract (artifact name, path, structure, out-of-scope)
**FAIL** — Artifact name is `design.md` and structure is defined via template. Path is "in the project" but not a specific path. No explicit out-of-scope declaration for the output.

### C3: Input contract (all inputs named with purposes)
**FAIL** — No formal input contract. The skill assumes a rough idea from the user but does not enumerate required vs. optional inputs.

### C4: Constraints as binary testable rules (no "should"/"ideally")
**FAIL** — "Avoid overwhelming with a list of 10 questions at once" is not binary testable. No hard numeric constraints on question count per turn.

### C5: Edge cases declared (>=3 with handling instructions)
**FAIL** — Zero edge cases declared. No handling for: user already has a design, user wants to skip brainstorming, conflicting requirements, overly broad scope.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 73 lines.

### C8: Handoff defined (specific artifact, location, condition)
**PASS** — Handoff section specifies: save `design.md` to project, signal `writing-plans` skill, plan references design doc.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (3/9 PASS)
