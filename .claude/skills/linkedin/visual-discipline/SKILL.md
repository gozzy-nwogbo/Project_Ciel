---
name: linkedin-visual-discipline
description: Use when rendering or reviewing LinkedIn post visuals (atom-graph diagrams, carousels, video). Enforces brand-spec consultation and anti-pattern checks. Triggers on `render visual`, `tier 1 diagram`, `review carousel`, `visual brief`, LinkedIn post bundle preparation.
when_to_use: Before any visual asset is committed to a LinkedIn post bundle. Also when reviewing an existing bundle for ship-readiness.
allowed-tools: Read, Bash, Glob
version: 1.0
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
2. **Validate brief against tier rules:**
   - Tier 1: ≤3 distilled atom blocks (4+ atoms apply overflow rule); non-empty thesis (extracted from `<THESIS>` or first-sentence fallback); `tldr` resolved for each shown atom (front-matter or LLM fill succeeded); source slug present in footer; aspect ratio 1:1.
   - Tier 2: ≤8 slides, ≤50 words/slide, ≤9 augmented images.
   - Tier 3: ≤12 total asset refs, ≤15s duration, 720p, body text always present.
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

## Anti-patterns (these are deterministic, not aesthetic preferences)

| Check | Why it matters |
|---|---|
| No center-radial-gradient | Generic AI aesthetic; instantly readable as generated |
| No drop shadows on nodes | Adds visual noise without information |
| No all-caps body labels | Reads as marketing-deck, not analytical |
| ≤3 distilled atoms per card | Cognitive load on a 1:1 LinkedIn feed image |
| Non-empty thesis | Card needs a hero line for scroll-stop |
| Source slug in footer | "Visible system" payload must be present |
| Aspect ratio 1:1 | LinkedIn-feed display optimization |

## Examples

### Example 1 — Tier 1 atom-card approval

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

### Example 2 — Tier 1 rejection (empty thesis)

Input: brief with 3 atoms but `brief.thesis == ""` (extraction fell back to empty, body had no usable first sentence).

Process:
1. Validate: thesis empty → FAIL.
2. Return validation error before invoking renderer.

Output: error surfaced to user; renderer not invoked; bundle stays in gate1_approved with a logged warning.

## Output contract

- On success: bundle directory contains the visual asset(s) and `visual-checks.json`.
- On failure: clear error message naming the failed check; renderer not invoked; bundle remains in pre-render state.
