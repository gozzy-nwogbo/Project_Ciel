# Skill Audit: test-driven-development

**Date:** 2026-04-14

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes what it does, trigger phrases, and names "Passing test suite with implementation code" as artifact.

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**FAIL** — Artifact named in header but no explicit output path, structure format, or out-of-scope declaration.

### C3: Input contract (all inputs named with purposes)
**FAIL** — "When to Use" lists scenarios but no formal input contract (e.g., requires feature spec, file path, language).

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Rules are binary: "Never write implementation before a test", "One failing test at a time", "Commit after each GREEN". No hedging.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** — Anti-Patterns section covers 5 edge cases with handling: writing all tests upfront, testing implementation details, mocking everything, skipping refactor, writing tests after the fact.

### C6: Worked example file exists in same folder
**FAIL** — No example file exists. The Arrange-Act-Assert snippet is inline but not a separate worked example file.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 70 lines (well under 150).

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — Integration section references other skills but no explicit handoff with artifact, location, or completion condition.

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (4/9)
