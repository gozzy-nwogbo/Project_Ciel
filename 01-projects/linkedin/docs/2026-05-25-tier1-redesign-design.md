# LinkedIn Engine v1.1 — Tier 1 Redesign + Cold-Reader Anchor v2

**Date:** 2026-05-25
**Version:** v1.1 (design)
**Status:** Approved (brainstorm), pending planning
**Owner:** nwogbo_gozzy
**Supersedes:** §5.1 of `2026-05-24-linkedin-engine-design.md` (Tier 1 atom-graph diagram)
**Precedes:** `2026-05-25-v1-1-implementation-plan.md` (to be written)

---

## Executive summary

Replace the v1.0 graphviz network-diagram renderer with an HTML/CSS atom-card renderer that pairs a thesis line with per-atom evidence and a source trace. Bundle with a voice-prompt update that makes the cold-reader anchor rule source-type-aware (book authors get a full bio sentence; video/podcast voices get the existing 3-5 word anchor). New data model: atom front-matter v2.2 adds an optional `tldr` field; a sources registry holds author bios and source types. The redesign converts the v1.0 smoke-test failure modes (3 floating ovals, "broken-looking" diagrams) into a template that ships shareable visuals on the same atoms.

---

## 1. Why now

The v1.0.2 smoke test surfaced two related failures that converged on the same root cause: the visual was visualizing the wrong thing.

1. **3-floating-ovals failure.** `source_spotlight` picked three Rumelt atoms with no inter-atom connection edges; the graphviz renderer drew three isolated nodes. v1.0.1 patched this with an edgeless guard that skips rendering, so today these posts ship text-only.
2. **Two-atom bridge thinness.** v1.0.2 defaulted `two_atom_bridge` to text-only after a 2-node graphviz render was confirmed to add no information the sentence already carried.

Both failures came from a strategic mismatch: "atom-graph diagram" assumed atoms in a post would have inter-atom edges in the vault, but most posts pull atoms that share a source or domain, not a connection. The visual was designed for the rare case (synthesis from typed connections) and broke on the common case (synthesis from co-source or co-domain).

This redesign accepts that **the post's pattern is in the synthesis, not in the vault graph topology.** The visual surfaces the synthesis (thesis) and the evidence (per-atom distillations) directly, with a small system-trace footer that keeps "visible system" positioning intact.

---

## 2. Visual template (Variant B)

### 2.1 Layout

```
┌──────────────────────────────────────────┐
│  FROM SECOND BRAIN          domain//tag  │  ← meta row (11px, terracotta + mono gray)
│                                          │
│  Strategy is problem-shaped,             │  ← thesis (28-32px, dark gray, -0.01em tracking)
│  not goal-shaped.                        │
│                                          │
│  ● Kernel of Good Strategy               │  ← atom block × 1-3
│    Diagnosis first. Then policy.         │
│                                          │
│  ● Proximate Objectives                  │
│    Pick a target close enough to solve.  │
│                                          │
│  ● Problem-Solution Tool                 │
│    Reverse-engineer policy to diagnosis. │
│                                          │
│  richard-rumelt, 2011    3 atoms · …     │  ← footer row (11px, mono, gray)
└──────────────────────────────────────────┘
```

