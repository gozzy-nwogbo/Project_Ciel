# LinkedIn Engine v1.2: Strategy-Specific Visuals (Bridge + Convergence)

**Date:** 2026-05-26
**Version:** v1.2 (design)
**Status:** Approved (brainstorm), pending planning
**Owner:** nwogbo_gozzy
**Supersedes:** Strategy defaults set in v1.1.3 (`two_atom_bridge` and `convergence_finder` reverting to `0_text`)
**Precedes:** `2026-05-26-v1-2-implementation-plan.md` (to be written next)

---

## Executive summary

Bring `two_atom_bridge` and `convergence_finder` back onto Tier 1 visuals with strategy-specific templates that match each strategy's conceptual shape. Bridge gets a literal-bridge template (two atom pillars side-by-side with a mechanism band spanning beneath). Convergence gets a funnel template (three atom blocks at the top, arrows down, a convergence panel at the bottom). Both render at 4:5 (1080×1350) so the text panels have room to breathe. The renderer codebase splits from one `AtomCardRenderer` into three sibling renderers behind a small Tier 1 registry; PostBrief gains three additive fields (`aspect_ratio`, `panel_label`, `panel_claim`); voice prompt v3 adds a strategy-scoped `<CLAIM>...</CLAIM>` tag for the two new strategies. `source_spotlight` is untouched.

---

## 1. Why now

v1.1 shipped the atom-card visual against `source_spotlight` and it worked. v1.1.3 then ran the other two Tier 1 strategies end-to-end and discovered the visual was conceptually wrong for them.

- `two_atom_bridge` is about *a connection between two things*. The atom-card flattened that into a list of two items, so the bridge structure (relationship, mechanism, analogy) was invisible.
- `convergence_finder` is about *multiple distant atoms pointing at a shared center*. The atom-card flattened that into a bullet list, so the convergence point itself was invisible.

The v1.1.3 patch defaulted both strategies back to `0_text` while preserving the engine's ability to ship those posts as text-only. This design unblocks visuals for both by accepting that **each strategy has its own conceptual shape and deserves its own visual primitive.**

---

## 2. Visual templates

### 2.1 Bridge A (`two_atom_bridge`)

**Layout:**

```
┌────────────────────────────────────────────────┐
│  FROM SECOND BRAIN          bridge // a × b    │  meta row
│                                                │
│  {thesis line, 28-32px}                        │
│                                                │
│  ┌─────────────────┐    ┌─────────────────┐    │
│  │ {domain a}      │    │ {domain b}      │    │  pillars
│  │ {Atom A Name}   │    │ {Atom B Name}   │    │
│  │ {tldr a}        │    │ {tldr b}        │    │
│  └─────────────────┘    └─────────────────┘    │
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │  {PANEL_LABEL}                         │    │  mechanism band
│  │  {italic panel_claim}                  │    │  (terracotta dashed border)
│  └────────────────────────────────────────┘    │
│                                                │
│  2 atoms · cross-domain      two-atom-bridge   │  footer
└────────────────────────────────────────────────┘
```

