# Skill Audit: ui-cloner

**Date:** 2026-04-14

---

## C1: Single-line description with trigger context + output artifact named
**PASS** — Description block includes trigger phrases ("clone this site", "replicate this UI", "ui cloner [URL]"), output artifact (`plans/` directory with all phase outputs), and pipeline step number (Step 4, entry point).

## C2: Output contract (artifact name, path, structure, out-of-scope declared)
**PASS** — Output directory `plans/` with 5 named artifacts (01-site-dna.md through 05-iterator.md). Structure defined. This skill orchestrates; it does not produce content directly (delegated to phase skills).

## C3: Input contract (all inputs named with purposes)
**PASS** — Inputs: target URL (site to clone), audit mode selection (Standard vs High-Fidelity, determines output precision).

## C4: Constraints as binary testable rules (no "should"/"ideally")
**PASS** — "Run the 4 phases in strict order." "Do not ask any other clarifying questions first." "When given a URL, ask for audit mode selection, then immediately invoke." Binary and testable.

## C5: Edge cases declared (3+ with handling instructions)
**FAIL** — Only covers: (1) Standard vs High-Fidelity mode selection, (2) Post-pipeline refinement via iterator. Does not cover: invalid URL, user providing multiple URLs, user wanting partial pipeline run, resuming a partially completed pipeline.

## C6: Worked example file exists in same folder
**FAIL** — No worked example file exists in the skill folder.

## C7: Core file 150 lines or fewer
**PASS** — Source is 58 lines, well under the 150-line limit.

## C8: Handoff defined (specific artifact, location, condition)
**PASS** — Handoff to ui-cloner-forensic-audit after mode selection. Post-pipeline handoff to ui-cloner-iterator if build attempt is poor.

## C9: Test basket file with 3+ cases exists in folder
**FAIL** — No test basket file exists in the skill folder.

---

## Verdict: DRAFT (6/9 — fails C5, C6, C9)
