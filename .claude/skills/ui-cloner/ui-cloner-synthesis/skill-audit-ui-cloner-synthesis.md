# Skill Audit: ui-cloner-synthesis

**Date:** 2026-04-14

---

## C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes trigger phrases ("synthesize replication prompt", "run phase 3", "generate build prompt"), output artifact (`plans/03-replication-prompt.md`), and pipeline step number (Step 3 of 6).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Output is `plans/03-replication-prompt.md`. Structure defined via Rule 1 (5-section hierarchy: Role + Aesthetic Identity, Core Design System, Component Architecture, Technical Requirements, Execution Directive). Out-of-scope: does not verify quality (that is Phase 4).

## C3: Input contract (all inputs named with purposes)
**PASS** — Inputs: `plans/01-site-dna.md` (design tokens, wireframes, timelines, state machines), `plans/02-brand-interview.md` (12 user answers for brand adaptation), `AUDIT_MODE` flag (determines Standard vs High-Fidelity processing).

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — All 11 rules are imperative: "MUST CONTAIN", "Do NOT convert", "Flattening is banned", "Never randomly reassign", "MUST be an italicized or quoted philosophical directive". No hedging language.

## C5: Edge cases declared (3+ with handling instructions)
**PASS** — Edge cases: (1) Standard vs High-Fidelity mode branching (Rules 2 vs 4-5), (2) Animation intensity scaling across 5 levels (Rule 9 with specific actions per level), (3) KEEP AS-IS vs ADAPT vs REMOVE section handling (Rule 2b), (4) Opaque media composition preservation.

## C6: Worked example file exists in same folder
**FAIL** — No worked example file exists in the skill folder.

## C7: Core file 150 lines or fewer
**FAIL** — Source is 172 lines, exceeds 150-line limit. (Expected failure per instructions.)

## C8: Handoff defined (specific artifact, location, condition)
**PASS** — "When complete: Invoke ui-cloner-quality-check to run Phase 4 before delivery." Artifact and save location defined.

## C9: Test basket file with 3+ cases exists in folder
**FAIL** — No test basket file exists in the skill folder.

---

## Verdict: DRAFT (6/9 — fails C6, C7, C9)