- **Canvas:** 1080×1350 (4:5). Padding 38px top/bottom, 36px left/right.
- **Pillars:** two equal-width cards (`grid-template-columns: 1fr 1fr`, gap 14px). Padding 18px/16px. Background `surface_subtle` (#F3F0EB), border `border` (#E8E4DF), radius 4px.
- **Pillar content (top-to-bottom):** domain (10px Geist Mono, lowercase, color `text_secondary`); atom name (15px Geist 600, color `text_primary`); tldr (12px Geist 400, line-height 1.4, color `text_secondary`, `margin-top: auto` so it anchors to the bottom of the panel).
- **Mechanism band:** full-width panel beneath the pillars. Padding 16px/18px. Background `background` (#FAF8F5). Border 1px dashed `accent_primary` (#B5654A), radius 4px.
- **Band content (centered):** `panel_label` (10px Geist Mono, uppercase, letter-spacing 0.14em, color `accent_primary`); `panel_claim` (14px italic Geist 400, line-height 1.35, color `text_primary`).
- **Footer:** left `"2 atoms · cross-domain"`, right `"two-atom-bridge"`. Both 11px Geist Mono.
- **Tldr cap:** 110 characters per pillar (more room than the 80-char cap on `source_spotlight` because there are only two atoms and the canvas is taller). Truncation at word boundary with ellipsis on overshoot.
- **Thesis cap:** 60 characters keeps the thesis to two lines at 28px. Auto-shrink to 24px if longer (mirrors v1.1.1 logic).

### 2.2 Convergence C (`convergence_finder`)

**Layout:**

```
┌────────────────────────────────────────────────┐
│  FROM SECOND BRAIN       convergence // 3 dom. │  meta row
│                                                │
│  {thesis line, 28-32px}                        │
│                                                │
│  ┌──────┐  ┌──────┐  ┌──────┐                  │
│  │ atom │  │ atom │  │ atom │                  │  funnel atoms
│  └──────┘  └──────┘  └──────┘                  │
│      ↓        ↓        ↓                       │  arrows
│                                                │
│  ┌────────────────────────────────────────┐    │
│  │  {PANEL_LABEL, e.g. "CONVERGES ON · X"} │   │  convergence panel
│  │  {italic panel_claim}                  │    │  (terracotta solid border)
│  └────────────────────────────────────────┘    │
│                                                │
│  3 atoms · 3 domains       convergence-finder  │  footer
└────────────────────────────────────────────────┘
```

- **Canvas:** 1080×1350 (4:5). Padding 38px top/bottom, 36px left/right.
- **Funnel atoms row:** three equal-width cards (`grid-template-columns: 1fr 1fr 1fr`, gap 10px). Padding 14px/12px. Same background, border, radius as Bridge pillars.
- **Atom content (top-to-bottom):** domain (10px Geist Mono, lowercase); atom name (13px Geist 600); tldr (11px Geist 400, line-height 1.4). Tldr cap: 60 characters per atom (tighter than bridge because three atoms share the row).
- **Arrows row:** three centered `↓` glyphs aligned to the three atom columns. 22px Geist Mono, color `accent_primary`.
- **Convergence panel:** full-width panel beneath the arrows. Padding 16px/18px. Background `background`. Border 1.5px **solid** `accent_primary` (slightly heavier than the dashed mechanism band so the two strategies remain visually distinguishable at a glance).
- **Panel content (centered):** `panel_label` (10px Geist Mono, uppercase, letter-spacing 0.14em, color `accent_primary`); `panel_claim` (16px Geist 500, italic, line-height 1.3, color `text_primary`).
- **Footer:** left `"{N} atoms · {M} domains"` where N = atom count and M = distinct domain count; right `"convergence-finder"`. Both 11px Geist Mono.
- **Atom-count cap:** 3 funnel atoms. If the strategy ever picks more, truncate to 3 in the funnel and append `+ N more` as a 4th block (same pattern as `atom_card` §2.2). In v1.2, `convergence_finder` only picks `MIN_DOMAINS=3` atoms so the cap is not triggered.
- **Thesis cap:** same as bridge (60 chars at 28px, auto-shrink to 24px).

### 2.3 Visual family

The dashed-border mechanism band (bridge) and the solid-border convergence panel (convergence) are the same primitive in two roles. Same terracotta accent, same internal layout (small uppercase label + italic claim), different stroke style. A future strategy that needs a synthesis anchor can reuse the primitive without inventing new vocabulary.

### 2.4 Aspect ratio policy

Per-strategy default:

| Strategy | Aspect ratio | Reason |
|---|---|---|
| `source_spotlight` | 1:1 (1080×1080) | Ships well at square; no reason to disturb. |
| `two_atom_bridge` | 4:5 (1080×1350) | Three-region layout (pillars + band + footer) needs vertical room. |
| `convergence_finder` | 4:5 (1080×1350) | Funnel needs vertical travel between the atom row and the convergence panel. |
| `cluster_reveal` | n/a (Tier 2, v1.3+) | Carousel, separate spec. |

`brand-spec.md` already declares `aspect_ratios: ["1:1", "4:5"]`. v1.2 activates 4:5.

---

## 3. Data model changes

### 3.1 PostBrief additions

Three new fields. All additive with safe defaults; `source_spotlight` ignores them.

```python
@dataclass
class PostBrief:
    # existing fields...
    aspect_ratio: str = "1:1"     # NEW
    panel_label: str = ""         # NEW
    panel_claim: str = ""         # NEW
```

- `aspect_ratio`: one of `"1:1"` or `"4:5"`. The Tier 1 renderer reads it to set the Playwright viewport (1080×1080 or 1080×1350) and apply the corresponding CSS aspect-ratio token. Each strategy sets its default at brief-generation time.
- `panel_label`: uppercase label string for the band/panel. Set deterministically by the strategy (see §4). `source_spotlight` leaves it empty and its renderer ignores the field.
- `panel_claim`: italic claim sentence for the band/panel. Set by the text generator via `<CLAIM>...</CLAIM>` tag extraction (see §5). `source_spotlight` leaves it empty.

### 3.2 No changes to atom front-matter

v2.2 (`tldr` field, sources registry) carries forward unchanged. No new atom-level fields are required.

### 3.3 No changes to sources registry

`sources.yml` is unchanged. Bridge and convergence both rely on the same source-type-aware cold-reader anchor mechanism v1.1 introduced.

---

## 4. Strategy updates

### 4.1 `two_atom_bridge.py`

Add a label map at module scope:

```python
_LABEL_BY_CONNECTION_TYPE = {
    "mechanism":  "SHARED MECHANISM",
    "analogical": "STRUCTURAL ANALOGUE",
    "inverse":    "INVERSE PAIR",
    "general":    "BRIDGE",
}
```

In `generate_brief()`, after looking up `connection_type` from the edge:

```python
return PostBrief(
    # existing fields...
    visual_tier="1_diagram",                          # was "0_text" in v1.1.3
    aspect_ratio="4:5",                                # NEW
    panel_label=_LABEL_BY_CONNECTION_TYPE.get(connection_type, "BRIDGE"),
    panel_claim="",                                    # filled by text_generator
)
```

Delete the v1.1.3 comment justifying `0_text`. The existing same-domain validation stays.

### 4.2 `convergence_finder.py`

In `generate_brief()`, after `MIN_DOMAINS` check passes:

```python
return PostBrief(
    # existing fields...
    visual_tier="1_diagram",                           # was "0_text" in v1.1.3
    aspect_ratio="4:5",                                 # NEW
    panel_label=f"CONVERGES ON · {topic.upper()}",
    panel_claim="",                                     # filled by text_generator
)
```

Delete the v1.1.3 comment justifying `0_text`. `MIN_DOMAINS = 3` stays.

### 4.3 `source_spotlight.py`

No changes. Continues to set `visual_tier="1_diagram"`, `aspect_ratio="1:1"` (defaults), `panel_label=""`, `panel_claim=""`.

### 4.4 `cluster_reveal.py`

No changes. Still produces `visual_tier="2_carousel"` and is non-functional until v1.3.

---

## 5. Voice prompt v3

### 5.1 New strategy-scoped CLAIM tag

`VOICE_SYSTEM_PROMPT` gains one new section that fires only for the two new strategies. The existing `<THESIS>` rule (v1.1) applies to all strategies and is unchanged.

```
CLAIM TAG (strategy-scoped):

If this is a `two_atom_bridge` or `convergence_finder` post, your post must
contain exactly one synthesizing sentence wrapped in <CLAIM>...</CLAIM> tags.

- For two_atom_bridge: the shared-mechanism sentence. It will render as the
  italic line inside the mechanism band.
- For convergence_finder: the unified-mechanism sentence. It will render as
  the italic line inside the convergence panel.

Place it where it reads naturally in the body. It is part of the post, not
a header. After generation the engine strips the tags so the saved post.md
reads clean.
```

The v1.1 `VOICE_SYSTEM_PROMPT` is a static constant today. v1.2 keeps it static but composes the per-call system prompt at `generate()` time:

```python
system_prompt = VOICE_SYSTEM_PROMPT
if brief.strategy in {"two_atom_bridge", "convergence_finder"}:
    system_prompt += "\n\n" + CLAIM_TAG_RULE
```

`CLAIM_TAG_RULE` is a new module-scope constant holding the block above. The conditional fires in Python, not in the prompt itself, so non-bridge / non-convergence posts never see the rule.

### 5.2 Extraction

The v1.1 `_extract_tagged_sentence()` helper is parameterized to take a tag name:

```python
def _extract_tagged_sentence(body: str, tag: str) -> tuple[str, str]:
    # returns (extracted_sentence, body_with_tags_stripped)
```

Pipeline order after generation:

1. Extract `<THESIS>` → `brief.thesis`; strip tags from body.
2. If strategy in `{two_atom_bridge, convergence_finder}`: extract `<CLAIM>` → `brief.panel_claim`; strip tags from body.
3. Save the cleaned body to `post.md`.

### 5.3 CLAIM tag failure modes

| Failure | Behavior |
|---|---|
| Zero `<CLAIM>` tags on bridge post | Fall back to `connection_edge.claim` as `panel_claim`; warn in logs. |
| Zero `<CLAIM>` tags on convergence post | Fall back to `angle` as `panel_claim`; warn in logs. |
| Multiple `<CLAIM>` tags | Use the first occurrence, warn. |
| Empty `<CLAIM></CLAIM>` | Treat as zero tags (apply fallback above). |

User edits at Gate 1 work the same as thesis: edit `panel_claim` in the brief directly, or re-tag a different sentence in the body and re-advance to re-extract.

---

## 6. Renderer architecture

### 6.1 File layout

```
src/renderers/
  base.py                       # existing. RenderResult, load_brand_spec
  atom_card.py                  # existing. AtomCardRenderer (source_spotlight)
  bridge_card.py                # NEW. BridgeCardRenderer
  convergence_card.py           # NEW. ConvergenceCardRenderer
  registry.py                   # NEW. strategy.name → renderer instance
  templates/
    _card_frame.css             # NEW. shared CSS partial
    atom_card.html.j2           # existing
    bridge_card.html.j2         # NEW
    convergence_card.html.j2    # NEW
```

### 6.2 Renderer class shape

Both new renderers follow the same shape as `AtomCardRenderer`:

```python
class BridgeCardRenderer:
    tier = 1

    def __init__(self, loader, sources_registry, brand_spec_path, tldr_filler):
        ...

    def validate(self, brief: PostBrief) -> list[str]:
        # see §6.4
        ...

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        # 1. validate(brief). Raise on error.
        # 2. Resolve atoms (2 for bridge, ≥3 for convergence)
        # 3. Resolve tldr per atom (front-matter; LLM fill if missing; back-write)
        # 4. Build template context (atom blocks, panel_label, panel_claim, brand tokens)
        # 5. Render strategy-specific Jinja template
        # 6. Playwright launch → set_viewport_size per aspect_ratio → screenshot
        # 7. Return RenderResult
```

### 6.3 Tier 1 registry

```python
# src/renderers/registry.py
from typing import Callable
from atom_loader import AtomLoader
from renderers.atom_card import AtomCardRenderer
from renderers.bridge_card import BridgeCardRenderer
from renderers.convergence_card import ConvergenceCardRenderer

_TIER1: dict[str, Callable] = {
    "source_spotlight":    AtomCardRenderer,
    "two_atom_bridge":     BridgeCardRenderer,
    "convergence_finder":  ConvergenceCardRenderer,
}

def for_strategy(strategy_name: str, **kwargs):
    cls = _TIER1.get(strategy_name)
    if cls is None:
        raise ValueError(f"No Tier 1 renderer for strategy '{strategy_name}'")
    return cls(**kwargs)
```

CLI wiring (in `_advance`) replaces the hard-coded `AtomCardRenderer(...)` instantiation with `tier1_registry.for_strategy(brief.strategy, loader=..., sources_registry=..., brand_spec_path=..., tldr_filler=...)`.

### 6.4 Per-renderer validate rules

| Renderer | Validates |
|---|---|
| `AtomCardRenderer` (unchanged) | thesis non-empty; ≥1 atom; tldr resolvable per atom. |
| `BridgeCardRenderer` (NEW) | thesis non-empty; exactly 2 atoms; atoms have different domains; `panel_label` non-empty; `panel_claim` non-empty; `aspect_ratio == "4:5"`; tldr resolvable per atom. |
| `ConvergenceCardRenderer` (NEW) | thesis non-empty; ≥3 atoms; ≥3 distinct domains; `panel_label` non-empty; `panel_claim` non-empty; `aspect_ratio == "4:5"`; tldr resolvable per atom. |

### 6.5 Shared CSS partial

`_card_frame.css` holds tokens and the structural CSS that all three Tier 1 visuals need: canvas frame (background, border, radius, padding, font-family), aspect-ratio CSS variable, meta-row, thesis, footer. Each strategy's `.html.j2` injects it via Jinja `{% include "_card_frame.css" %}` inside a `<style>` block. Anti-pattern checks unchanged (no center-gradient, no drop shadows, no all-caps body text).

---

## 7. `visual-discipline` skill update

Replace the single Tier 1 rule block in `.claude/skills/linkedin/visual-discipline/SKILL.md` §3 with three strategy-keyed blocks.

**Tier 1 · `source_spotlight` rules (unchanged from v1.1):**
- ≤3 distilled atom blocks (overflow rule for 4+)
- non-empty thesis
- `tldr` resolved per shown atom
- source slug present in footer
- aspect ratio 1:1
- brand tokens loaded from `brand-spec.md`

**Tier 1 · `two_atom_bridge` rules (NEW):**
- exactly 2 atom pillars
- atoms in different domains
- non-empty thesis
- non-empty `panel_label` (from `_LABEL_BY_CONNECTION_TYPE`)
- non-empty `panel_claim` (from `<CLAIM>` or fallback)
- `tldr` resolved per pillar
- aspect ratio 4:5
- mechanism band: dashed terracotta border, italic claim

**Tier 1 · `convergence_finder` rules (NEW):**
- 3 funnel atoms (truncate at 3 if strategy emits more)
- ≥3 distinct domains across atoms
- non-empty thesis
- non-empty `panel_label` (composed as `CONVERGES ON · {topic}`)
- non-empty `panel_claim` (from `<CLAIM>` or fallback)
- `tldr` resolved per atom
- aspect ratio 4:5
- convergence panel: solid terracotta border, italic claim

**Anti-patterns (shared across all Tier 1):**
- no center-radial-gradient backgrounds
- no drop shadows on atom cards or panels
- no all-caps body text (labels in band/panel are allowed; tldr text is not)

---

## 8. Failure modes (consolidated)

| Failure | Behavior |
|---|---|
| Atom missing `tldr` | LLM fill runs, back-writes to atom file (unchanged from v1.1). |
| LLM fill fails | Atom renders with name only, no distillation line, warn (unchanged). |
| Body has no `<THESIS>` tag | Fall back to first sentence, warn (unchanged). |
| **Bridge/convergence post has no `<CLAIM>` tag** | **Fall back to `connection_edge.claim` (bridge) or `angle` (convergence); warn.** |
| **Multiple `<CLAIM>` tags** | **Use the first occurrence, warn.** |
| **Bridge `connection_type` not in label map** | **Default to `"BRIDGE"`, warn.** |
| Bridge atoms share domain | Strategy-side error before render (existing check, kept). |
| Convergence with <3 distinct domains | Strategy-side error before render (existing `MIN_DOMAINS` check, kept). |
| **Renderer receives unexpected `aspect_ratio`** | **`validate()` fails before Playwright launch.** |
| Source not in `sources.yml` | Fall back to 3-5 word anchor, log registry-miss (unchanged). |
| Playwright Chromium not installed | Hard fail at engine startup (unchanged). |
| Atom count exceeds renderer cap | Truncate + overflow line for convergence (≥4 case); strategy enforces 2 for bridge. |

---

## 9. Out of scope (deferred)

- **1:1 variants of bridge/convergence.** Chosen 4:5 because of the text-density concern flagged during brainstorm; 1:1 would re-create the problem.
- **4:5 for `source_spotlight`.** Works at 1:1; no reason to disturb.
- **Tier 2 carousel (`cluster_reveal`).** Still v1.3.
- **Hand-authored `panel_label` override at Gate 1.** Derived deterministically for now; if it bites in practice, add an editable field later.
- **Bridge mechanism sub-label.** The `· SPECIFIC-NAME` part of the mockup label is dropped from v1.2. The italic claim sentence carries the specifics. Reconsider if it shows up as a real gap during smoke.
- **Multi-source footer for bridge/convergence.** Footer right-side still shows strategy name only; v1.x.
- **THESIS / CLAIM tag auto-repair.** Still warn + fall back, don't auto-fix.
- **SVG export.** Still PNG only (Playwright doesn't natively export SVG; not worth the conversion path in v1.x).

---

## 10. Implementation phases (preview, not the plan)

The actual plan goes in `2026-05-26-v1-2-implementation-plan.md`, produced by `writing-plans`. Rough decomposition:

1. **PostBrief schema deltas.** Add `aspect_ratio`, `panel_label`, `panel_claim` to the dataclass with safe defaults. Make sure existing brief bundles deserialize cleanly (the three new fields are additive).
2. **Strategy updates.** Flip `two_atom_bridge` and `convergence_finder` `visual_tier` back to `1_diagram`; set the new fields; delete v1.1.3 justification comments.
3. **Voice prompt v3.** Add the strategy-scoped `<CLAIM>` rule. Parameterize `_extract_tagged_sentence()`. Pipeline order: extract THESIS, then CLAIM (if applicable), then strip both.
4. **Shared CSS partial.** Extract the canvas frame / meta-row / thesis / footer CSS from `atom_card.html.j2` into `_card_frame.css`. Re-include in `atom_card.html.j2` so nothing visually changes for `source_spotlight`.
5. **`BridgeCardRenderer` + `bridge_card.html.j2`.** Pillars + mechanism band at 4:5.
6. **`ConvergenceCardRenderer` + `convergence_card.html.j2`.** Funnel + convergence panel at 4:5.
7. **Tier 1 registry + CLI wiring.** Replace hard-coded `AtomCardRenderer` instantiation with `tier1_registry.for_strategy(...)`.
8. **`visual-discipline` skill update.** Three strategy-keyed rule blocks; shared anti-patterns stay shared.
9. **Tests.** Per-renderer `validate()` (bridge: exactly-2-atoms, different-domains, panel fields, 4:5; convergence: ≥3 atoms, ≥3 domains, panel fields, 4:5); `_LABEL_BY_CONNECTION_TYPE` derivation; `panel_label` composition for convergence; `<CLAIM>` extraction + fallback paths; viewport math per aspect_ratio; Playwright render smoke for each new renderer.
10. **Smoke test.** Re-run the v1.1.3 atoms (`antifragile-triad × autoregulated-active-recovery` for bridge, `--topic=feedback` for convergence). Document in `decision-log.md`. Expected: both render cleanly at 4:5, no truncation, claim text reads as a natural sentence inside the band/panel.

**Effort estimate:** 3-4 days end-to-end including smoke and any patch iterations. Similar to v1.1 in shape and scope.

---

## 11. Open questions (deferred to planning)

These have no design implications and don't block planning. Carry the v1.1 defaults unless smoke surfaces a reason to change.

- Long-running Playwright context vs per-render launch. Carry v1.1: per-render launch.
- Haiku vs Sonnet for `TldrFiller`. Carry v1.1: Haiku.
- Whether `_card_frame.css` should live as a separate file Jinja-included, or as a Jinja macro that emits the `<style>` block. Stylistic choice; planner picks.

---

*Companion docs:*
- *v1.1 atom-card design: `2026-05-25-tier1-redesign-design.md`*
- *Decision log: `decision-log.md`*
- *Implementation plan: `2026-05-26-v1-2-implementation-plan.md` (to be written next)*
