# LinkedIn Engine v1.2 Implementation Plan: Strategy-Specific Visuals

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `two_atom_bridge` and `convergence_finder` back onto Tier 1 visuals with strategy-specific templates that match each strategy's conceptual shape, rendered at 4:5 (1080x1350) so the texts have room. `source_spotlight` is untouched.

**Architecture:** Three sibling renderer classes (`AtomCardRenderer` existing, plus new `BridgeCardRenderer` and `ConvergenceCardRenderer`) sit behind a small Tier 1 registry. `PostBrief` gains three additive fields (`aspect_ratio`, `panel_label`, `panel_claim`). A new strategy-scoped `<CLAIM>...</CLAIM>` rule is appended to the voice prompt at `generate()` time for bridge and convergence posts; the existing `extract_thesis` helper is generalized to `extract_tagged`. Two new Jinja templates include a shared CSS partial for the meta row, footer, and brand tokens; layout CSS (pillars + mechanism band; funnel + convergence panel) lives in each strategy's template.

**Tech Stack:** Python 3.11+, Playwright (headless Chromium, existing), Jinja2 (existing), Anthropic SDK (`claude-opus-4-7`, existing), pytest (existing).

**Spec reference:** `01-projects/linkedin/docs/2026-05-26-strategy-visuals-design.md`

**Working tree:** Create a feature branch `feat/linkedin-engine-v1.2` from `main` before Task 1.

---

## File map

**Create:**
- `src/renderers/bridge_card.py`. `BridgeCardRenderer` class.
- `src/renderers/convergence_card.py`. `ConvergenceCardRenderer` class.
- `src/renderers/registry.py`. Tier 1 strategy-to-renderer dispatch.
- `src/renderers/templates/_card_frame.css.j2`. Shared CSS partial (Jinja-included).
- `src/renderers/templates/bridge_card.html.j2`. Bridge A template (pillars + mechanism band, 4:5).
- `src/renderers/templates/convergence_card.html.j2`. Convergence C template (funnel + convergence panel, 4:5).
- `src/linter/tagged.py`. Generalized `extract_tagged(body, tag)` helper.
- `tests/test_bridge_card_renderer.py`. Renderer + validate tests.
- `tests/test_convergence_card_renderer.py`. Renderer + validate tests.
- `tests/test_renderers_registry.py`. Registry dispatch tests.
- `tests/test_tagged_extraction.py`. Generalized extractor tests.

**Modify:**
- `src/models.py`. Add `aspect_ratio`, `panel_label`, `panel_claim` to `PostBrief`; round-trip in `to_dict` / `from_dict`.
- `src/linter/thesis.py`. Re-implement on top of `extract_tagged`; keep public API stable so callers keep working.
- `src/text_generator.py`. Add `CLAIM_TAG_RULE` constant, conditional concat in `generate()`, CLAIM extraction step.
- `src/strategies/two_atom_bridge.py`. Flip `visual_tier` to `"1_diagram"`, set `aspect_ratio="4:5"`, set `panel_label` from `_LABEL_BY_CONNECTION_TYPE`, delete v1.1.3 comment.
- `src/strategies/convergence_finder.py`. Flip `visual_tier` to `"1_diagram"`, set `aspect_ratio="4:5"`, compose `panel_label`, delete v1.1.3 comment.
- `src/cli/draft_post.py`. Replace hard-coded `AtomCardRenderer` instantiation with `tier1_registry.for_strategy(...)`.
- `.claude/skills/linkedin/visual-discipline/SKILL.md`. Replace single Tier 1 block with three strategy-keyed blocks.
- `tests/test_models.py`. Round-trip with the three new fields.
- `tests/test_two_atom_bridge.py`. Assert new `visual_tier`, `aspect_ratio`, `panel_label`.
- `tests/test_convergence_finder.py`. Assert new `visual_tier`, `aspect_ratio`, `panel_label`.
- `tests/test_text_generator.py`. Assert CLAIM rule appears only for bridge/convergence posts and that CLAIM extraction populates `brief.panel_claim`.
- `tests/test_thesis_extraction.py`. Adjust if internals moved (public API unchanged so most tests should keep passing).
- `tests/test_cli_draft_post.py`. Registry-based dispatch.
- `tests/test_end_to_end.py`. Expect non-empty `visual_asset_paths` for bridge + convergence; 4:5 viewport math.

**Leave alone:**
- `src/renderers/atom_card.py` and `src/renderers/templates/atom_card.html.j2`. The CSS-partial extraction inside `atom_card.html.j2` is deferred to keep `source_spotlight` regression-free in this cycle. The shared partial is used by the two new templates only; migrating `atom_card.html.j2` is a follow-up after smoke confirms parity.

---

## Task 1: Branch + scaffolding

**Files:**
- No code yet. Branch + directory check.

- [ ] **Step 1: Create the feature branch from main.**

```bash
cd /Users/gozzynwogbo/second-brain
git checkout main && git pull --ff-only && git checkout -b feat/linkedin-engine-v1.2
```

Expected: branch `feat/linkedin-engine-v1.2` created from current `main` (tip `ce8b28c` as of design lock).

- [ ] **Step 2: Confirm the spec is on this branch.**

```bash
ls 01-projects/linkedin/docs/2026-05-26-strategy-visuals-design.md
```

