# Skill Audit: interface-design

**Date:** 2026-04-14

## Criteria Evaluation

### C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes what it does, trigger phrases, and names ".interface-design/system.md (persisted design system)" as artifact.

### C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Artifact: system.md. Path: .interface-design/system.md. Structure: fully defined in System File Format section (Direction, Tokens, Patterns). Out-of-scope declared: "Not for marketing sites."

### C3: Input contract (all inputs named with purposes)
**FAIL** — Session Start describes two paths (system.md exists vs. not) but no formal input contract listing required inputs (e.g., project directory, design direction preference).

### C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Rules are binary: "Always work on a grid", "State the design choices being applied" before each component, specific values (4px base scale). No hedging.

### C5: Edge cases declared (>=3 with handling instructions)
**PASS** — Covers: existing system.md (load and apply), no system.md (assess and propose), 6 distinct design directions with selection criteria, 3 depth strategies with use cases.

### C6: Worked example file exists in same folder
**FAIL** — No separate example file. System File Format section shows an inline example but not a standalone file.

### C7: Core file <=150 lines
**PASS** — SKILL.md is 117 lines (under 150).

### C8: Handoff defined (specific artifact, location, condition)
**FAIL** — System file is saved to .interface-design/system.md but no explicit handoff condition (when to stop, what to deliver, who receives it).

### C9: Test basket file with >=3 cases exists in folder
**FAIL** — No test basket file exists.

## Verdict: DRAFT (5/9)
