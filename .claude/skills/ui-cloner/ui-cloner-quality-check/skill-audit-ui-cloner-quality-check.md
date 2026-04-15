# Skill Audit: ui-cloner-quality-check

**Date:** 2026-04-14

---

## C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes trigger phrases ("quality check prompt", "run phase 4", "verify replication prompt"), output artifact (`plans/04-final-prompt.md`), and pipeline step number (Step 6 of 6).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Output is `plans/04-final-prompt.md` (the verified final prompt). Structure: verified prompt delivered in a fenced code block. Out-of-scope: does not build the site, only verifies the prompt's completeness.

## C3: Input contract (all inputs named with purposes)
**PASS** — Inputs: `plans/03-replication-prompt.md` (the generated prompt to verify), `plans/01-site-dna.md` (for AUDIT_MODE flag and reference data for gap-filling).

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — All checklist items are binary (checked/unchecked). Generic language table provides exact replacement patterns. "Do not deliver until all applicable items are checked." No hedging.

## C5: Edge cases declared (3+ with handling instructions)
**PASS** — Edge cases: (1) Standard vs High-Fidelity mode branching (different checklist scope), (2) Missing items trigger Failure Protocol (identify, generate, insert, re-check), (3) Generic language detected (specific replacement table with 8+ patterns), (4) Flattened descriptions (6 additional banned patterns with required replacements).

## C6: Worked example file exists in same folder
**FAIL** — No worked example file exists in the skill folder.

## C7: Core file 150 lines or fewer
**PASS** — Source is 113 lines, under the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**PASS** — Delivery is the terminal step: save to `plans/04-final-prompt.md`, output in fenced code block, confirm completion message. No downstream handoff needed (this is the final pipeline step).

## C9: Test basket file with 3+ cases exists in folder
**FAIL** — No test basket file exists in the skill folder.

---

## Verdict: DRAFT (7/9 — fails C6, C9)
