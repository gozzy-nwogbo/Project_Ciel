---
name: linkedin-visual-discipline
description: Use when rendering or reviewing LinkedIn post visuals (atom-graph diagrams, carousels, video). Enforces brand-spec consultation and anti-pattern checks. Triggers on `render visual`, `tier 1 diagram`, `review carousel`, `visual brief`, LinkedIn post bundle preparation.
when_to_use: Before any visual asset is committed to a LinkedIn post bundle. Also when reviewing an existing bundle for ship-readiness.
allowed-tools: Read, Bash, Glob
version: 1.2
scope: project
---

# LinkedIn Visual Discipline

## Purpose

Enforces visual quality discipline across LinkedIn post bundles. Two responsibilities:

1. **Brand-spec consultation.** No visual is allowed to drift from `01-projects/linkedin/brand-spec.md`. If the brand-spec changes, all subsequent renders adopt the change automatically.
2. **Anti-pattern enforcement.** Deterministic checks that block ship-readiness when violated.

## Trigger conditions

Fire automatically when:
- A renderer is about to write a visual asset to a backlog bundle.
- A `gate2_pending` bundle is being reviewed.
- User says "render the diagram", "make the carousel", "review the bundle".

## Required inputs

- `brief`: a PostBrief object (or its meta.json on disk).
- `brand_spec_path`: path to brand-spec.md (default: `01-projects/linkedin/brand-spec.md`).
- `bundle_dir`: target output directory.

## Protocol

1. **Load brand-spec.** Parse the YAML block. If missing or unparseable, halt and surface error.
2. **Validate brief against tier rules (strategy-keyed for Tier 1 as of v1.2):**

   **Tier 1 · `source_spotlight`:**
   - ≤3 distilled atom blocks (4+ atoms apply overflow rule)
   - non-empty thesis (extracted from `<THESIS>` or first-sentence fallback)
   - `tldr` resolved for each shown atom (front-matter or LLM fill succeeded)
   - source slug present in footer
   - aspect ratio 1:1
   - brand tokens loaded from `brand-spec.md` (no hardcoded colors in template)

   **Tier 1 · `two_atom_bridge` (v1.2):**
   - exactly 2 atom pillars
   - atoms in different domains (strategy enforces this)
   - non-empty thesis
   - non-empty `panel_label` (derived from `_LABEL_BY_CONNECTION_TYPE`)
   - non-empty `panel_claim` (from `<CLAIM>` tag or fallback to connection edge claim)
   - `tldr` resolved per pillar
   - aspect ratio 4:5
   - mechanism band uses dashed terracotta border + italic claim

   **Tier 1 · `convergence_finder` (v1.2):**
   - 3 funnel atoms (truncate at 3 if strategy emits more)
   - ≥3 distinct domains across atoms
   - non-empty thesis
   - non-empty `panel_label` (composed as `CONVERGES ON · {topic}`)
   - non-empty `panel_claim` (from `<CLAIM>` tag or fallback to angle)
   - `tldr` resolved per atom
   - aspect ratio 4:5
   - convergence panel uses solid terracotta border + italic claim

   **Tier 2:** ≤8 slides, ≤50 words/slide, ≤9 augmented images.

   **Tier 3:** ≤12 total asset refs, ≤15s duration, 720p, body text always present.
3. **Run anti-pattern checks:**
   - No center-radial-gradient backgrounds.
   - No drop shadows on graph nodes.
   - No all-caps body labels.
4. **Invoke renderer.** Pass brand tokens explicitly; renderer must not invent colors or fonts.
5. **Post-render verification.**
   - Output file(s) exist and are non-empty.
   - PNG dimensions match declared aspect ratio.
   - For tier 1: SVG also produced alongside PNG.
6. **Annotate bundle.** Write `01-projects/linkedin/backlog/<slug>/visual-checks.json` with check results.

## Anti-patterns (shared across all Tier 1 strategies)

These are deterministic blockers regardless of which Tier 1 template renders. Strategy-specific rules (atom counts, thesis presence, aspect ratio) now live in the per-strategy tier rules above.

| Check | Why it matters |
|---|---|
| No center-radial-gradient backgrounds | Generic AI aesthetic; instantly readable as generated |
| No drop shadows on atom cards or panels | Adds visual noise without information |
| No all-caps body text | Reads as marketing-deck, not analytical (labels in the band/panel are allowed; tldr text is not) |

## Examples

### Example 1: Tier 1 atom-card approval (source_spotlight)

Input: `brief` with 3 atoms (each with `tldr` in front-matter), thesis="Strategy is problem-shaped, not goal-shaped.", visual_tier=1_diagram.
Brand-spec: terracotta accent, Geist font.

Process:
1. Load brand-spec → confirm `colors.accent_primary` exists.
2. Validate: 3 atoms ≤ 3 ✓, thesis non-empty ✓, all atoms have tldr ✓, source slug present ✓, aspect 1:1 ✓.
3. Anti-patterns: no shadows used ✓, labels mixed-case ✓.
4. Renderer outputs PNG.
5. Verify file exists, PNG is 1080×1080 px.
6. Write checks file.

Output: `visual-checks.json` with `{"passed": true, "checks": [...]}`.

### Example 2: Tier 1 rejection (empty thesis)

Input: brief with 3 atoms but `brief.thesis == ""` (extraction fell back to empty, body had no usable first sentence).

Process:
1. Validate: thesis empty → FAIL.
2. Return validation error before invoking renderer.

Output: error surfaced to user; renderer not invoked; bundle stays in gate1_approved with a logged warning.

## Output contract

- On success: bundle directory contains the visual asset(s) and `visual-checks.json`.
- On failure: clear error message naming the failed check; renderer not invoked; bundle remains in pre-render state.