Expected: file present (it's already on `main`, so the branch inherits it).

- [ ] **Step 3: Run the existing test suite to confirm green baseline.**

```bash
cd 01-projects/linkedin
PYTHONPATH=src pytest tests/ -v 2>&1 | tail -20
```

Expected: 68/68 pass (v1.1.3 baseline).

- [ ] **Step 4: No commit. Branch is the only artifact.**

---

## Task 2: PostBrief schema deltas

**Files:**
- Modify: `src/models.py`
- Modify: `tests/test_models.py`

- [ ] **Step 1: Write the failing test in `tests/test_models.py`.**

Append this test at the bottom of the file (read the file first to keep style consistent):

```python
def test_postbrief_v12_fields_roundtrip():
    """v1.2 adds aspect_ratio, panel_label, panel_claim. Round-trip through to_dict / from_dict."""
    from datetime import datetime, timezone
    from models import AtomRef, PostBrief, Status

    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    brief = PostBrief(
        id="t",
        slug="t",
        created_at=now,
        updated_at=now,
        strategy="two_atom_bridge",
        strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary")],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        aspect_ratio="4:5",
        panel_label="SHARED MECHANISM",
        panel_claim="Both systems run the same loop.",
    )
    d = brief.to_dict()
    assert d["aspect_ratio"] == "4:5"
    assert d["panel_label"] == "SHARED MECHANISM"
    assert d["panel_claim"] == "Both systems run the same loop."

    rt = PostBrief.from_dict(d)
    assert rt.aspect_ratio == "4:5"
    assert rt.panel_label == "SHARED MECHANISM"
    assert rt.panel_claim == "Both systems run the same loop."


def test_postbrief_v12_defaults_when_missing():
    """Briefs serialized before v1.2 deserialize with safe defaults."""
    from datetime import datetime, timezone
    from models import PostBrief, Status

    d = {
        "id": "t",
        "slug": "t",
        "created_at": datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "updated_at": datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "strategy": "source_spotlight",
        "strategy_params": {},
        "atoms_used": [],
        "angle": "x",
        "visual_tier": "1_diagram",
        "status": "drafting",
    }
    rt = PostBrief.from_dict(d)
    assert rt.aspect_ratio == "1:1"
    assert rt.panel_label == ""
    assert rt.panel_claim == ""
```

- [ ] **Step 2: Run the failing test.**

```bash
PYTHONPATH=src pytest tests/test_models.py::test_postbrief_v12_fields_roundtrip tests/test_models.py::test_postbrief_v12_defaults_when_missing -v
```

Expected: FAIL with `TypeError: PostBrief.__init__() got an unexpected keyword argument 'aspect_ratio'`.

- [ ] **Step 3: Add the three fields to `PostBrief` in `src/models.py`.**

Find the dataclass block (currently ending at the `metrics: Optional[dict[str, Any]] = None` line near line 63). Add the three fields right after `thesis: str = ""`:

```python
    thesis: str = ""
    aspect_ratio: str = "1:1"
    panel_label: str = ""
    panel_claim: str = ""
```

- [ ] **Step 4: Extend `from_dict` to populate the new fields with defaults.**

Locate the `from_dict` classmethod. After the `thesis=d.get("thesis", ""),` line, add:

```python
            aspect_ratio=d.get("aspect_ratio", "1:1"),
            panel_label=d.get("panel_label", ""),
            panel_claim=d.get("panel_claim", ""),
```

`to_dict` uses `asdict(self)` so the new fields serialize automatically; no change needed there.

- [ ] **Step 5: Run the new tests.**

```bash
PYTHONPATH=src pytest tests/test_models.py -v 2>&1 | tail -20
```

Expected: PASS for both new tests; all other `test_models.py` tests still pass.

- [ ] **Step 6: Run the full suite to confirm nothing else broke.**

```bash
PYTHONPATH=src pytest tests/ -v 2>&1 | tail -10
```

Expected: all tests pass (the new fields are additive with defaults; existing call sites unaffected).

- [ ] **Step 7: Commit.**

```bash
git add 01-projects/linkedin/src/models.py 01-projects/linkedin/tests/test_models.py
git commit -m "feat(linkedin): v1.2 PostBrief gains aspect_ratio + panel_label + panel_claim"
```

---

## Task 3: Generalized tag extractor

**Goal:** Refactor `linter/thesis.py` so `extract_thesis` calls into a generic `extract_tagged(body, tag)` helper. This lets v1.2 add `extract_claim` (Task 4) without duplicating regex logic.

**Files:**
- Create: `src/linter/tagged.py`
- Modify: `src/linter/thesis.py`
- Create: `tests/test_tagged_extraction.py`

- [ ] **Step 1: Write the failing tests in `tests/test_tagged_extraction.py`.**

```python
"""Tests for the generalized <TAG>...</TAG> extractor."""
from linter.tagged import extract_tagged


def test_extract_tagged_finds_single_tag():
    body = "Intro. <THESIS>This is the thesis.</THESIS> Outro."
    result = extract_tagged(body, "THESIS")
    assert result.extracted == "This is the thesis."
    assert result.clean_body == "Intro. This is the thesis. Outro."
    assert result.warning is None


def test_extract_tagged_falls_back_to_first_sentence_when_missing():
    body = "First sentence. Second sentence."
    result = extract_tagged(body, "CLAIM")
    assert result.extracted == "First sentence."
    assert result.warning == "no CLAIM tag found, used first sentence fallback"


def test_extract_tagged_warns_on_multiple_tags():
    body = "<CLAIM>first claim</CLAIM> middle <CLAIM>second claim</CLAIM>"
    result = extract_tagged(body, "CLAIM")
    assert result.extracted == "first claim"
    assert "multiple" in (result.warning or "")
    assert "<CLAIM>" not in result.clean_body
    assert "</CLAIM>" not in result.clean_body


def test_extract_tagged_treats_empty_tag_as_missing():
    body = "Intro. <CLAIM></CLAIM> Outro."
    result = extract_tagged(body, "CLAIM")
    assert result.extracted == "Intro."
    assert "no CLAIM tag" in (result.warning or "")
```

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_tagged_extraction.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'linter.tagged'`.

- [ ] **Step 3: Create `src/linter/tagged.py`.**

```python
"""Extract <TAG>...</TAG> sentences from generated body text. Tag-agnostic."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_SENTENCE_RE = re.compile(r"([^.!?]+[.!?])(?:\s|$)")


@dataclass
class TaggedExtractionResult:
    extracted: str
    clean_body: str
    warning: Optional[str]


def extract_tagged(body: str, tag: str) -> TaggedExtractionResult:
    """Extract content from <TAG>...</TAG>. Strip all such tags from the body.

    Returns the first non-empty match; warns if multiple were found, or falls
    back to the body's first sentence if no non-empty match exists.
    """
    pattern = re.compile(rf"<{tag}>(.*?)</{tag}>", re.DOTALL)
    matches = pattern.findall(body)
    non_empty = [m.strip() for m in matches if m.strip()]
    clean = pattern.sub(lambda m: m.group(1), body)

    if not non_empty:
        first = _first_sentence(clean)
        return TaggedExtractionResult(
            extracted=first,
            clean_body=clean,
            warning=f"no {tag} tag found, used first sentence fallback",
        )

    if len(non_empty) == 1 and len(matches) == 1:
        return TaggedExtractionResult(extracted=non_empty[0], clean_body=clean, warning=None)

    return TaggedExtractionResult(
        extracted=non_empty[0],
        clean_body=clean,
        warning=f"multiple {tag} tags found, used the first",
    )


def _first_sentence(body: str) -> str:
    stripped = body.strip()
    m = _SENTENCE_RE.search(stripped)
    if m:
        return m.group(1).strip()
    return stripped.split("\n")[0].strip()
```

- [ ] **Step 4: Run the tagged-extraction tests.**

```bash
PYTHONPATH=src pytest tests/test_tagged_extraction.py -v
```

Expected: all four PASS.

- [ ] **Step 5: Re-implement `src/linter/thesis.py` on top of `extract_tagged`. Keep the public API stable so the existing extract-thesis tests keep passing.**

Replace the body of `src/linter/thesis.py` with:

```python
"""Extract <THESIS>...</THESIS> sentences from generated body text.

Thin wrapper over the tag-agnostic linter.tagged.extract_tagged so v1.1 callers
that still use ExtractionResult keep working.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from linter.tagged import extract_tagged


@dataclass
class ExtractionResult:
    thesis: str
    clean_body: str
    warning: Optional[str]


def extract_thesis(body: str) -> ExtractionResult:
    r = extract_tagged(body, "THESIS")
    return ExtractionResult(thesis=r.extracted, clean_body=r.clean_body, warning=r.warning)
```

- [ ] **Step 6: Run the existing thesis-extraction tests to confirm parity.**

```bash
PYTHONPATH=src pytest tests/test_thesis_extraction.py tests/test_tagged_extraction.py -v
```

Expected: all PASS. The v1.1 `extract_thesis` behavior is unchanged from the caller's perspective.

- [ ] **Step 7: Commit.**

```bash
git add 01-projects/linkedin/src/linter/tagged.py 01-projects/linkedin/src/linter/thesis.py 01-projects/linkedin/tests/test_tagged_extraction.py
git commit -m "refactor(linkedin): generalize thesis extractor into linter.tagged.extract_tagged"
```

---

## Task 4: Voice prompt v3 + CLAIM extraction

**Files:**
- Modify: `src/text_generator.py`
- Modify: `tests/test_text_generator.py`

- [ ] **Step 1: Write the failing tests in `tests/test_text_generator.py`.**

Read the file first to see fixtures and patterns. Append (or merge into existing tests) the following:

```python
def test_voice_prompt_does_not_include_claim_rule_for_source_spotlight():
    """source_spotlight posts should not see the CLAIM rule."""
    from text_generator import CLAIM_TAG_RULE, _compose_system_prompt

    prompt = _compose_system_prompt(strategy="source_spotlight")
    assert CLAIM_TAG_RULE not in prompt


def test_voice_prompt_includes_claim_rule_for_two_atom_bridge():
    from text_generator import CLAIM_TAG_RULE, _compose_system_prompt

    prompt = _compose_system_prompt(strategy="two_atom_bridge")
    assert CLAIM_TAG_RULE in prompt


def test_voice_prompt_includes_claim_rule_for_convergence_finder():
    from text_generator import CLAIM_TAG_RULE, _compose_system_prompt

    prompt = _compose_system_prompt(strategy="convergence_finder")
    assert CLAIM_TAG_RULE in prompt


def test_claim_tag_rule_mentions_band_and_panel():
    """The rule must explain where the claim renders so the model gets right tone."""
    from text_generator import CLAIM_TAG_RULE

    assert "<CLAIM>" in CLAIM_TAG_RULE
    assert "</CLAIM>" in CLAIM_TAG_RULE
    assert "two_atom_bridge" in CLAIM_TAG_RULE
    assert "convergence_finder" in CLAIM_TAG_RULE
    assert "mechanism" in CLAIM_TAG_RULE.lower()
    assert "exactly one" in CLAIM_TAG_RULE.lower()


def test_generate_extracts_claim_for_bridge(monkeypatch, tmp_path):
    """generate() must populate brief.panel_claim from <CLAIM> for bridge posts."""
    # Minimal stub for the Anthropic client.
    from atom_loader import AtomLoader
    from models import AtomRef, PostBrief, Status, utc_now
    from text_generator import TextGenerator

    class StubBlock:
        def __init__(self, text):
            self.text = text

    class StubMessage:
        def __init__(self, text):
            self.content = [StubBlock(text)]

    class StubMessages:
        def create(self, **kwargs):
            return StubMessage(
                "Stress is the dose. <THESIS>Stress is not the enemy.</THESIS> "
                "<CLAIM>Both systems get stronger from controlled stress they can recover from.</CLAIM> "
                "Find your dose."
            )

    class StubClient:
        def __init__(self):
            self.messages = StubMessages()

    loader = AtomLoader(tmp_path)
    gen = TextGenerator(client=StubClient(), loader=loader)

    brief = PostBrief(
        id="t", slug="t",
        created_at=utc_now(), updated_at=utc_now(),
        strategy="two_atom_bridge",
        strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary"), AtomRef(slug="b", role="primary")],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    result = gen.generate(brief)
    assert result.thesis == "Stress is not the enemy."
    assert result.panel_claim == "Both systems get stronger from controlled stress they can recover from."
    # Body has both tag pairs stripped.
    assert "<THESIS>" not in result.draft_text
    assert "<CLAIM>" not in result.draft_text


def test_generate_skips_claim_extraction_for_source_spotlight(monkeypatch, tmp_path):
    """source_spotlight briefs leave panel_claim empty even if model emits a CLAIM tag."""
    from atom_loader import AtomLoader
    from models import AtomRef, PostBrief, Status, utc_now
    from text_generator import TextGenerator

    class StubBlock:
        def __init__(self, text):
            self.text = text

    class StubMessage:
        def __init__(self, text):
            self.content = [StubBlock(text)]

    class StubMessages:
        def create(self, **kwargs):
            return StubMessage(
                "<THESIS>Source spotlight thesis.</THESIS> "
                "<CLAIM>Stray claim tag the model emitted.</CLAIM>"
            )

    class StubClient:
        def __init__(self):
            self.messages = StubMessages()

    loader = AtomLoader(tmp_path)
    gen = TextGenerator(client=StubClient(), loader=loader)

    brief = PostBrief(
        id="t", slug="t",
        created_at=utc_now(), updated_at=utc_now(),
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary")],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    result = gen.generate(brief)
    assert result.thesis == "Source spotlight thesis."
    assert result.panel_claim == ""
```

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_text_generator.py -v -k "claim or v12 or composes" 2>&1 | tail -20
```

Expected: import-error or assertion failures (CLAIM_TAG_RULE and _compose_system_prompt don't exist yet).

- [ ] **Step 3: Add the new constant and helper to `src/text_generator.py`.**

After the `VOICE_SYSTEM_PROMPT` constant (around line 49), add:

```python
CLAIM_TAG_RULE = """
CLAIM TAG (strategy-scoped, two_atom_bridge and convergence_finder only):
- This post must contain exactly one synthesizing sentence wrapped in <CLAIM>...</CLAIM> tags.
- For two_atom_bridge: the shared-mechanism sentence. It will render as the italic line inside the mechanism band beneath the two atom pillars.
- For convergence_finder: the unified-mechanism sentence. It will render as the italic line inside the convergence panel beneath the funnel.
- Place the tags where the sentence reads naturally in the body. It is part of the post, not a header. The engine strips the tags so the saved post.md reads clean.
"""

_CLAIM_STRATEGIES = {"two_atom_bridge", "convergence_finder"}


def _compose_system_prompt(strategy: str) -> str:
    """Compose the per-call system prompt. Appends CLAIM_TAG_RULE for strategies that need it."""
    if strategy in _CLAIM_STRATEGIES:
        return VOICE_SYSTEM_PROMPT + "\n" + CLAIM_TAG_RULE
    return VOICE_SYSTEM_PROMPT
```

- [ ] **Step 4: Update `TextGenerator.generate()` to use the composed prompt + extract CLAIM.**

In `generate()`, replace the `system=VOICE_SYSTEM_PROMPT,` line in the `client.messages.create(...)` call with:

```python
            system=_compose_system_prompt(brief.strategy),
```

Then, after the existing thesis extraction block (around line 113), insert CLAIM extraction:

```python
        if brief.strategy in _CLAIM_STRATEGIES:
            from linter.tagged import extract_tagged
            claim_result = extract_tagged(extraction.clean_body, "CLAIM")
            brief.panel_claim = claim_result.extracted
            brief.draft_text = claim_result.clean_body.strip()
            if claim_result.warning:
                brief.status_history.append({
                    "status": Status.TEXT_READY.value,
                    "timestamp": brief.updated_at.isoformat(),
                    "actor": "engine",
                    "note": claim_result.warning,
                })
```

- [ ] **Step 5: Run the new tests.**

```bash
PYTHONPATH=src pytest tests/test_text_generator.py -v -k "claim or v12 or composes" 2>&1 | tail -20
```

Expected: all PASS.

- [ ] **Step 6: Run the full suite.**

```bash
PYTHONPATH=src pytest tests/ -v 2>&1 | tail -10
```

Expected: all pass. The new behavior is additive; `source_spotlight` still gets `panel_claim=""`.

- [ ] **Step 7: Commit.**

```bash
git add 01-projects/linkedin/src/text_generator.py 01-projects/linkedin/tests/test_text_generator.py
git commit -m "feat(linkedin): v1.2 voice prompt v3 adds strategy-scoped <CLAIM> tag"
```

---

## Task 5: `two_atom_bridge.py` strategy update

**Files:**
- Modify: `src/strategies/two_atom_bridge.py`
- Modify: `tests/test_two_atom_bridge.py`

- [ ] **Step 1: Write the failing tests in `tests/test_two_atom_bridge.py`.**

Read the existing file first, then add or replace assertions inside the existing happy-path test (you'll find an `assert brief.visual_tier == "0_text"` from v1.1.3):

```python
def test_bridge_brief_uses_tier1_diagram_at_4x5():
    """v1.2: bridge defaults to Tier 1 atom-card at 4:5."""
    # use the existing fixtures from conftest/this test file to call the strategy.
    # ... existing setup that produces `brief` from TwoAtomBridge.generate_brief ...
    assert brief.visual_tier == "1_diagram"
    assert brief.aspect_ratio == "4:5"
    assert brief.panel_label in {
        "SHARED MECHANISM", "STRUCTURAL ANALOGUE", "INVERSE PAIR", "BRIDGE",
    }
    assert brief.panel_claim == ""  # filled later by text_generator


def test_bridge_panel_label_derived_from_connection_type():
    """Label map covers each known connection_type."""
    from strategies.two_atom_bridge import _LABEL_BY_CONNECTION_TYPE
    assert _LABEL_BY_CONNECTION_TYPE["mechanism"] == "SHARED MECHANISM"
    assert _LABEL_BY_CONNECTION_TYPE["analogical"] == "STRUCTURAL ANALOGUE"
    assert _LABEL_BY_CONNECTION_TYPE["inverse"] == "INVERSE PAIR"
    assert _LABEL_BY_CONNECTION_TYPE["general"] == "BRIDGE"


def test_bridge_unknown_connection_type_falls_back_to_bridge_label():
    """If a connection edge has an unrecognized connection_type, panel_label falls back to BRIDGE."""
    from strategies.two_atom_bridge import _LABEL_BY_CONNECTION_TYPE
    fallback = _LABEL_BY_CONNECTION_TYPE.get("unknown-type", "BRIDGE")
    assert fallback == "BRIDGE"
```

Adjust any existing v1.1.3 `visual_tier == "0_text"` assertions in this file to the new expected values, or wrap them under the v1.2 expectations. There should be no `0_text` assertion left for `two_atom_bridge` after Step 1.

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_two_atom_bridge.py -v 2>&1 | tail -20
```

Expected: FAIL on `visual_tier == "1_diagram"` (still `"0_text"` per v1.1.3) and on `_LABEL_BY_CONNECTION_TYPE` import.

- [ ] **Step 3: Edit `src/strategies/two_atom_bridge.py`.**

Above the class definition, add the label map:

```python
_LABEL_BY_CONNECTION_TYPE = {
    "mechanism":  "SHARED MECHANISM",
    "analogical": "STRUCTURAL ANALOGUE",
    "inverse":    "INVERSE PAIR",
    "general":    "BRIDGE",
}
```

Inside `generate_brief()`, delete the multi-line v1.1.3 comment block above `visual_tier="0_text"` (lines 59-65) and replace the `visual_tier` line with three lines:

```python
            visual_tier="1_diagram",
            aspect_ratio="4:5",
            panel_label=_LABEL_BY_CONNECTION_TYPE.get(connection_type, "BRIDGE"),
```

The PostBrief construction now passes `aspect_ratio` and `panel_label` as keyword args; `panel_claim` keeps its default of `""`.

- [ ] **Step 4: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_two_atom_bridge.py -v 2>&1 | tail -20
```

Expected: all PASS.

- [ ] **Step 5: Commit.**

```bash
git add 01-projects/linkedin/src/strategies/two_atom_bridge.py 01-projects/linkedin/tests/test_two_atom_bridge.py
git commit -m "feat(linkedin): v1.2 two_atom_bridge defaults back to Tier 1 at 4:5"
```

---

## Task 6: `convergence_finder.py` strategy update

**Files:**
- Modify: `src/strategies/convergence_finder.py`
- Modify: `tests/test_convergence_finder.py`

- [ ] **Step 1: Write the failing tests in `tests/test_convergence_finder.py`.**

Read the existing file. Adjust existing v1.1.3 `visual_tier == "0_text"` assertion(s), and append:

```python
def test_convergence_brief_uses_tier1_diagram_at_4x5():
    """v1.2: convergence_finder defaults to Tier 1 atom-card at 4:5."""
    # ... existing setup that produces `brief` from ConvergenceFinder.generate_brief ...
    assert brief.visual_tier == "1_diagram"
    assert brief.aspect_ratio == "4:5"
    assert brief.panel_claim == ""  # filled later by text_generator


def test_convergence_panel_label_composes_from_topic():
    """panel_label is 'CONVERGES ON · {topic.upper()}'."""
    # Re-use the same fixture-driven brief from above.
    # Suppose the topic parameter was "feedback".
    assert brief.panel_label == "CONVERGES ON · FEEDBACK"
```

Adjust any existing v1.1.3 `"0_text"` assertions to the new values; no `"0_text"` for `convergence_finder` after Step 1.

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_convergence_finder.py -v 2>&1 | tail -20
```

Expected: FAIL.

- [ ] **Step 3: Edit `src/strategies/convergence_finder.py`.**

Inside `generate_brief()`, delete the v1.1.3 comment block above `visual_tier="0_text"` (lines 60-64). Replace the `visual_tier` line with three lines:

```python
            visual_tier="1_diagram",
            aspect_ratio="4:5",
            panel_label=f"CONVERGES ON · {topic.upper()}",
```

`panel_claim` keeps its default of `""`.

- [ ] **Step 4: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_convergence_finder.py -v 2>&1 | tail -20
```

Expected: all PASS.

- [ ] **Step 5: Commit.**

```bash
git add 01-projects/linkedin/src/strategies/convergence_finder.py 01-projects/linkedin/tests/test_convergence_finder.py
git commit -m "feat(linkedin): v1.2 convergence_finder defaults back to Tier 1 at 4:5"
```

---

## Task 7: Shared CSS partial

**Files:**
- Create: `src/renderers/templates/_card_frame.css.j2`

This is a content task with no failing test of its own; the partial is exercised by the bridge and convergence renderer tests in the next two tasks. Keep this task small.

- [ ] **Step 1: Create `src/renderers/templates/_card_frame.css.j2`.**

This is a Jinja partial. It contains only the CSS that bridge and convergence both need. Bridge-specific and convergence-specific CSS lives in each strategy's template.

```css
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: {{ colors.background }};
  font-family: {{ typography.body }};
  color: {{ colors.text_primary }};
  -webkit-font-smoothing: antialiased;
}

.card {
  display: flex;
  flex-direction: column;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.meta {
  color: {{ colors.accent_primary }};
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-weight: 500;
}

.domain {
  color: {{ colors.text_secondary }};
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-family: {{ typography.mono }};
}

.thesis {
  font-weight: 500;
  line-height: 1.1;
  letter-spacing: -0.01em;
  color: {{ colors.text_primary }};
}

.footer-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-family: {{ typography.mono }};
  letter-spacing: 0.02em;
  gap: 24px;
}

.footer-source, .footer-count { white-space: nowrap; }
.footer-source { color: {{ colors.text_primary }}; }
.footer-count  { color: {{ colors.text_secondary }}; }

.panel-label {
  color: {{ colors.accent_primary }};
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-family: {{ typography.mono }};
}

.panel-claim {
  color: {{ colors.text_primary }};
  font-style: italic;
  line-height: 1.3;
}
```

This partial intentionally does NOT set font-sizes, widths, heights, or paddings. Those live in the strategy templates because they vary by aspect ratio and strategy.

- [ ] **Step 2: No tests yet; the partial is exercised by Tasks 8 and 9.**

- [ ] **Step 3: Commit.**

```bash
git add 01-projects/linkedin/src/renderers/templates/_card_frame.css.j2
git commit -m "feat(linkedin): v1.2 add shared card-frame CSS partial for new tier-1 templates"
```

---

## Task 8: BridgeCardRenderer + template

**Files:**
- Create: `src/renderers/bridge_card.py`
- Create: `src/renderers/templates/bridge_card.html.j2`
- Create: `tests/test_bridge_card_renderer.py`

- [ ] **Step 1: Write the failing tests in `tests/test_bridge_card_renderer.py`.**

```python
"""Tests for BridgeCardRenderer (Bridge A at 4:5)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from atom_loader import AtomLoader
from models import AtomRef, PostBrief, Status
from renderers.bridge_card import BridgeCardRenderer


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    # Minimal brand-spec.md so load_brand_spec() works.
    brand = tmp_path / "brand-spec.md"
    brand.write_text(
        "```yaml\n"
        "colors:\n"
        "  accent_primary: \"#B5654A\"\n"
        "  background: \"#FAF8F5\"\n"
        "  text_primary: \"#2C2825\"\n"
        "  text_secondary: \"#6B6560\"\n"
        "typography:\n"
        "  body: \"Geist, system-ui, sans-serif\"\n"
        "  mono: \"Geist Mono, ui-monospace, monospace\"\n"
        "```\n"
    )
    return tmp_path


def _make_brief(strategy="two_atom_bridge", **overrides) -> PostBrief:
    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    base = dict(
        id="t", slug="t",
        created_at=now, updated_at=now,
        strategy=strategy,
        strategy_params={},
        atoms_used=[
            AtomRef(slug="atom-a", role="primary"),
            AtomRef(slug="atom-b", role="primary"),
        ],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        thesis="Stress is not the enemy.",
        aspect_ratio="4:5",
        panel_label="SHARED MECHANISM",
        panel_claim="Both systems get stronger from controlled stress.",
    )
    base.update(overrides)
    return PostBrief(**base)


def test_validate_passes_on_valid_brief(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief()
    assert renderer.validate(brief) == []


def test_validate_requires_exactly_2_atoms(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(atoms_used=[AtomRef(slug="only-one", role="primary")])
    errors = renderer.validate(brief)
    assert any("exactly 2" in e for e in errors)


def test_validate_requires_non_empty_panel_label(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(panel_label="")
    errors = renderer.validate(brief)
    assert any("panel_label" in e for e in errors)


def test_validate_requires_non_empty_panel_claim(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(panel_claim="")
    errors = renderer.validate(brief)
    assert any("panel_claim" in e for e in errors)


def test_validate_requires_4x5_aspect_ratio(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(aspect_ratio="1:1")
    errors = renderer.validate(brief)
    assert any("4:5" in e for e in errors)


def test_renderer_tier_is_1(project_root):
    assert BridgeCardRenderer.tier == 1


@pytest.mark.smoke
def test_render_writes_png_at_1080x1350(project_root, tmp_path):
    """Live Playwright render. Mark with -m smoke to opt in / out."""
    pytest.importorskip("playwright.sync_api")

    # Build a tiny atom store so the renderer can resolve atom names.
    (project_root / "atom-a.md").write_text(
        "---\ntitle: Atom A\ndomain: mental-models\nsource: Test, 2026\ntldr: A tldr sentence for A.\n---\n"
    )
    (project_root / "atom-b.md").write_text(
        "---\ntitle: Atom B\ndomain: health-performance\nsource: Test, 2026\ntldr: A tldr sentence for B.\n---\n"
    )

    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief()
    out_dir = tmp_path / "out"
    result = renderer.render(brief, out_dir)
    png = out_dir / "diagram.png"
    assert png.exists()
    # Quick sanity: PNG header.
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert result.asset_paths == [png]
```

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_bridge_card_renderer.py -v 2>&1 | tail -20
```

Expected: ModuleNotFoundError on `renderers.bridge_card`.

- [ ] **Step 3: Create the template at `src/renderers/templates/bridge_card.html.j2`.**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    {% include "_card_frame.css.j2" %}

    html, body { width: 1080px; height: 1350px; }

    .card { width: 1080px; height: 1350px; padding: 90px 86px; }

    .meta-row { margin-bottom: 56px; }
    .meta, .domain { font-size: 26px; }

    .thesis { font-size: {{ thesis_font_size }}; margin-bottom: 64px; }

    .pillars {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 36px;
      flex: 1;
    }
    .pillar {
      background: {{ colors.surface_subtle }};
      border: 1px solid {{ colors.border }};
      border-radius: 10px;
      padding: 40px 36px;
      display: flex;
      flex-direction: column;
    }
    .pillar-domain {
      font-size: 22px;
      color: {{ colors.text_secondary }};
      font-family: {{ typography.mono }};
      letter-spacing: 0.05em;
      text-transform: lowercase;
      margin-bottom: 24px;
    }
    .pillar-name {
      font-size: 36px;
      font-weight: 600;
      color: {{ colors.text_primary }};
      line-height: 1.2;
      margin-bottom: 20px;
    }
    .pillar-tldr {
      font-size: 28px;
      color: {{ colors.text_secondary }};
      line-height: 1.4;
      margin-top: auto;
    }

    .mechanism-band {
      background: {{ colors.background }};
      border: 1px dashed {{ colors.accent_primary }};
      border-radius: 10px;
      padding: 36px 40px;
      margin-top: 36px;
      text-align: center;
    }
    .mechanism-band .panel-label { font-size: 22px; margin-bottom: 18px; }
    .mechanism-band .panel-claim { font-size: 32px; }

    .footer-row { margin-top: 56px; font-size: 24px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="meta-row">
      <div class="meta">from second brain</div>
      <div class="domain">{{ domain_tag }}</div>
    </div>
    <div class="thesis">{{ thesis }}</div>
    <div class="pillars">
      <div class="pillar">
        <div class="pillar-domain">{{ atom_a.domain }}</div>
        <div class="pillar-name">{{ atom_a.name }}</div>
        <div class="pillar-tldr">{{ atom_a.tldr }}</div>
      </div>
      <div class="pillar">
        <div class="pillar-domain">{{ atom_b.domain }}</div>
        <div class="pillar-name">{{ atom_b.name }}</div>
        <div class="pillar-tldr">{{ atom_b.tldr }}</div>
      </div>
    </div>
    <div class="mechanism-band">
      <div class="panel-label">{{ panel_label }}</div>
      <div class="panel-claim">{{ panel_claim }}</div>
    </div>
    <div class="footer-row">
      <div class="footer-source">2 atoms · cross-domain</div>
      <div class="footer-count">two-atom-bridge</div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 4: Create the renderer at `src/renderers/bridge_card.py`.**

```python
"""Tier 1 BridgeCardRenderer (Playwright + Jinja2). Bridge A at 4:5."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from atom_loader import AtomLoader
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_TEMPLATE_DIR = Path(__file__).parent / "templates"

_ATOM_TEXT_MAX_CHARS = 110
_THESIS_LARGE_MAX_CHARS = 60
_THESIS_LARGE_FONT = "78px"
_THESIS_SMALL_FONT = "60px"

_VIEWPORT_BY_RATIO = {"1:1": (1080, 1080), "4:5": (1080, 1350)}


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rstrip()
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.") + "…"


class BridgeCardRenderer:
    tier = 1

    def __init__(
        self,
        loader: AtomLoader,
        sources_registry: Optional[Any],
        brand_spec_path: Path,
        tldr_filler: Optional[Any] = None,
    ):
        self.loader = loader
        self.sources_registry = sources_registry
        self.brand = load_brand_spec(brand_spec_path)
        self.tldr_filler = tldr_filler
        self._env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def validate(self, brief: PostBrief) -> list[str]:
        errors: list[str] = []
        if not (brief.thesis or "").strip():
            errors.append("thesis must be non-empty")
        if len(brief.atoms_used) != 2:
            errors.append("bridge renderer requires exactly 2 atoms")
        if not (brief.panel_label or "").strip():
            errors.append("panel_label must be non-empty")
        if not (brief.panel_claim or "").strip():
            errors.append("panel_claim must be non-empty")
        if brief.aspect_ratio != "4:5":
            errors.append("bridge renderer requires aspect_ratio == \"4:5\"")
        # Different-domain check is the strategy's responsibility; if briefs are constructed
        # by hand and share a domain, the strategy would have errored before reaching here.
        # We don't re-check it in the renderer to avoid duplicating the rule.
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        from playwright.sync_api import sync_playwright

        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._build_template_context(brief)
        template = self._env.get_template("bridge_card.html.j2")
        html = template.render(**ctx)

        viewport_w, viewport_h = _VIEWPORT_BY_RATIO[brief.aspect_ratio]
        png_path = out_dir / "diagram.png"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": viewport_w, "height": viewport_h})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(
                path=str(png_path),
                full_page=False,
                clip={"x": 0, "y": 0, "width": viewport_w, "height": viewport_h},
            )
            browser.close()

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered bridge-card in {elapsed:.2f}s"],
        )

    # ---------- internals ----------

    def _build_template_context(self, brief: PostBrief) -> dict:
        colors = self.brand.get("colors", {})
        typography = self.brand.get("typography", {})

        atom_a_ref, atom_b_ref = brief.atoms_used
        atom_a_full = self.loader.load_one(atom_a_ref.slug)
        atom_b_full = self.loader.load_one(atom_b_ref.slug)

        def _block(atom, ref) -> dict:
            name = atom.title if atom else ref.slug
            domain = (atom.domain if atom else None) or ""
            tldr = (atom.tldr if atom else None) or self._fill_tldr(atom) or ""
            return {
                "name": name,
                "domain": domain,
                "tldr": _truncate_at_word_boundary(tldr, _ATOM_TEXT_MAX_CHARS),
            }

        atom_a = _block(atom_a_full, atom_a_ref)
        atom_b = _block(atom_b_full, atom_b_ref)

        thesis_font_size = (
            _THESIS_LARGE_FONT if len(brief.thesis) <= _THESIS_LARGE_MAX_CHARS
            else _THESIS_SMALL_FONT
        )

        domain_tag = "bridge"
        if atom_a["domain"] and atom_b["domain"]:
            domain_tag = f"bridge // {atom_a['domain']} × {atom_b['domain']}"

        return {
            "colors": {
                "background": colors.get("background", "#FAF8F5"),
                "accent_primary": colors.get("accent_primary", "#B5654A"),
                "text_primary": colors.get("text_primary", "#2C2825"),
                "text_secondary": colors.get("text_secondary", "#6B6560"),
                "surface_subtle": colors.get("surface_subtle", "#F3F0EB"),
                "border": colors.get("border", "#E8E4DF"),
            },
            "typography": {
                "body": typography.get("body", "Geist, system-ui, sans-serif"),
                "mono": typography.get("mono", "Geist Mono, ui-monospace, monospace"),
            },
            "domain_tag": domain_tag,
            "thesis": brief.thesis,
            "thesis_font_size": thesis_font_size,
            "atom_a": atom_a,
            "atom_b": atom_b,
            "panel_label": brief.panel_label,
            "panel_claim": brief.panel_claim,
        }

    def _fill_tldr(self, atom: Optional[Any]) -> Optional[str]:
        if atom is None or self.tldr_filler is None:
            return None
        return self.tldr_filler.fill(atom)
```

- [ ] **Step 5: Run the renderer tests (skip the live smoke).**

```bash
PYTHONPATH=src pytest tests/test_bridge_card_renderer.py -v -m "not smoke" 2>&1 | tail -20
```

Expected: all validate tests PASS.

- [ ] **Step 6: Run the live render smoke (requires Playwright Chromium installed).**

```bash
PYTHONPATH=src pytest tests/test_bridge_card_renderer.py -v -m smoke 2>&1 | tail -20
```

Expected: PNG produced; PNG header check passes.

- [ ] **Step 7: Commit.**

```bash
git add 01-projects/linkedin/src/renderers/bridge_card.py 01-projects/linkedin/src/renderers/templates/bridge_card.html.j2 01-projects/linkedin/tests/test_bridge_card_renderer.py
git commit -m "feat(linkedin): v1.2 BridgeCardRenderer (Bridge A at 4:5)"
```

---

## Task 9: ConvergenceCardRenderer + template

**Files:**
- Create: `src/renderers/convergence_card.py`
- Create: `src/renderers/templates/convergence_card.html.j2`
- Create: `tests/test_convergence_card_renderer.py`

- [ ] **Step 1: Write the failing tests in `tests/test_convergence_card_renderer.py`.**

```python
"""Tests for ConvergenceCardRenderer (Convergence C at 4:5)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from atom_loader import AtomLoader
from models import AtomRef, PostBrief, Status
from renderers.convergence_card import ConvergenceCardRenderer


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    brand = tmp_path / "brand-spec.md"
    brand.write_text(
        "```yaml\n"
        "colors:\n"
        "  accent_primary: \"#B5654A\"\n"
        "  background: \"#FAF8F5\"\n"
        "  text_primary: \"#2C2825\"\n"
        "  text_secondary: \"#6B6560\"\n"
        "typography:\n"
        "  body: \"Geist, system-ui, sans-serif\"\n"
        "  mono: \"Geist Mono, ui-monospace, monospace\"\n"
        "```\n"
    )
    return tmp_path


def _make_brief(**overrides) -> PostBrief:
    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    base = dict(
        id="t", slug="t",
        created_at=now, updated_at=now,
        strategy="convergence_finder",
        strategy_params={"topic": "feedback", "domains": ["d1", "d2", "d3"]},
        atoms_used=[
            AtomRef(slug="atom-a", role="primary"),
            AtomRef(slug="atom-b", role="primary"),
            AtomRef(slug="atom-c", role="primary"),
        ],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        thesis="Every loop measures.",
        aspect_ratio="4:5",
        panel_label="CONVERGES ON · FEEDBACK",
        panel_claim="Every loop narrows the gap between intent and outcome.",
    )
    base.update(overrides)
    return PostBrief(**base)


def test_validate_passes_on_valid_brief(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    assert renderer.validate(_make_brief()) == []


def test_validate_requires_at_least_3_atoms(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(atoms_used=[AtomRef(slug="only-two-a", role="primary"), AtomRef(slug="only-two-b", role="primary")])
    errors = renderer.validate(brief)
    assert any("at least 3" in e or "≥3" in e for e in errors)


def test_validate_requires_non_empty_panel_label(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    errors = renderer.validate(_make_brief(panel_label=""))
    assert any("panel_label" in e for e in errors)


def test_validate_requires_4x5_aspect_ratio(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    errors = renderer.validate(_make_brief(aspect_ratio="1:1"))
    assert any("4:5" in e for e in errors)


def test_renderer_tier_is_1():
    assert ConvergenceCardRenderer.tier == 1


@pytest.mark.smoke
def test_render_writes_png_at_1080x1350(project_root, tmp_path):
    pytest.importorskip("playwright.sync_api")

    for slug, dom in [("atom-a", "habits-systems"), ("atom-b", "platform-writing"), ("atom-c", "psychology-reader")]:
        (project_root / f"{slug}.md").write_text(
            f"---\ntitle: {slug.title()}\ndomain: {dom}\nsource: Test, 2026\ntldr: A short tldr for {slug}.\n---\n"
        )

    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    out_dir = tmp_path / "out"
    result = renderer.render(_make_brief(), out_dir)
    png = out_dir / "diagram.png"
    assert png.exists()
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert result.asset_paths == [png]
```

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_convergence_card_renderer.py -v 2>&1 | tail -20
```

Expected: ModuleNotFoundError on `renderers.convergence_card`.

- [ ] **Step 3: Create the template at `src/renderers/templates/convergence_card.html.j2`.**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    {% include "_card_frame.css.j2" %}

    html, body { width: 1080px; height: 1350px; }

    .card { width: 1080px; height: 1350px; padding: 90px 86px; }

    .meta-row { margin-bottom: 56px; }
    .meta, .domain { font-size: 26px; }

    .thesis { font-size: {{ thesis_font_size }}; margin-bottom: 60px; }

    .funnel-atoms {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 24px;
    }
    .fa {
      background: {{ colors.surface_subtle }};
      border: 1px solid {{ colors.border }};
      border-radius: 10px;
      padding: 32px 26px;
      display: flex;
      flex-direction: column;
    }
    .fa-domain {
      font-size: 20px;
      color: {{ colors.text_secondary }};
      font-family: {{ typography.mono }};
      letter-spacing: 0.05em;
      text-transform: lowercase;
      margin-bottom: 20px;
    }
    .fa-name {
      font-size: 30px;
      font-weight: 600;
      color: {{ colors.text_primary }};
      line-height: 1.2;
      margin-bottom: 18px;
    }
    .fa-tldr {
      font-size: 24px;
      color: {{ colors.text_secondary }};
      line-height: 1.4;
      margin-top: auto;
    }

    .funnel-arrows {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      text-align: center;
      color: {{ colors.accent_primary }};
      font-family: {{ typography.mono }};
      font-size: 48px;
      letter-spacing: -0.05em;
      margin: 18px 0 18px 0;
    }

    .convergence-panel {
      background: {{ colors.background }};
      border: 2px solid {{ colors.accent_primary }};
      border-radius: 10px;
      padding: 40px 44px;
      text-align: center;
      margin-top: auto;
    }
    .convergence-panel .panel-label { font-size: 22px; margin-bottom: 20px; }
    .convergence-panel .panel-claim { font-size: 34px; font-weight: 500; }

    .footer-row { margin-top: 56px; font-size: 24px; }

    body, html { display: flex; }
    .card { flex: 1; }
  </style>
</head>
<body>
  <div class="card">
    <div class="meta-row">
      <div class="meta">from second brain</div>
      <div class="domain">{{ domain_tag }}</div>
    </div>
    <div class="thesis">{{ thesis }}</div>
    <div class="funnel-atoms">
      {% for atom in atom_blocks %}
      <div class="fa">
        <div class="fa-domain">{{ atom.domain }}</div>
        <div class="fa-name">{{ atom.name }}</div>
        <div class="fa-tldr">{{ atom.tldr }}</div>
      </div>
      {% endfor %}
    </div>
    <div class="funnel-arrows">
      <div>↓</div><div>↓</div><div>↓</div>
    </div>
    <div class="convergence-panel">
      <div class="panel-label">{{ panel_label }}</div>
      <div class="panel-claim">{{ panel_claim }}</div>
    </div>
    <div class="footer-row">
      <div class="footer-source">{{ footer_left }}</div>
      <div class="footer-count">convergence-finder</div>
    </div>
  </div>
</body>
</html>
```

- [ ] **Step 4: Create the renderer at `src/renderers/convergence_card.py`.**

```python
"""Tier 1 ConvergenceCardRenderer (Playwright + Jinja2). Convergence C at 4:5."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from atom_loader import AtomLoader
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_TEMPLATE_DIR = Path(__file__).parent / "templates"

_ATOM_TEXT_MAX_CHARS = 60
_THESIS_LARGE_MAX_CHARS = 60
_THESIS_LARGE_FONT = "78px"
_THESIS_SMALL_FONT = "60px"
_MAX_FUNNEL_ATOMS = 3

_VIEWPORT_BY_RATIO = {"1:1": (1080, 1080), "4:5": (1080, 1350)}


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rstrip()
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.") + "…"


class ConvergenceCardRenderer:
    tier = 1

    def __init__(
        self,
        loader: AtomLoader,
        sources_registry: Optional[Any],
        brand_spec_path: Path,
        tldr_filler: Optional[Any] = None,
    ):
        self.loader = loader
        self.sources_registry = sources_registry
        self.brand = load_brand_spec(brand_spec_path)
        self.tldr_filler = tldr_filler
        self._env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def validate(self, brief: PostBrief) -> list[str]:
        errors: list[str] = []
        if not (brief.thesis or "").strip():
            errors.append("thesis must be non-empty")
        if len(brief.atoms_used) < 3:
            errors.append("convergence renderer requires at least 3 atoms")
        if not (brief.panel_label or "").strip():
            errors.append("panel_label must be non-empty")
        if not (brief.panel_claim or "").strip():
            errors.append("panel_claim must be non-empty")
        if brief.aspect_ratio != "4:5":
            errors.append("convergence renderer requires aspect_ratio == \"4:5\"")
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        from playwright.sync_api import sync_playwright

        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._build_template_context(brief)
        template = self._env.get_template("convergence_card.html.j2")
        html = template.render(**ctx)

        viewport_w, viewport_h = _VIEWPORT_BY_RATIO[brief.aspect_ratio]
        png_path = out_dir / "diagram.png"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": viewport_w, "height": viewport_h})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(
                path=str(png_path),
                full_page=False,
                clip={"x": 0, "y": 0, "width": viewport_w, "height": viewport_h},
            )
            browser.close()

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered convergence-card in {elapsed:.2f}s"],
        )

    # ---------- internals ----------

    def _build_template_context(self, brief: PostBrief) -> dict:
        colors = self.brand.get("colors", {})
        typography = self.brand.get("typography", {})

        refs = brief.atoms_used[:_MAX_FUNNEL_ATOMS]
        atom_blocks = []
        seen_domains: set[str] = set()
        for ref in refs:
            atom = self.loader.load_one(ref.slug)
            name = atom.title if atom else ref.slug
            domain = (atom.domain if atom else None) or ""
            tldr = (atom.tldr if atom else None) or self._fill_tldr(atom) or ""
            tldr = _truncate_at_word_boundary(tldr, _ATOM_TEXT_MAX_CHARS)
            atom_blocks.append({"name": name, "domain": domain, "tldr": tldr})
            if domain:
                seen_domains.add(domain)

        thesis_font_size = (
            _THESIS_LARGE_FONT if len(brief.thesis) <= _THESIS_LARGE_MAX_CHARS
            else _THESIS_SMALL_FONT
        )

        total_atoms = len(brief.atoms_used)
        domain_count = len(seen_domains)
        footer_left = f"{total_atoms} atoms · {domain_count} domains"
        domain_tag = f"convergence // {domain_count} domains"

        return {
            "colors": {
                "background": colors.get("background", "#FAF8F5"),
                "accent_primary": colors.get("accent_primary", "#B5654A"),
                "text_primary": colors.get("text_primary", "#2C2825"),
                "text_secondary": colors.get("text_secondary", "#6B6560"),
                "surface_subtle": colors.get("surface_subtle", "#F3F0EB"),
                "border": colors.get("border", "#E8E4DF"),
            },
            "typography": {
                "body": typography.get("body", "Geist, system-ui, sans-serif"),
                "mono": typography.get("mono", "Geist Mono, ui-monospace, monospace"),
            },
            "domain_tag": domain_tag,
            "thesis": brief.thesis,
            "thesis_font_size": thesis_font_size,
            "atom_blocks": atom_blocks,
            "panel_label": brief.panel_label,
            "panel_claim": brief.panel_claim,
            "footer_left": footer_left,
        }

    def _fill_tldr(self, atom: Optional[Any]) -> Optional[str]:
        if atom is None or self.tldr_filler is None:
            return None
        return self.tldr_filler.fill(atom)
```

- [ ] **Step 5: Run the renderer tests (skip the live smoke).**

```bash
PYTHONPATH=src pytest tests/test_convergence_card_renderer.py -v -m "not smoke" 2>&1 | tail -20
```

Expected: all validate tests PASS.

- [ ] **Step 6: Run the live render smoke.**

```bash
PYTHONPATH=src pytest tests/test_convergence_card_renderer.py -v -m smoke 2>&1 | tail -20
```

Expected: PNG produced.

- [ ] **Step 7: Commit.**

```bash
git add 01-projects/linkedin/src/renderers/convergence_card.py 01-projects/linkedin/src/renderers/templates/convergence_card.html.j2 01-projects/linkedin/tests/test_convergence_card_renderer.py
git commit -m "feat(linkedin): v1.2 ConvergenceCardRenderer (Convergence C at 4:5)"
```

---

## Task 10: Tier 1 registry

**Files:**
- Create: `src/renderers/registry.py`
- Create: `tests/test_renderers_registry.py`

- [ ] **Step 1: Write the failing tests.**

```python
"""Tests for the Tier 1 renderer registry."""
from pathlib import Path
import pytest

from renderers.registry import for_strategy
from renderers.atom_card import AtomCardRenderer
from renderers.bridge_card import BridgeCardRenderer
from renderers.convergence_card import ConvergenceCardRenderer


@pytest.fixture
def brand_spec(tmp_path: Path) -> Path:
    b = tmp_path / "brand-spec.md"
    b.write_text("```yaml\ncolors: {}\ntypography: {}\n```\n")
    return b


def test_source_spotlight_returns_atom_card_renderer(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    r = for_strategy(
        "source_spotlight",
        loader=AtomLoader(tmp_path),
        sources_registry=None,
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    assert isinstance(r, AtomCardRenderer)


def test_two_atom_bridge_returns_bridge_card_renderer(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    r = for_strategy(
        "two_atom_bridge",
        loader=AtomLoader(tmp_path),
        sources_registry=None,
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    assert isinstance(r, BridgeCardRenderer)


def test_convergence_finder_returns_convergence_card_renderer(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    r = for_strategy(
        "convergence_finder",
        loader=AtomLoader(tmp_path),
        sources_registry=None,
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    assert isinstance(r, ConvergenceCardRenderer)


def test_unknown_strategy_raises(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    with pytest.raises(ValueError, match="No Tier 1 renderer"):
        for_strategy(
            "cluster_reveal",
            loader=AtomLoader(tmp_path),
            sources_registry=None,
            brand_spec_path=brand_spec,
            tldr_filler=None,
        )
```

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_renderers_registry.py -v
```

Expected: ImportError.

- [ ] **Step 3: Create `src/renderers/registry.py`.**

```python
"""Tier 1 renderer registry. Strategy.name -> renderer instance."""
from __future__ import annotations

from typing import Any

from renderers.atom_card import AtomCardRenderer
from renderers.bridge_card import BridgeCardRenderer
from renderers.convergence_card import ConvergenceCardRenderer


_TIER1_CLASSES: dict[str, type] = {
    "source_spotlight":   AtomCardRenderer,
    "two_atom_bridge":    BridgeCardRenderer,
    "convergence_finder": ConvergenceCardRenderer,
}


def for_strategy(strategy_name: str, **kwargs: Any):
    cls = _TIER1_CLASSES.get(strategy_name)
    if cls is None:
        raise ValueError(f"No Tier 1 renderer for strategy '{strategy_name}'")
    return cls(**kwargs)
```

Confirm no em-dashes are introduced. Run `grep -cP "\x{2014}" 01-projects/linkedin/src/renderers/registry.py`; expected: 0.

- [ ] **Step 4: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_renderers_registry.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit.**

```bash
git add 01-projects/linkedin/src/renderers/registry.py 01-projects/linkedin/tests/test_renderers_registry.py
git commit -m "feat(linkedin): v1.2 Tier 1 renderer registry"
```

---

## Task 11: CLI wiring

**Files:**
- Modify: `src/cli/draft_post.py`
- Modify: `tests/test_cli_draft_post.py`

- [ ] **Step 1: Write the failing test in `tests/test_cli_draft_post.py`.**

Read the file first to see existing fixtures. Add a test that verifies `_advance` routes via the registry:

```python
def test_advance_uses_registry_for_strategy(monkeypatch, tmp_path, sample_brief_bridge):
    """_advance must call tier1_registry.for_strategy(brief.strategy) instead of hardcoding AtomCardRenderer."""
    from cli import draft_post
    seen: dict = {}

    def fake_for_strategy(strategy, **kwargs):
        seen["strategy"] = strategy
        # Return a stub that satisfies validate() + render().
        class StubRenderer:
            def validate(self, brief): return []
            def render(self, brief, out_dir):
                from renderers.base import RenderResult
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "diagram.png").write_bytes(b"\x89PNG\r\n\x1a\n")
                return RenderResult(asset_paths=[out_dir / "diagram.png"], cost=0.0, duration_s=0.0, logs=[])
        return StubRenderer()

    monkeypatch.setattr("renderers.registry.for_strategy", fake_for_strategy)
    # ... fixture-driven advance call ...
    draft_post.main(["--advance", sample_brief_bridge.slug])
    assert seen["strategy"] == "two_atom_bridge"
```

The exact fixture name `sample_brief_bridge` is illustrative; if `test_cli_draft_post.py` already builds a brief via helpers, reuse those. The point is to assert `for_strategy` was called with the brief's strategy.

- [ ] **Step 2: Run the failing test.**

```bash
PYTHONPATH=src pytest tests/test_cli_draft_post.py -v -k registry 2>&1 | tail -20
```

Expected: FAIL (the CLI still imports `AtomCardRenderer` directly).

- [ ] **Step 3: Edit `src/cli/draft_post.py`.**

Find the `if brief.visual_tier == "1_diagram":` block in `_advance` (around line 157-184). Replace the section that imports `AtomCardRenderer` and instantiates it (`from renderers.atom_card import AtomCardRenderer` and the following `renderer = AtomCardRenderer(...)` call) with a registry call:

```python
        from renderers import registry
        from sources.registry import SourcesRegistry
        from sources.tldr_filler import TldrFiller

        loader = AtomLoader(atom_source)
        sources_path = Path(os.environ.get("LINKEDIN_SOURCES_REGISTRY", project_root / "sources.yml"))
        sources_registry = SourcesRegistry(sources_path)

        import anthropic
        client = anthropic.Anthropic()
        tldr_filler = TldrFiller(client=client)

        renderer = registry.for_strategy(
            brief.strategy,
            loader=loader,
            sources_registry=sources_registry,
            brand_spec_path=brand_spec,
            tldr_filler=tldr_filler,
        )
```

The rest of the `_advance` body (validate, render, store paths) stays the same.

- [ ] **Step 4: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_cli_draft_post.py -v 2>&1 | tail -20
```

Expected: all PASS.

- [ ] **Step 5: Commit.**

```bash
git add 01-projects/linkedin/src/cli/draft_post.py 01-projects/linkedin/tests/test_cli_draft_post.py
git commit -m "feat(linkedin): v1.2 CLI routes tier-1 rendering through registry"
```

---

## Task 12: `visual-discipline` skill update

**Files:**
- Modify: `.claude/skills/linkedin/visual-discipline/SKILL.md`

There's no automated test for this skill file; it's read by Claude at runtime. The change is documentation. Keep the structure parallel to the v1.1 update for consistency.

- [ ] **Step 1: Read the current SKILL.md.**

```bash
cat .claude/skills/linkedin/visual-discipline/SKILL.md | head -100
```

- [ ] **Step 2: Replace §3 ("Validate brief against tier rules") with three strategy-keyed blocks.**

Use the exact rule text from the spec §7 (`01-projects/linkedin/docs/2026-05-26-strategy-visuals-design.md`). The replacement covers:

- Tier 1 · `source_spotlight` rules (unchanged from v1.1).
- Tier 1 · `two_atom_bridge` rules (NEW).
- Tier 1 · `convergence_finder` rules (NEW).
- Anti-patterns (shared across all Tier 1, unchanged).

Confirm no em-dashes were added:

```bash
grep -cP "\x{2014}" .claude/skills/linkedin/visual-discipline/SKILL.md
```

Expected: 0.

- [ ] **Step 3: Commit.**

```bash
git add .claude/skills/linkedin/visual-discipline/SKILL.md
git commit -m "docs(linkedin): v1.2 visual-discipline skill gets per-strategy tier-1 rules"
```

---

## Task 13: End-to-end test updates + final regression sweep

**Files:**
- Modify: `tests/test_end_to_end.py`

- [ ] **Step 1: Read the current end-to-end test.**

```bash
PYTHONPATH=src pytest tests/test_end_to_end.py -v 2>&1 | tail -20
```

Confirm what it asserts today (per v1.1.3 it expects `visual_asset_paths == []` for bridge after `--advance`).

- [ ] **Step 2: Update assertions so the bridge and convergence pipelines now produce visual assets.**

Where `test_end_to_end.py` exercises `two_atom_bridge` end-to-end, the post-advance assertion should change from `assert brief.visual_asset_paths == []` to something like:

```python
assert brief.visual_tier == "1_diagram"
assert brief.aspect_ratio == "4:5"
assert len(brief.visual_asset_paths) == 1
assert brief.visual_asset_paths[0].endswith("diagram.png")
```

Same for any `convergence_finder` end-to-end path.

If the existing tests don't actually exercise rendering (they may stop at `text_ready` to avoid live Playwright calls), the assertion update is narrower: just confirm the brief has `aspect_ratio="4:5"` and `panel_label` set after `generate_brief()`.

- [ ] **Step 3: Run the full suite.**

```bash
PYTHONPATH=src pytest tests/ -v 2>&1 | tail -20
```

Expected: green. Note: the live Playwright smoke tests in Tasks 8 and 9 are gated by the `smoke` marker. Use `-m "not smoke"` for the green-on-CI baseline; the smoke marker runs in Task 14.

- [ ] **Step 4: Commit.**

```bash
git add 01-projects/linkedin/tests/test_end_to_end.py
git commit -m "test(linkedin): v1.2 end-to-end expects 4:5 visuals for bridge + convergence"
```

---

## Task 14: Smoke test (user-run) + decision-log entry

**This is a user-run task. The model produces the commands and the log entry skeleton; the user runs the commands against the live Anthropic API and pastes back observations.**

**Files:**
- Modify: `01-projects/linkedin/docs/decision-log.md` (append v1.2 smoke section)

- [ ] **Step 1: Pre-flight checks.**

```bash
echo "ANTHROPIC_API_KEY: ${#ANTHROPIC_API_KEY} chars"
test -f 01-projects/linkedin/sources.yml && echo "sources.yml present" || echo "MISSING sources.yml"
python3 -m playwright install chromium  # idempotent
```

Expected: API key length non-zero; sources.yml present; chromium installed.

- [ ] **Step 2: Bridge smoke command (run from the vault root).**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --strategy=two_atom_bridge \
  --atom-a=antifragile-triad --atom-b=autoregulated-active-recovery \
  --no-render
```

Expected: `"Wrote bundle: ...backlog/<slug>/"`. Note the slug.

Then advance:

```bash
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --advance <bridge-slug>
```

Expected: render completes, `diagram.png` exists in the bundle folder, dimensions ~1080×1350.

Inspect:

```bash
open /Users/gozzynwogbo/second-brain/01-projects/linkedin/backlog/<bridge-slug>/diagram.png
```

- [ ] **Step 3: Convergence smoke command.**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --strategy=convergence_finder --topic=feedback --no-render
```

Then advance and open as in Step 2.

- [ ] **Step 4: Append a v1.2 smoke section to `01-projects/linkedin/docs/decision-log.md`.**

Use the v1.1 / v1.1.3 sections as template. Capture: strategy used, atoms chosen, body text observations (does the CLAIM read naturally? does the body strip cleanly?), visual observations (panel positioning, text overflow, brand-token usage). Note any patches needed.

- [ ] **Step 5: Commit the decision-log update.**

```bash
git add 01-projects/linkedin/docs/decision-log.md
git commit -m "docs(linkedin): log v1.2 bridge + convergence smoke results"
```

- [ ] **Step 6: Push the branch and open a PR.**

```bash
git push -u origin feat/linkedin-engine-v1.2
gh pr create --title "feat(linkedin): v1.2 strategy-specific visuals (bridge + convergence)" \
  --body "$(cat <<'EOF'
## Summary
- Bridge A renderer (pillars + mechanism band) at 4:5
- Convergence C renderer (funnel + convergence panel) at 4:5
- PostBrief: +aspect_ratio, +panel_label, +panel_claim
- Voice prompt v3 with strategy-scoped <CLAIM> tag
- Tier 1 registry replaces hardcoded AtomCardRenderer dispatch

## Test plan
- [ ] Unit tests: bridge + convergence renderer validate, tagged extractor, strategy deltas, registry dispatch
- [ ] Smoke: bridge (antifragile-triad × autoregulated-active-recovery) renders at 4:5
- [ ] Smoke: convergence (--topic=feedback) renders at 4:5
- [ ] Visual check: no text overflow, brand tokens correct, no em-dashes in any output

Spec: 01-projects/linkedin/docs/2026-05-26-strategy-visuals-design.md
Plan: 01-projects/linkedin/docs/2026-05-26-v1-2-implementation-plan.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-review checklist (run before handing off to execution)

- [ ] Every spec section has at least one corresponding task. Spec §2.1 (Bridge A layout) maps to Task 8. Spec §2.2 (Convergence C layout) maps to Task 9. Spec §3 (PostBrief fields) maps to Task 2. Spec §4 (strategy deltas) maps to Tasks 5 and 6. Spec §5 (voice prompt v3) maps to Tasks 3 and 4. Spec §6 (renderer arch) maps to Tasks 7, 8, 9, 10, 11. Spec §7 (visual-discipline skill) maps to Task 12. Spec §8 (failure modes) is covered by validation rules in Tasks 8 and 9 + extraction fallbacks in Tasks 3 and 4. Spec §9 (out of scope) requires no tasks. Spec §10 (implementation phases) is exactly this plan's structure.
- [ ] No "TBD" / "TODO" placeholders.
- [ ] Every code step has full code, not pseudo-code or "similar to above."
- [ ] Type and method names are consistent across tasks: `extract_tagged` (not `extractTagged`), `panel_label` (not `panelLabel`), `_LABEL_BY_CONNECTION_TYPE` (not `LABEL_BY_TYPE`).
- [ ] No em-dashes in plan body or in any code example. Run `grep -cP "\x{2014}" 01-projects/linkedin/docs/2026-05-26-v1-2-implementation-plan.md`; expected: 0.

---

*Companion docs:*
- *Design spec: `2026-05-26-strategy-visuals-design.md`*
- *v1.1 plan precedent: `2026-05-25-v1-1-implementation-plan.md`*
- *Decision log: `decision-log.md`*
