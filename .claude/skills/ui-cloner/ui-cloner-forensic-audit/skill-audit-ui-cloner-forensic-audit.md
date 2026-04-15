# Skill Audit: ui-cloner-forensic-audit

**Date:** 2026-04-14

---

## C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes trigger phrases ("forensic audit [URL]", "analyze site DNA", "run phase 1 audit"), output artifact (`plans/01-site-dna.md`), and pipeline step number (Step 1 of 6).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Output artifact is `plans/01-site-dna.md` with `AUDIT_MODE` flag at top. Structure is defined across 9 steps (1.1-1.9) with explicit Standard vs High-Fidelity formats. Out-of-scope is implicit: this phase only produces the Site DNA, does not interview or synthesize.

## C3: Input contract (all inputs named with purposes)
**PASS** — Inputs: target URL (the site to audit), `AUDIT_MODE` flag from `plans/01-site-dna.md` (determines output format: standard vs high-fidelity).

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — Rules are imperative: "you MUST", "BANNED", "DO NOT SKIP", "NEVER reduce". Anti-Flattening Doctrine uses banned examples. No hedging language detected.

## C5: Edge cases declared (3+ with handling instructions)
**PASS** — Edge cases include: (1) Sites without `<section>` tags (fallback to div-based detection with specific JS snippet), (2) Tall sections >2000px (scroll mandate with 500px increments), (3) Orphan classes / mixed component types in sub-section discovery (flag and create sub-section wireframe), (4) Opaque media (Lottie/SVG/canvas) that are invisible to DOM queries (screenshot-based decomposition procedure).

## C6: Worked example file exists in same folder
**FAIL** — No worked example file exists in the skill folder.

## C7: Core file 150 lines or fewer
**FAIL** — Source file is 450 lines. The restructured SKILL.md preserves all content and exceeds 150 lines. (Expected failure per instructions.)

## C8: Handoff defined (specific artifact, location, condition)
**PASS** — "When complete: Invoke ui-cloner-brand-interview to begin Phase 2." Artifact (`plans/01-site-dna.md`) and save location defined.

## C9: Test basket file with 3+ cases exists in folder
**FAIL** — No test basket file exists in the skill folder.

---

## Verdict: DRAFT (6/9 — fails C6, C7, C9)
