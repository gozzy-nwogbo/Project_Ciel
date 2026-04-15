# Skill Audit: ui-cloner-iterator

**Date:** 2026-04-14

---

## C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes trigger phrases ("iterate on build", "run refinement loop", "compare against site DNA"), output artifact (`plans/05-iterator.md`), and pipeline step number (Step 5 of 6).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Output is `plans/05-iterator.md` containing all 5 passes (each with Gaps Identified + Corrective Prompt) plus a Master Correction Summary. Structure defined with explicit per-pass format template.

## C3: Input contract (all inputs named with purposes)
**PASS** — Inputs: `plans/01-site-dna.md` (reference for comparison), current implementation (screenshot, URL, or code showing what was built). Missing input handling defined: "ask for it before proceeding."

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — "Never skip a pass." "Each corrective prompt must be self-contained." "Do not re-audit already-corrected gaps." "Use Claude with chrome for visual checking MANDATORY." All binary and testable.

## C5: Edge cases declared (3+ with handling instructions)
**PASS** — Edge cases: (1) Missing Site DNA (ask before proceeding), (2) Missing implementation screenshot/URL (ask before proceeding), (3) Implementation looks good but later passes still run (never skip), (4) Previously corrected gaps (do not re-audit).

## C6: Worked example file exists in same folder
**FAIL** — No worked example file exists in the skill folder.

## C7: Core file 150 lines or fewer
**PASS** — Source is 127 lines, under the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**PASS** — Final output saved to `plans/05-iterator.md`. Master Correction Summary provides consolidated "Final Dial-In Prompt" as the terminal handoff artifact.

## C9: Test basket file with 3+ cases exists in folder
**FAIL** — No test basket file exists in the skill folder.

---

## Verdict: DRAFT (7/9 — fails C6, C9)