- Canvas: **1080×1080 (1:1)** in v1.1. 4:5 deferred.
- Padding: 36px top/bottom, 34px left/right.
- Typography: all text uses `body` font from brand-spec (Geist, falling back to system-ui). Monospace where noted uses `mono` from brand-spec (Geist Mono fallback).
- Meta row: `from second brain` (11px, color `accent_primary`, uppercase, letter-spacing 0.1em) + domain tag (11px, color `text_secondary`, monospace).
- Thesis: 28-32px Geist, weight 500, line-height 1.1, letter-spacing -0.01em, color `text_primary`. Final size locked in planning based on character-count testing.
- Atom block: terracotta dot (6px circle, color `accent_primary`), atom name (13px, weight 600, color `text_primary`), distillation on next line (13px, weight 400, color `text_secondary`, line-height 1.4, indent 14px under name).
- Block spacing: 14px between atom blocks. **No dividers, no borders, no arrows.**
- Footer row: source slug left-aligned (11px, monospace, color `text_primary`); atom count + scope tag right-aligned (11px, monospace, color `text_secondary`).
- Card border: 1px solid `border` (#E8E4DF), border-radius 4px, background `background` (#FAF8F5).

### 2.2 Overflow rule (4+ atoms)

Tier 1 hard-caps at **3 distilled atom blocks.** When `len(brief.atoms_used) > 3`:

- First 3 atoms render as normal atom blocks.
- A single overflow line replaces atom block 4+: `+ N more atoms inside the post · slug-4, slug-5, …` (11px, monospace, color `accent_primary`, letter-spacing 0.05em).
- The overflow line appears as the 4th block in the same vertical rhythm — no separator.
- All atom slugs (including the omitted ones) remain in `brief.atoms_used`; only the visual is truncated.

`cluster_reveal` (which intentionally walks 4+ atoms) defaults to Tier 2 carousel in v1.2 — it should not fall back to truncated Tier 1.

### 2.3 Single-atom case

Same template, one atom block, terracotta dot, thesis still extracted from body. No special variant needed.

### 2.4 Aspect ratio

1:1 only in v1.1. 4:5 (1080×1350) deferred to a later phase. The brand spec's `aspect_ratios: ["1:1", "4:5"]` stays declared but only 1:1 is implemented.

### 2.5 Brand tokens (inherited)

All tokens read from `01-projects/linkedin/brand-spec.md`. No tokens defined inside the renderer code. If the brand spec evolves, the renderer adopts the new tokens on next render.

---

## 3. Data model changes

### 3.1 Atom front-matter v2.2

Add one optional field to atom front-matter:

```yaml
---
title: Kernel of Good Strategy
type: concept
source: Richard Rumelt, 2011
domain: strategy
tags: [strategy, decision-making]
tldr: Diagnosis first. Then policy. Then coherent action.   # ← NEW, optional
---
```

(`connection_type` from atom v2.1 stays optional on connection atoms only; not shown here since it's irrelevant to v2.2.)

- **Field:** `tldr`
- **Type:** single sentence string, soft cap ~80 characters
- **Optional:** yes; missing tldr triggers the LLM-fill fallback
- **Audience:** the cold reader who has never seen this atom; should stand alone

v2.2 is backwards-compatible: atoms without `tldr` continue to load. The LLM fallback (§3.4) handles missing tldr for atoms used in posts; back-writes the result so the atom is "completed" by use.

### 3.2 Sources registry

New file: `01-projects/linkedin/sources.yml` (engine-scoped).

```yaml
"Richard Rumelt, 2011":
  type: book
  author_bio: "UCLA strategy professor and author of Good Strategy / Bad Strategy"
  work: "Good Strategy / Bad Strategy"

"Daniel Kahneman, 2011":
  type: book
  author_bio: "Princeton psychologist, Nobel laureate, author of Thinking Fast and Slow"
  work: "Thinking Fast and Slow"

"Nate B. Jones, AI Daily Update":
  type: video
  # no author_bio — treated as voice, not citation

"Anonymous":
  type: post
```

- **Key:** source slug as it appears in atom `source:` field.
- **`type`:** `book | video | podcast | post`
- **`author_bio`:** required for `type: book`, optional otherwise.
- **`work`:** optional; book title for citation rendering.

Missing entries → fall back to 3-5 word anchor with a logged warning so the registry can be filled forward.

### 3.3 PostBrief additions

Add one field:

- `thesis: str` — the display-type line that renders as hero. Extracted from body text via `<THESIS>...</THESIS>` tags during text generation. User-editable at Gate 1.

No other shape changes. `visual_tier="1_diagram"` retained (do not rename to "1_card" — keeping the field name avoids migrating any existing PostBrief bundles).

### 3.4 LLM fallback for missing tldr

When the renderer needs an atom's tldr and it's missing, a one-shot fill runs at draft time:

- **Input:** atom title, summary (atom body up to first heading or 200 words), domain, source.
- **Output:** single sentence, ~80 chars, standalone-readable.
- **Side effect:** back-write the result to the atom file's front-matter under `tldr`. Atom is now "filled" for future uses.
- **Failure mode:** if the fill itself fails (API error, validation), render the atom block with name only (no distillation line), warn in logs.

This is a one-time cost per atom; the graph compounds.

---

## 4. Voice prompt v2

### 4.1 THESIS tags

The text generator system prompt requires:

> Your post must contain **exactly one** thesis sentence wrapped in `<THESIS>...</THESIS>` tags. This sentence will be rendered as the hero line of the visual — treat it as a standalone aphorism. Place it where it reads naturally in the post; it is part of the body, not a header.

After generation, the engine extracts the tagged sentence into `PostBrief.thesis` and strips the tags from the saved `post.md`. The saved post.md is what gets pasted to LinkedIn — clean.

**Failure modes:**
- Zero `<THESIS>` tags → use the first sentence of the body as fallback, warn in logs.
- Multiple `<THESIS>` tags → use the first, warn.
- Empty tag → use first sentence fallback, warn.

At Gate 1, user can edit `thesis` directly in PostBrief (overrides extraction) or re-tag a different sentence in the body and re-advance (re-extracts).

### 4.2 Source-type-aware COLD READER ANCHOR

The current rule (added in v1.0.1) is a uniform "place source authors in 3-5 words on first reference." It becomes:

```
COLD READER ANCHOR (source-type-aware):

For each cited source, look up the source in sources.yml:

- type: book → On first reference, introduce the author with a full one-sentence
  bio from the registry. Example: "Reading three atoms from Richard Rumelt, a
  UCLA strategy professor and author of Good Strategy / Bad Strategy..."

- type: video | podcast | post → On first reference, use a 3-5 word descriptor
  (current rule). Example: "Per Nate B. Jones, an AI commentator..."

- source not in registry → Use 3-5 word descriptor as fallback; the system will
  log a registry-miss warning.

Anchored concepts (5-8 word definition on first reference) rule remains
unchanged for all source types.
```

The voice linter does not enforce this rule programmatically — it's a generation-time prompt constraint, not a post-hoc lint. (The linter still enforces em-dashes, contrastive framing, etc.)

---

## 5. Renderer (Playwright stack)

### 5.1 Stack

- **Engine:** Playwright headless Chromium, driven from Python.
- **Template:** Jinja2-rendered HTML file at `src/renderers/templates/atom-card.html`.
- **CSS:** inline `<style>` block at the top of the template. Tokens injected from brand-spec at render time.
- **Output:** PNG (1080×1080) + SVG (vector source). Both written to bundle folder.

### 5.2 Class layout

```python
class AtomCardRenderer:
    tier = 1

    def __init__(self, loader: AtomLoader,
                 sources_registry: SourcesRegistry,
                 brand_spec_path: Path,
                 tldr_filler: TldrFiller):
        ...

    def validate(self, brief: PostBrief) -> list[str]:
        # See §6 for full rule list
        ...

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        # 1. Load brand tokens
        # 2. Resolve atoms (load each atom referenced)
        # 3. Resolve tldr per atom (front-matter; LLM fill if missing; back-write)
        # 4. Apply overflow rule (cap at 3, build overflow line for 4+)
        # 5. Resolve source for footer (first cited source slug)
        # 6. Render Jinja template → HTML string
        # 7. Playwright: launch, set_viewport_size(1080, 1080), set_content, screenshot
        # 8. Also export SVG via page.evaluate('document.documentElement.outerHTML') + svg conversion
        # 9. Return RenderResult(asset_paths=[png, svg], cost=tldr_fill_cost, duration_s, logs)
```

### 5.3 Setup

- `requirements.txt`: add `playwright>=1.40`.
- One-time install: `playwright install chromium`. Document in project README and CLAUDE.md.
- Chromium binary location: managed by Playwright (`~/Library/Caches/ms-playwright/` on macOS).
- Render cost: ~1-2s per call (browser startup amortizable if we keep a long-running context, but v1.1 ships with per-render launch for simplicity).

### 5.4 Deletions

Delete from the codebase as part of this phase:

- `src/renderers/diagram.py` (graphviz renderer)
- `_EDGE_STYLE_BY_TYPE` mapping
- Edgeless-diagram validation in the old renderer
- Graphviz dependency from `requirements.txt`
- The `dot` binary check in CLI pre-flight
- All `connection_graph` reads from the renderer path (the graph is still loaded for strategies; the renderer no longer touches it)

`ConnectionGraph` itself stays — it's used by `two_atom_bridge` and `source_spotlight._find_secondary_domain`. Just the renderer-side coupling goes.

---

## 6. Strategy default updates

| Strategy | v1.0.2 default | v1.1 default | Notes |
|---|---|---|---|
| `source_spotlight` | `1_diagram` (with edgeless guard) | `1_diagram` | Now renders cleanly even with no inter-atom edges |
| `two_atom_bridge` | `0_text` | `1_diagram` | Card template works at 2 atoms (validated in mockup) |
| `cluster_reveal` | `2_carousel` (not implemented) | `2_carousel` (deferred to v1.2) | If user forces `1_diagram`, overflow rule kicks in |
| `convergence_finder` | `2_carousel` (not implemented) | `1_diagram` | Convergence posts work as 2-3 atom card; carousel was overkill for v1 |

Note on `convergence_finder`: the v1.0 design defaulted it to Tier 2 carousel under the assumption that convergence posts walk through 3+ atoms. In practice the synthesis is the value; 2-3 atoms in the new card template carry it. Flipping to Tier 1 means convergence posts ship in v1.1 instead of waiting for v1.2.

---

## 7. visual-discipline skill update

Replace the Tier 1 rules in `.claude/skills/linkedin/visual-discipline/SKILL.md` §3 ("Validate brief against tier rules"):

**Old Tier 1 rules (delete):**
- ≤6 nodes
- every node has ≥1 edge
- aspect ratio 1:1 or 4:5
- connection-type edge labels mandatory when `connection_type ≠ general`

**New Tier 1 rules:**
- ≤3 distilled atom blocks (4+ atoms apply overflow rule)
- non-empty thesis present (extracted from `<THESIS>` or first-sentence fallback)
- `tldr` resolved for each shown atom (front-matter or LLM fill succeeded)
- source slug present in footer (first cited source from atoms)
- aspect ratio 1:1
- brand tokens loaded from `brand-spec.md` (no hardcoded colors in template)

Anti-pattern checks unchanged (no center-gradient, no drop shadows, no all-caps body labels).

---

## 8. Failure modes (consolidated)

| Failure | Behavior |
|---|---|
| Atom missing `tldr` | LLM fill runs, back-writes to atom file |
| LLM fill fails | Atom renders with name only, no distillation line, warn in logs |
| Body has no `<THESIS>` tag | Fall back to first sentence, warn in logs |
| Body has multiple `<THESIS>` tags | Use the first, warn |
| Source not in `sources.yml` | Fall back to 3-5 word anchor, log registry-miss for forward fill |
| Playwright Chromium not installed | Hard fail at engine startup with install instructions |
| Atom count > 3 | Overflow rule (§2.2) |
| Strategy emits `atom_count=0` | Strategy-side error before render |

---

## 9. Out of scope (deferred)

- **Tier 2 carousel** → v1.2. `cluster_reveal` waits.
- **Tier 3 video** → v1.3.
- **4:5 aspect ratio variant** → v1.x as needed.
- **Atom backfill (existing atoms get tldr retroactively)** → forward-fill only; atoms get filled when first used in a post.
- **Sources registry backfill** → forward-fill only; registry grows as posts cite new sources.
- **Multi-source posts (footer shows 2+ sources)** → v1.x. v1.1 footer shows the first cited source.
- **Telegram approval gate** → v2.0.
- **Supabase backlog migration** → v2.0.

---

## 10. Implementation phases (preview, not the plan)

The implementation plan will be written separately. Rough decomposition:

1. **Renderer swap.** Add Playwright, write the Jinja template, AtomCardRenderer class, delete graphviz code.
2. **Atom schema v2.2.** Add optional `tldr` field to AtomLoader parse; back-write helper.
3. **Sources registry.** Add `sources.yml`, SourcesRegistry loader.
4. **Voice prompt v2.** Update `text_generator.py` system prompt; THESIS tag extraction; sources-aware anchor injection.
5. **Strategy defaults.** Flip `two_atom_bridge` and `convergence_finder` defaults.
6. **visual-discipline skill.** Update rules per §7.
7. **Tests.** Replace graphviz tests; new tests for tldr fill, THESIS extraction, overflow rule, Playwright render smoke.
8. **Smoke test.** Re-run `source_spotlight --source='Richard Rumelt, 2011'` against the new renderer. Inspect output. Document in `decision-log.md`.

Estimated effort: 3-5 days end-to-end including smoke verification.

---

## 11. Open questions

None at design lock. Open items deferred to planning:

- Long-running Chromium context vs per-render launch (latency vs simplicity tradeoff).
- SVG export approach (Playwright doesn't natively export SVG; either render SVG via the HTML directly or skip SVG in v1.1).
- Whether `tldr` LLM fill uses Haiku or Sonnet (cost vs quality).
- Whether the overflow line clicks through to a sources.yml-like atom registry (a v2.0 idea, not v1.1).

---

*Companion docs:*
- *Original engine design: `2026-05-24-linkedin-engine-design.md` (§5.1 superseded by this doc)*
- *Decision log: `decision-log.md`*
- *Implementation plan: `2026-05-25-v1-1-implementation-plan.md` (to be written next)*
