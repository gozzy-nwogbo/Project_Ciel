# LinkedIn Engine v1.1 Implementation Plan — Tier 1 Redesign + Cold-Reader Anchor v2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the graphviz network-diagram Tier 1 renderer with an HTML/CSS atom-card renderer (Playwright-driven) and ship source-type-aware cold-reader anchoring. Result: every Tier 1 strategy produces a shippable visual without depending on vault graph topology.

**Architecture:** New `AtomCardRenderer` reads atoms + tldr distillations + a sources registry, renders a Jinja2 HTML template (thesis hero + atom evidence + source trace), screenshots it at 1080×1080 via Playwright headless Chromium. Voice prompt grows a source-type-aware anchor rule and a `<THESIS>` tag requirement; text generator extracts the thesis and stores it on `PostBrief`. Atom front-matter v2.2 adds optional `tldr`; missing tldr triggers a one-shot LLM fill that back-writes the result.

**Tech Stack:** Python 3.11+, Playwright (headless Chromium), Jinja2, Anthropic SDK (`claude-opus-4-7` already in use), python-frontmatter, PyYAML, pytest + pytest-mock.

**Spec reference:** `01-projects/linkedin/docs/2026-05-25-tier1-redesign-design.md`

**Working tree:** Create a feature branch `feat/linkedin-engine-v1.1` from `main` before starting Task 1.

---

## File map

**Create:**
- `src/renderers/atom_card.py` — `AtomCardRenderer` class
- `src/renderers/templates/atom_card.html.j2` — Jinja2 HTML template
- `src/sources/__init__.py` — empty module init
- `src/sources/registry.py` — `SourcesRegistry` class
- `src/sources/tldr_filler.py` — `TldrFiller` class
- `src/linter/thesis.py` — `extract_thesis()` utility
- `sources.yml` — engine-scoped source registry (initial entries for known book sources)
- `tests/test_atom_card_renderer.py` — renderer tests
- `tests/test_sources_registry.py` — registry tests
- `tests/test_tldr_filler.py` — filler tests
- `tests/test_thesis_extraction.py` — extractor tests

**Modify:**
- `requirements.txt` — add Playwright + Jinja2, remove graphviz
- `src/atom_loader.py` — add `tldr` field on `Atom`, parse it in `_parse`
- `src/models.py` — add `PostBrief.thesis: str` and round-trip in `to_dict` / `from_dict`
- `src/text_generator.py` — voice prompt v2 + THESIS extraction + sources-aware anchor injection
- `src/strategies/two_atom_bridge.py` — flip default `visual_tier` to `"1_diagram"`
- `src/strategies/convergence_finder.py` — flip default `visual_tier` to `"1_diagram"`
- `src/cli/draft_post.py` — swap `DiagramRenderer` for `AtomCardRenderer`, remove edgeless guard
- `01-projects/linkedin/CLAUDE.md` — Playwright install note
- `.claude/skills/linkedin/visual-discipline/SKILL.md` — Tier 1 rules per spec §7
- `tests/test_two_atom_bridge.py` — update default-tier assertion
- `tests/test_convergence_finder.py` — update default-tier assertion
- `tests/test_models.py` — round-trip test includes `thesis`
- `tests/test_atom_loader.py` — load atom with tldr field
- `tests/test_text_generator.py` — voice prompt v2 + THESIS extraction
- `tests/test_cli_draft_post.py` — update for new renderer
- `tests/test_end_to_end.py` — replace graphviz expectations

**Delete:**
- `src/renderers/diagram.py`
- `tests/test_diagram_renderer.py`

---

## Task 1: Branch + dependency setup

**Files:**
- Modify: `requirements.txt`
- Modify: `01-projects/linkedin/CLAUDE.md`

- [ ] **Step 1: Create feature branch from main.**

```bash
cd /Users/gozzynwogbo/second-brain
git checkout main && git pull --ff-only && git checkout -b feat/linkedin-engine-v1.1
```

- [ ] **Step 2: Update `requirements.txt`.**

Open `01-projects/linkedin/requirements.txt`. Replace the file with:

```
anthropic==0.40.0
Jinja2==3.1.4
playwright==1.49.1
python-frontmatter==1.1.0
PyYAML==6.0.2
```

(Removes `graphviz==0.20.3`. Adds Jinja2 + Playwright.)

- [ ] **Step 3: Install Python deps and Chromium.**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin
pip install -r requirements.txt
python -m playwright install chromium
```

Expected: chromium binary downloads (~150MB), prints "chromium <version> downloaded to ~/Library/Caches/ms-playwright/…".

- [ ] **Step 4: Verify install with a smoke import.**

```bash
PYTHONPATH=src python -c "from playwright.sync_api import sync_playwright; from jinja2 import Environment; print('ok')"
```

Expected: `ok`. If `ModuleNotFoundError`, re-run pip install.

- [ ] **Step 5: Add Playwright install note to project CLAUDE.md.**

Open `01-projects/linkedin/CLAUDE.md`. Under `## How to run`, add a new subsection before `## Testing`:

```markdown
## One-time install

After `pip install -r requirements.txt`, install the Chromium binary
Playwright uses for the Tier 1 renderer:

    python -m playwright install chromium
```

- [ ] **Step 6: Commit.**

```bash
git add 01-projects/linkedin/requirements.txt 01-projects/linkedin/CLAUDE.md
git commit -m "$(cat <<'EOF'
chore(linkedin): swap graphviz for Playwright + Jinja2

Removes graphviz dep (replaced by atom-card renderer). Adds Playwright
1.49.1 for headless Chromium screenshot rendering and Jinja2 3.1.4 for
HTML templating. Documents one-time chromium install in project CLAUDE.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: PostBrief.thesis field

**Files:**
- Modify: `src/models.py`
- Modify: `tests/test_models.py`

- [ ] **Step 1: Write the failing test.**

Open `tests/test_models.py`. Add at the end of the file:

```python
def test_post_brief_round_trip_includes_thesis():
    """PostBrief.thesis is preserved across to_dict / from_dict round-trip."""
    from datetime import datetime, timezone
    from models import AtomRef, PostBrief, Status

    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id="b1",
        slug="2026-05-25-thesis-test",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug="atom-a", role="primary")],
        angle="An angle.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        thesis="Strategy is problem-shaped, not goal-shaped.",
    )
    d = brief.to_dict()
    assert d["thesis"] == "Strategy is problem-shaped, not goal-shaped."
    restored = PostBrief.from_dict(d)
    assert restored.thesis == "Strategy is problem-shaped, not goal-shaped."


def test_post_brief_thesis_defaults_empty():
    """PostBrief.thesis defaults to empty string when not provided."""
    from datetime import datetime, timezone
    from models import AtomRef, PostBrief, Status

    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id="b2",
        slug="x",
        created_at=now,
        updated_at=now,
        strategy="x",
        strategy_params={},
        atoms_used=[],
        angle="",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    assert brief.thesis == ""
```

- [ ] **Step 2: Run test, verify fail.**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin
PYTHONPATH=src pytest tests/test_models.py::test_post_brief_round_trip_includes_thesis tests/test_models.py::test_post_brief_thesis_defaults_empty -v
```

Expected: FAIL with `TypeError: __init__() got an unexpected keyword argument 'thesis'`.

- [ ] **Step 3: Add `thesis` field to PostBrief.**

Open `src/models.py`. In the `PostBrief` dataclass, add `thesis` after `approved_text`:

```python
    draft_text: str = ""
    approved_text: str = ""
    thesis: str = ""
    edit_delta: Optional[dict[str, Any]] = None
```

In `from_dict` classmethod, add `thesis=d.get("thesis", "")` to the constructor call (insert near the other string fields, before `edit_delta`):

```python
            draft_text=d.get("draft_text", ""),
            approved_text=d.get("approved_text", ""),
            thesis=d.get("thesis", ""),
            edit_delta=d.get("edit_delta"),
```

- [ ] **Step 4: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_models.py -v
```

Expected: all tests pass including the two new ones.

- [ ] **Step 5: Commit.**

```bash
git add src/models.py tests/test_models.py
git commit -m "$(cat <<'EOF'
feat(linkedin): add PostBrief.thesis field

Thesis line will be extracted from <THESIS>...</THESIS> tags in
generated body text and consumed by the Tier 1 renderer as the
display-type hero. Defaults to empty string; round-trips through
to_dict / from_dict.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Atom v2.2 — tldr field

**Files:**
- Modify: `src/atom_loader.py`
- Modify: `tests/test_atom_loader.py`
- Modify: `tests/fixtures/` (add one fixture with tldr)

- [ ] **Step 1: Add a fixture atom with `tldr`.**

Create `tests/fixtures/atom-with-tldr.md`:

```markdown
---
title: Atom With Tldr
type: concept
source: Test Source, 2026
domain: test
tags: [fixture]
tldr: This is the tldr line for the atom.
---

Body text for the atom.
```

- [ ] **Step 2: Write failing tests.**

Open `tests/test_atom_loader.py`. Append:

```python
def test_atom_loads_with_tldr():
    """Atom front-matter v2.2 includes an optional tldr field."""
    from pathlib import Path
    from atom_loader import AtomLoader

    fixtures = Path(__file__).parent / "fixtures"
    loader = AtomLoader(fixtures)
    atom = loader.load_one("atom-with-tldr")
    assert atom is not None
    assert atom.tldr == "This is the tldr line for the atom."


def test_atom_without_tldr_defaults_none():
    """Atoms missing tldr load with tldr=None (backwards compat)."""
    from pathlib import Path
    from atom_loader import AtomLoader

    fixtures = Path(__file__).parent / "fixtures"
    loader = AtomLoader(fixtures)
    # sample-concept fixture has no tldr field
    atom = loader.load_one("sample-concept")
    assert atom is not None
    assert atom.tldr is None
```

- [ ] **Step 3: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_atom_loader.py::test_atom_loads_with_tldr tests/test_atom_loader.py::test_atom_without_tldr_defaults_none -v
```

Expected: FAIL with `AttributeError: 'Atom' object has no attribute 'tldr'`.

- [ ] **Step 4: Add `tldr` to `Atom` dataclass and parser.**

Open `src/atom_loader.py`. In the `Atom` dataclass, add `tldr` after `source`:

```python
    source: Optional[str] = None
    tldr: Optional[str] = None
    path: Optional[Path] = None
```

In `_parse`, populate it from front-matter:

```python
        return Atom(
            slug=path.stem,
            title=meta["title"],
            type=meta["type"],
            source_date=str(meta.get("source_date", "")),
            body=post.content,
            tags=list(meta.get("tags", []) or []),
            domain=meta.get("domain"),
            origin=meta.get("origin"),
            source=meta.get("source"),
            tldr=meta.get("tldr"),
            path=path,
            from_atom=meta.get("from"),
            to_atom=meta.get("to"),
            connection_type=meta.get("connection_type", "general"),
        )
```

- [ ] **Step 5: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_atom_loader.py -v
```

Expected: all atom loader tests pass.

- [ ] **Step 6: Commit.**

```bash
git add src/atom_loader.py tests/test_atom_loader.py tests/fixtures/atom-with-tldr.md
git commit -m "$(cat <<'EOF'
feat(linkedin): atom front-matter v2.2 — optional tldr field

Atoms can now declare a single-sentence tldr in front-matter, consumed
by the Tier 1 atom-card renderer as the per-atom evidence line.
Backwards-compatible — atoms without tldr load with tldr=None and get
filled forward on first use (Task 5).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: SourcesRegistry

**Files:**
- Create: `src/sources/__init__.py`
- Create: `src/sources/registry.py`
- Create: `01-projects/linkedin/sources.yml`
- Create: `tests/test_sources_registry.py`
- Create: `tests/fixtures/sources-test.yml`

- [ ] **Step 1: Write failing tests.**

Create `tests/test_sources_registry.py`:

```python
from pathlib import Path

from sources.registry import SourceEntry, SourcesRegistry


def _registry_path(tmp_path: Path) -> Path:
    p = tmp_path / "sources.yml"
    p.write_text(
        'Richard Rumelt, 2011:\n'
        '  type: book\n'
        '  author_bio: "UCLA strategy professor and author of Good Strategy / Bad Strategy"\n'
        '  work: "Good Strategy / Bad Strategy"\n'
        '\n'
        '"Nate B. Jones, AI Daily Update":\n'
        '  type: video\n'
        '\n'
        'Anonymous:\n'
        '  type: post\n'
    )
    return p


def test_registry_loads_book_entry(tmp_path):
    reg = SourcesRegistry(_registry_path(tmp_path))
    entry = reg.lookup("Richard Rumelt, 2011")
    assert entry is not None
    assert entry.type == "book"
    assert "UCLA" in entry.author_bio
    assert entry.work == "Good Strategy / Bad Strategy"


def test_registry_loads_video_entry_without_bio(tmp_path):
    reg = SourcesRegistry(_registry_path(tmp_path))
    entry = reg.lookup("Nate B. Jones, AI Daily Update")
    assert entry is not None
    assert entry.type == "video"
    assert entry.author_bio is None


def test_registry_missing_entry_returns_none(tmp_path):
    reg = SourcesRegistry(_registry_path(tmp_path))
    assert reg.lookup("Unknown Person, 9999") is None


def test_registry_handles_missing_file(tmp_path):
    """Registry loads cleanly even if the file does not exist."""
    reg = SourcesRegistry(tmp_path / "does-not-exist.yml")
    assert reg.lookup("anyone") is None
```

- [ ] **Step 2: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_sources_registry.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'sources'`.

- [ ] **Step 3: Create the sources module.**

Create `src/sources/__init__.py` as an empty file.

Create `src/sources/registry.py`:

```python
"""Source registry — maps atom source slugs to source-type metadata."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class SourceEntry:
    type: str                       # "book" | "video" | "podcast" | "post"
    author_bio: Optional[str] = None
    work: Optional[str] = None


class SourcesRegistry:
    """Reads sources.yml. Lookups by source slug return SourceEntry or None."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._entries: dict[str, SourceEntry] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open() as f:
            raw = yaml.safe_load(f) or {}
        for key, value in raw.items():
            if not isinstance(value, dict) or "type" not in value:
                continue
            self._entries[key] = SourceEntry(
                type=value["type"],
                author_bio=value.get("author_bio"),
                work=value.get("work"),
            )

    def lookup(self, source: str) -> Optional[SourceEntry]:
        return self._entries.get(source)
```

- [ ] **Step 4: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_sources_registry.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 5: Create the initial production `sources.yml`.**

Create `01-projects/linkedin/sources.yml`:

```yaml
# Source registry — keyed by atom `source:` slug.
# Fields:
#   type:        book | video | podcast | post   (required)
#   author_bio:  single sentence describing the author    (required for book)
#   work:        title of the source work        (optional)
#
# Voice prompt uses `type` to choose between full-bio anchoring (book)
# and 3-5 word descriptor anchoring (video/podcast/post). Missing entries
# fall back to 3-5 word anchor with a logged warning.

"Richard Rumelt, 2011":
  type: book
  author_bio: "UCLA strategy professor and author of Good Strategy / Bad Strategy"
  work: "Good Strategy / Bad Strategy"

"Daniel Kahneman, 2011":
  type: book
  author_bio: "Princeton psychologist, Nobel laureate, author of Thinking Fast and Slow"
  work: "Thinking Fast and Slow"

"Charlie Munger, 1994":
  type: book
  author_bio: "Berkshire Hathaway vice-chair, author of Poor Charlie's Almanack"
  work: "Poor Charlie's Almanack"

"Anonymous":
  type: post
```

(Other sources will be added forward as posts cite them.)

- [ ] **Step 6: Commit.**

```bash
git add src/sources/__init__.py src/sources/registry.py 01-projects/linkedin/sources.yml tests/test_sources_registry.py
git commit -m "$(cat <<'EOF'
feat(linkedin): sources registry

New SourcesRegistry maps atom source slugs to {type, author_bio, work}.
type drives source-aware cold-reader anchoring (book → full bio, other
→ 3-5 word). Initial entries for 3 known book sources; registry fills
forward as new sources are cited.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: TldrFiller

**Files:**
- Create: `src/sources/tldr_filler.py`
- Create: `tests/test_tldr_filler.py`

- [ ] **Step 1: Write failing tests.**

Create `tests/test_tldr_filler.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock

from atom_loader import Atom
from sources.tldr_filler import TldrFiller


def _atom_file(tmp_path: Path) -> Path:
    """Write a real atom file we can read back to check the back-write."""
    p = tmp_path / "filler-fixture.md"
    p.write_text(
        "---\n"
        "title: Filler Fixture\n"
        "type: concept\n"
        "source: Test Source, 2026\n"
        "domain: test\n"
        "tags: [fixture]\n"
        "---\n\n"
        "Some body text describing the concept.\n"
    )
    return p


def _make_atom(path: Path) -> Atom:
    return Atom(
        slug="filler-fixture",
        title="Filler Fixture",
        type="concept",
        source_date="",
        body="Some body text describing the concept.",
        tags=["fixture"],
        domain="test",
        source="Test Source, 2026",
        tldr=None,
        path=path,
    )


def test_fill_calls_llm_and_returns_single_sentence(tmp_path):
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="A single sentence distillation of the concept.")]
    fake_client.messages.create.return_value = fake_response

    filler = TldrFiller(client=fake_client, model="claude-haiku-4-5-20251001")
    result = filler.fill(atom)

    assert result == "A single sentence distillation of the concept."
    fake_client.messages.create.assert_called_once()


def test_fill_back_writes_tldr_to_atom_file(tmp_path):
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="Back-written distillation.")]
    fake_client.messages.create.return_value = fake_response

    TldrFiller(client=fake_client).fill(atom)

    content = path.read_text()
    assert "tldr: Back-written distillation." in content
    # Body still present
    assert "Some body text describing the concept." in content


def test_fill_returns_none_when_client_raises(tmp_path):
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = RuntimeError("API down")

    result = TldrFiller(client=fake_client).fill(atom)
    assert result is None
```

- [ ] **Step 2: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_tldr_filler.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'sources.tldr_filler'`.

- [ ] **Step 3: Implement TldrFiller.**

Create `src/sources/tldr_filler.py`:

```python
"""LLM-based tldr fill for atoms missing the optional v2.2 tldr field.

Successful fills back-write the result to the atom file's front-matter
so the atom is "completed" for future uses — the graph compounds.
"""
from __future__ import annotations

from typing import Any, Optional

import frontmatter

from atom_loader import Atom


SYSTEM_PROMPT = """You distill a knowledge atom into one sentence.

The sentence:
- Stands alone for a cold reader who has never seen this atom.
- Is one declarative sentence, ideally under 80 characters.
- Captures the core mechanism or claim, not metadata about the atom.
- Plain text only. No quotes, no markdown, no preamble.
"""


class TldrFiller:
    def __init__(self, client: Any, model: str = "claude-haiku-4-5-20251001"):
        self.client = client
        self.model = model

    def fill(self, atom: Atom) -> Optional[str]:
        """Generate a tldr for the atom. Back-write on success. Return text or None on failure."""
        body_snippet = (atom.body or "").strip().replace("\n", " ")[:600]
        user_prompt = (
            f"Atom title: {atom.title}\n"
            f"Domain: {atom.domain or 'unspecified'}\n"
            f"Source: {atom.source or 'unspecified'}\n"
            f"Body:\n{body_snippet}\n\n"
            f"Produce one sentence."
        )
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=120,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(block.text for block in response.content if hasattr(block, "text"))
        except Exception:
            return None

        tldr = text.strip().strip('"').strip()
        if not tldr:
            return None

        if atom.path is not None and atom.path.exists():
            try:
                post = frontmatter.load(atom.path)
                post["tldr"] = tldr
                atom.path.write_text(frontmatter.dumps(post) + "\n")
            except Exception:
                # Back-write failed; still return the tldr so caller can use it for this render.
                pass

        return tldr
```

- [ ] **Step 4: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_tldr_filler.py -v
```

Expected: all 3 tests pass.

- [ ] **Step 5: Commit.**

```bash
git add src/sources/tldr_filler.py tests/test_tldr_filler.py
git commit -m "$(cat <<'EOF'
feat(linkedin): TldrFiller — LLM fill for missing atom tldr

When the renderer needs a tldr that isn't in atom front-matter, the
filler calls Haiku, back-writes the result to the atom file, and
returns the tldr for this render. Failure modes (API error, empty
output, write failure) return None gracefully so the renderer can
degrade to atom-name-only display.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: THESIS extraction utility

**Files:**
- Create: `src/linter/thesis.py`
- Create: `tests/test_thesis_extraction.py`

- [ ] **Step 1: Write failing tests.**

Create `tests/test_thesis_extraction.py`:

```python
from linter.thesis import ExtractionResult, extract_thesis


def test_extracts_single_tagged_thesis():
    body = (
        "Opening paragraph here.\n\n"
        "<THESIS>Strategy is problem-shaped, not goal-shaped.</THESIS>\n\n"
        "Closing remark."
    )
    result = extract_thesis(body)
    assert result.thesis == "Strategy is problem-shaped, not goal-shaped."
    assert result.warning is None
    # Tag stripped from clean_body but the sentence remains inline.
    assert "<THESIS>" not in result.clean_body
    assert "Strategy is problem-shaped" in result.clean_body


def test_no_tag_falls_back_to_first_sentence():
    body = "First sentence here. Second sentence here. Third."
    result = extract_thesis(body)
    assert result.thesis == "First sentence here."
    assert result.warning is not None
    assert "no THESIS" in result.warning.lower()


def test_multiple_tags_uses_first_and_warns():
    body = (
        "<THESIS>First tagged thesis.</THESIS>\n\n"
        "Some body.\n\n"
        "<THESIS>Second tagged thesis.</THESIS>"
    )
    result = extract_thesis(body)
    assert result.thesis == "First tagged thesis."
    assert result.warning is not None
    assert "multiple" in result.warning.lower()
    # Both tag-pairs stripped from clean_body
    assert "<THESIS>" not in result.clean_body
    assert "First tagged thesis." in result.clean_body
    assert "Second tagged thesis." in result.clean_body


def test_empty_tag_falls_back():
    body = "Real first sentence. <THESIS></THESIS> Body text."
    result = extract_thesis(body)
    assert result.thesis == "Real first sentence."
    assert result.warning is not None
```

- [ ] **Step 2: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_thesis_extraction.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'linter.thesis'`.

- [ ] **Step 3: Implement extractor.**

Create `src/linter/thesis.py`:

```python
"""Extract <THESIS>...</THESIS> sentences from generated body text."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_THESIS_RE = re.compile(r"<THESIS>(.*?)</THESIS>", re.DOTALL)
# Naive sentence split — splits on . ! ? followed by whitespace/EOL. Good enough
# for fallback; voice rules already cap exclamation points.
_SENTENCE_RE = re.compile(r"([^.!?]+[.!?])(?:\s|$)")


@dataclass
class ExtractionResult:
    thesis: str
    clean_body: str
    warning: Optional[str]


def extract_thesis(body: str) -> ExtractionResult:
    matches = _THESIS_RE.findall(body)
    non_empty = [m.strip() for m in matches if m.strip()]

    if not non_empty:
        first = _first_sentence(body)
        clean = _strip_tags(body)
        warning = "no THESIS tag found, used first sentence fallback"
        return ExtractionResult(thesis=first, clean_body=clean, warning=warning)

    clean = _strip_tags(body)

    if len(non_empty) == 1 and len(matches) == 1:
        return ExtractionResult(thesis=non_empty[0], clean_body=clean, warning=None)

    warning = "multiple THESIS tags found, used the first"
    return ExtractionResult(thesis=non_empty[0], clean_body=clean, warning=warning)


def _strip_tags(body: str) -> str:
    return _THESIS_RE.sub(lambda m: m.group(1), body)


def _first_sentence(body: str) -> str:
    stripped = _strip_tags(body).strip()
    m = _SENTENCE_RE.search(stripped)
    if m:
        return m.group(1).strip()
    return stripped.split("\n")[0].strip()
```

- [ ] **Step 4: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_thesis_extraction.py -v
```

Expected: all 4 tests pass.

- [ ] **Step 5: Commit.**

```bash
git add src/linter/thesis.py tests/test_thesis_extraction.py
git commit -m "$(cat <<'EOF'
feat(linkedin): THESIS tag extraction

Parses <THESIS>...</THESIS> from generated body text. Returns the
thesis string, a tag-stripped clean body, and a warning string for
fallback cases (no tag → first sentence; multiple tags → first).
Empty tag treated as no tag.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Voice prompt v2 + text generator integration

**Files:**
- Modify: `src/text_generator.py`
- Modify: `tests/test_text_generator.py`

- [ ] **Step 1: Write failing tests.**

Open `tests/test_text_generator.py`. Add at the end:

```python
def test_voice_prompt_v2_thesis_requirement():
    """System prompt requires exactly one <THESIS>...</THESIS> block."""
    from text_generator import VOICE_SYSTEM_PROMPT
    assert "<THESIS>" in VOICE_SYSTEM_PROMPT
    assert "</THESIS>" in VOICE_SYSTEM_PROMPT
    assert "exactly one" in VOICE_SYSTEM_PROMPT.lower()


def test_voice_prompt_v2_source_type_aware_anchor():
    """COLD READER ANCHOR rule mentions source type differentiation."""
    from text_generator import VOICE_SYSTEM_PROMPT
    assert "book" in VOICE_SYSTEM_PROMPT.lower()
    assert "video" in VOICE_SYSTEM_PROMPT.lower() or "podcast" in VOICE_SYSTEM_PROMPT.lower()
    assert "author_bio" in VOICE_SYSTEM_PROMPT or "bio" in VOICE_SYSTEM_PROMPT.lower()


def test_generate_extracts_thesis_and_strips_tags(monkeypatch, tmp_path):
    """generate() populates brief.thesis and strips tags from draft_text."""
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    from atom_loader import AtomLoader
    from models import AtomRef, PostBrief, Status
    from text_generator import TextGenerator

    # Create a minimal atom fixture
    atom_file = tmp_path / "atom-a.md"
    atom_file.write_text(
        "---\ntitle: Atom A\ntype: concept\nsource: Test, 2026\ndomain: test\ntags: []\n---\n\nBody.\n"
    )

    loader = AtomLoader(tmp_path)

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text=(
        "Opening line.\n\n"
        "<THESIS>The locked thesis sentence.</THESIS>\n\n"
        "Closing line."
    ))]
    fake_client.messages.create.return_value = fake_response

    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id="b1",
        slug="thesis-extract-test",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug="atom-a", role="primary")],
        angle="An angle.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )

    gen = TextGenerator(client=fake_client, loader=loader)
    result = gen.generate(brief)

    assert result.thesis == "The locked thesis sentence."
    assert "<THESIS>" not in result.draft_text
    assert "</THESIS>" not in result.draft_text
    assert "The locked thesis sentence." in result.draft_text
```

- [ ] **Step 2: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_text_generator.py::test_voice_prompt_v2_thesis_requirement tests/test_text_generator.py::test_voice_prompt_v2_source_type_aware_anchor tests/test_text_generator.py::test_generate_extracts_thesis_and_strips_tags -v
```

Expected: FAIL — prompt assertions fail, thesis extraction not wired.

- [ ] **Step 3: Update VOICE_SYSTEM_PROMPT and `generate()`.**

Open `src/text_generator.py`. Replace the `VOICE_SYSTEM_PROMPT` constant with:

```python
VOICE_SYSTEM_PROMPT = """You write LinkedIn posts in the author's voice.

HARD RULES (these are never broken):
- No em-dashes or en-dashes. Use commas, periods, or restructure.
- No contrastive framing patterns ("Not as X, but as Y", "Not just X, X+"). This is an AI watermark.
- No AI watermark vocabulary: "delve", "tapestry", "navigate the complex", "in conclusion", "moreover", "furthermore", "in essence".
- Active voice as default. Passive only when the subject is genuinely unknown.
- Maximum 1 exclamation point per 150 words.

POSITIONING:
- Framing is "insight + visible system". Posts can name "my second brain" or "the atom graph"
  as the source of the observation. The system is the differentiator.

VOICE:
- Observational, sharp, willing to be specific. Not promotional.
- Tight openings. No throat-clearing. No "In today's world..." or "Have you ever noticed...".
- One observation, evidence from the atoms, named takeaway.
- End with a question or an invitation when natural. No forced CTAs.

COLD READER ANCHOR (source-type-aware):
- Assume the reader has never heard of the source author or the concepts you name.
- The first time you reference a concept from an atom, anchor it with a 5-to-8-word inline definition or context cue. Example: not "Chain-Link Systems are tricky" but "Chain-Link Systems, where the weakest link caps the whole, are tricky."
- For source authors, anchor depends on source type (provided in the user prompt under "Source anchors"):
  - type: book → On first reference, introduce the author using the full bio sentence provided. Example: "Reading three atoms from Richard Rumelt, a UCLA strategy professor and author of Good Strategy / Bad Strategy, a pattern surfaced."
  - type: video | podcast | post → On first reference, use a 3-5 word descriptor.
  - source type not provided → Use a 3-5 word descriptor as fallback.
- The post must stand alone for a cold LinkedIn reader who has not been following any prior posts.

THESIS LINE:
- The post must contain exactly one thesis sentence wrapped in <THESIS>...</THESIS> tags.
- Treat the tagged sentence as a standalone aphorism — it will be rendered as the visual's hero line.
- Place the tags where the sentence reads naturally in the body. It is part of the post, not a header.

OUTPUT:
- Plain text only. No headers, no markdown.
- Target word count provided in the user prompt — stay in range.
"""
```

Now update the `TextGenerator` class. Replace the entire class body with:

```python
class TextGenerator:
    def __init__(
        self,
        client: Any,
        loader: AtomLoader,
        model: str = "claude-opus-4-7",
        sources_registry: Optional["SourcesRegistry"] = None,
    ):
        self.client = client
        self.loader = loader
        self.model = model
        self.sources_registry = sources_registry

    def generate(self, brief: PostBrief, target_word_range: tuple[int, int] = (80, 200)) -> PostBrief:
        from linter.thesis import extract_thesis

        atom_summaries = []
        source_anchors: list[str] = []
        seen_sources: set[str] = set()
        for ref in brief.atoms_used:
            atom = self.loader.load_one(ref.slug)
            if not atom:
                continue
            snippet = (atom.body or "").strip().replace("\n", " ")[:240]
            atom_summaries.append(f"- [{atom.title}] ({atom.domain or 'no-domain'}): {snippet}")
            src = atom.source or atom.origin
            if src and src not in seen_sources and self.sources_registry is not None:
                seen_sources.add(src)
                entry = self.sources_registry.lookup(src)
                if entry is None:
                    source_anchors.append(f"- {src}: type=unknown (fall back to 3-5 word descriptor)")
                elif entry.type == "book" and entry.author_bio:
                    source_anchors.append(f"- {src}: type=book, bio=\"{entry.author_bio}\"")
                else:
                    source_anchors.append(f"- {src}: type={entry.type}")

        atoms_block = "\n".join(atom_summaries) or "(no atom summaries available)"
        sources_block = "\n".join(source_anchors) if source_anchors else "(no source entries available)"

        lo, hi = target_word_range
        user_prompt = (
            f"Write a LinkedIn post advancing this angle:\n\n"
            f"  {brief.angle}\n\n"
            f"Use these atoms as substance:\n\n"
            f"{atoms_block}\n\n"
            f"Source anchors:\n\n"
            f"{sources_block}\n\n"
            f"Target word count: {lo}-{hi}.\n"
            f"Name 'my second brain' or 'the atom graph' as the source of the observation.\n"
            f"Plain text only — no markdown, no headers. Remember the THESIS tag rule."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=VOICE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))

        extraction = extract_thesis(text.strip())
        brief.thesis = extraction.thesis
        brief.draft_text = extraction.clean_body.strip()
        brief.status = Status.TEXT_READY
        brief.updated_at = utc_now()
        brief.status_history.append({
            "status": Status.TEXT_READY.value,
            "timestamp": brief.updated_at.isoformat(),
            "actor": "engine",
            "note": extraction.warning or "",
        })
        return brief
```

Add the matching imports at the top of the file (replace the existing imports block):

```python
"""Text generator — Claude API call constrained by voice rules."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from atom_loader import AtomLoader
from models import PostBrief, Status, utc_now

if TYPE_CHECKING:
    from sources.registry import SourcesRegistry
```

- [ ] **Step 4: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_text_generator.py -v
```

Expected: all tests pass (new ones + any pre-existing ones for the v1.0.1 anchor rule should now reference the v2 prompt).

If any pre-existing test fails because it asserted on the v1.0.1 anchor wording, update its assertion to check for the v2 wording (`"source-type-aware"` or `"type: book"`).

- [ ] **Step 5: Commit.**

```bash
git add src/text_generator.py tests/test_text_generator.py
git commit -m "$(cat <<'EOF'
feat(linkedin): voice prompt v2 + THESIS extraction

VOICE_SYSTEM_PROMPT grows two rules:
1. THESIS LINE — body must contain exactly one <THESIS>...</THESIS>
   sentence; renderer consumes it as the visual's hero line.
2. COLD READER ANCHOR (source-type-aware) — book sources get a full
   author-bio sentence on first reference; video/podcast/post get the
   existing 3-5 word descriptor.

TextGenerator now accepts an optional SourcesRegistry, looks up the
source per atom, and injects per-source anchor instructions into the
user prompt. On response, extracts the thesis into brief.thesis and
stores the tag-stripped body in brief.draft_text.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Atom card HTML template

**Files:**
- Create: `src/renderers/templates/atom_card.html.j2`

This task is template-only — no test step. The template is exercised by Task 9's renderer tests.

- [ ] **Step 1: Create the template directory.**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin
mkdir -p src/renderers/templates
```

- [ ] **Step 2: Write the Jinja2 template.**

Create `src/renderers/templates/atom_card.html.j2`:

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono&display=swap');

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 1080px; height: 1080px;
      background: {{ colors.background }};
      font-family: {{ typography.body }};
      color: {{ colors.text_primary }};
      -webkit-font-smoothing: antialiased;
    }
    .card {
      width: 1080px; height: 1080px;
      padding: 90px 86px;
      display: flex; flex-direction: column;
    }
    .meta-row {
      display: flex; justify-content: space-between; align-items: baseline;
      margin-bottom: 56px;
    }
    .meta {
      font-size: 28px;
      color: {{ colors.accent_primary }};
      letter-spacing: 0.1em;
      text-transform: uppercase;
      font-weight: 500;
    }
    .domain {
      font-size: 28px;
      color: {{ colors.text_secondary }};
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-family: {{ typography.mono }};
    }
    .thesis {
      font-size: 78px;
      font-weight: 500;
      line-height: 1.1;
      letter-spacing: -0.01em;
      color: {{ colors.text_primary }};
      margin-bottom: 64px;
    }
    .atoms { margin-bottom: auto; }
    .atom-block { margin-bottom: 36px; }
    .atom-block:last-child { margin-bottom: 0; }
    .atom-name {
      font-size: 32px;
      font-weight: 600;
      color: {{ colors.text_primary }};
      margin-bottom: 8px;
      display: flex; align-items: baseline; gap: 18px;
    }
    .atom-name::before {
      content: ""; width: 14px; height: 14px;
      background: {{ colors.accent_primary }};
      border-radius: 50%;
      flex-shrink: 0;
      transform: translateY(-2px);
    }
    .atom-text {
      font-size: 30px;
      line-height: 1.4;
      color: {{ colors.text_secondary }};
      padding-left: 32px;
    }
    .overflow-line {
      margin-top: 18px;
      font-size: 26px;
      color: {{ colors.accent_primary }};
      font-family: {{ typography.mono }};
      letter-spacing: 0.05em;
      padding-left: 32px;
    }
    .footer-row {
      margin-top: 56px;
      display: flex; justify-content: space-between; align-items: baseline;
      font-size: 26px;
      font-family: {{ typography.mono }};
      letter-spacing: 0.02em;
    }
    .footer-source { color: {{ colors.text_primary }}; }
    .footer-count { color: {{ colors.text_secondary }}; }
  </style>
</head>
<body>
  <div class="card">
    <div class="meta-row">
      <div class="meta">from second brain</div>
      <div class="domain">{{ domain_tag }}</div>
    </div>
    <div class="thesis">{{ thesis }}</div>
    <div class="atoms">
      {% for atom in atom_blocks %}
      <div class="atom-block">
        <div class="atom-name">{{ atom.name }}</div>
        {% if atom.text %}<div class="atom-text">{{ atom.text }}</div>{% endif %}
      </div>
      {% endfor %}
      {% if overflow_line %}
      <div class="overflow-line">{{ overflow_line }}</div>
      {% endif %}
    </div>
    <div class="footer-row">
      <div class="footer-source">{{ source_slug }}</div>
      <div class="footer-count">{{ footer_right }}</div>
    </div>
  </div>
</body>
</html>
```

(Pixel sizes are scaled up ~3× from the 1:1 mockup because the final canvas is 1080×1080 rather than the ~360px preview size we designed against; ratios preserved.)

- [ ] **Step 3: Commit (no test — exercised by Task 9).**

```bash
git add src/renderers/templates/atom_card.html.j2
git commit -m "$(cat <<'EOF'
feat(linkedin): atom-card Jinja2 template

HTML+CSS template for the Tier 1 atom-card visual. Brand tokens
(colors, fonts) injected at render time from brand-spec.md. Variant B
layout from the v1.1 design: meta row + thesis hero + atom blocks
(terracotta dot leader, name, distillation) + source footer.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: AtomCardRenderer class

**Files:**
- Create: `src/renderers/atom_card.py`
- Create: `tests/test_atom_card_renderer.py`

- [ ] **Step 1: Write failing tests.**

Create `tests/test_atom_card_renderer.py`:

```python
from pathlib import Path
from unittest.mock import MagicMock

from atom_loader import Atom
from models import AtomRef, PostBrief, Status, utc_now
from renderers.atom_card import AtomCardRenderer


def _brief(slugs: list[str], thesis: str = "Locked thesis line.") -> PostBrief:
    now = utc_now()
    return PostBrief(
        id="b1",
        slug="2026-05-25-atomcard-test",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug=s, role="primary", source="Test Source, 2026") for s in slugs],
        angle="An angle.",
        visual_tier="1_diagram",
        status=Status.GATE1_APPROVED,
        thesis=thesis,
    )


def _atom(slug: str, tldr: str | None) -> Atom:
    return Atom(
        slug=slug,
        title=slug.replace("-", " ").title(),
        type="concept",
        source_date="",
        body=f"Body for {slug}.",
        tags=[],
        domain="test",
        source="Test Source, 2026",
        tldr=tldr,
        path=None,
    )


def test_validate_rejects_more_than_three_atom_blocks_when_no_overflow():
    """≤3 distilled atoms is enforced in render path — but validate
    only flags illegal states. atom_count > 3 is legal (handled by overflow rule)."""
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, "tldr-" + s)

    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=None,
    )
    brief = _brief(["a", "b", "c", "d", "e"])
    errors = renderer.validate(brief)
    # 4+ atoms is allowed; overflow rule kicks in during render.
    assert errors == []


def test_validate_rejects_empty_thesis():
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, "tldr-" + s)
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=None,
    )
    brief = _brief(["a"], thesis="")
    errors = renderer.validate(brief)
    assert any("thesis" in e.lower() for e in errors)


def test_validate_rejects_zero_atoms():
    loader = MagicMock()
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=None,
    )
    brief = _brief([])
    errors = renderer.validate(brief)
    assert any("at least 1" in e.lower() or "zero" in e.lower() for e in errors)


def test_build_template_context_caps_at_three_with_overflow_line():
    """When 4+ atoms, first 3 render normally; remainder become overflow line."""
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, f"tldr-{s}")

    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=None,
    )
    brief = _brief(["a", "b", "c", "d", "e"])
    ctx = renderer._build_template_context(brief)
    assert len(ctx["atom_blocks"]) == 3
    assert ctx["atom_blocks"][0]["name"] == "A"
    assert ctx["overflow_line"] is not None
    assert "2 more" in ctx["overflow_line"]
    assert "d" in ctx["overflow_line"]
    assert "e" in ctx["overflow_line"]


def test_build_template_context_no_overflow_for_three_or_fewer():
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, f"tldr-{s}")
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=None,
    )
    brief = _brief(["a", "b", "c"])
    ctx = renderer._build_template_context(brief)
    assert len(ctx["atom_blocks"]) == 3
    assert ctx["overflow_line"] is None


def test_missing_tldr_triggers_filler_when_provided():
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, tldr=None)

    filler = MagicMock()
    filler.fill.return_value = "Filled tldr."

    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=filler,
    )
    brief = _brief(["a"])
    ctx = renderer._build_template_context(brief)
    assert ctx["atom_blocks"][0]["text"] == "Filled tldr."
    filler.fill.assert_called_once()


def test_missing_tldr_and_no_filler_renders_name_only():
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, tldr=None)
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=Path("01-projects/linkedin/brand-spec.md"),
        tldr_filler=None,
    )
    brief = _brief(["a"])
    ctx = renderer._build_template_context(brief)
    assert ctx["atom_blocks"][0]["name"] == "A"
    assert ctx["atom_blocks"][0]["text"] is None


def test_render_writes_png(tmp_path, atom_source, brand_spec):
    """Smoke: actual Playwright invocation produces a PNG file.

    Marked slow because it launches Chromium. Skip if env says so.
    """
    import os
    if os.environ.get("SKIP_PLAYWRIGHT_TESTS"):
        import pytest
        pytest.skip("SKIP_PLAYWRIGHT_TESTS=1")

    from atom_loader import AtomLoader
    loader = AtomLoader(atom_source)

    # Build a minimal brief using a real fixture atom.
    brief = _brief(["sample-concept"])
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    out_dir = tmp_path / "bundle"
    out_dir.mkdir()
    result = renderer.render(brief, out_dir)

    assert any(p.suffix == ".png" for p in result.asset_paths)
    assert all(Path(p).exists() and Path(p).stat().st_size > 0 for p in result.asset_paths)
```

- [ ] **Step 2: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_atom_card_renderer.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'renderers.atom_card'`.

- [ ] **Step 3: Implement the renderer.**

Create `src/renderers/atom_card.py`:

```python
"""Tier 1 atom-card renderer (Playwright + Jinja2)."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from atom_loader import AtomLoader
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_TEMPLATE_DIR = Path(__file__).parent / "templates"


class AtomCardRenderer:
    tier = 1

    def __init__(
        self,
        loader: AtomLoader,
        sources_registry: Any,
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
        if not brief.atoms_used:
            errors.append("at least 1 atom required")
        if not (brief.thesis or "").strip():
            errors.append("thesis must be non-empty (set brief.thesis before render)")
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        from playwright.sync_api import sync_playwright

        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._build_template_context(brief)
        template = self._env.get_template("atom_card.html.j2")
        html = template.render(**ctx)

        png_path = out_dir / "diagram.png"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(path=str(png_path), full_page=False, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            browser.close()

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered atom-card with {len(ctx['atom_blocks'])} atom blocks in {elapsed:.2f}s"],
        )

    # ---------- internals ----------

    def _build_template_context(self, brief: PostBrief) -> dict:
        colors = self.brand.get("colors", {})
        typography = self.brand.get("typography", {})

        refs = brief.atoms_used
        first_three = refs[:3]
        overflow = refs[3:]

        atom_blocks = []
        for ref in first_three:
            atom = self.loader.load_one(ref.slug)
            name = atom.title if atom else ref.slug
            tldr = (atom.tldr if atom else None) or self._fill_tldr(atom)
            atom_blocks.append({"name": name, "text": tldr})

        overflow_line = None
        if overflow:
            slugs = ", ".join(r.slug for r in overflow)
            overflow_line = f"+ {len(overflow)} more atoms inside the post · {slugs}"

        # Source for footer: first cited source from atoms.
        # Prefer atom.source / atom.origin; fall back to ref.source so callers
        # can override at the brief level.
        source_slug = ""
        for ref in refs:
            atom = self.loader.load_one(ref.slug)
            src: Optional[str] = None
            if atom:
                src = atom.source or atom.origin
            if not src:
                src = ref.source
            if src:
                source_slug = src
                break

        # Domain tag — try first atom's domain, fall back to strategy name.
        domain_tag = "second-brain"
        if refs:
            first_atom = self.loader.load_one(refs[0].slug)
            if first_atom and first_atom.domain:
                domain_tag = f"domain//{first_atom.domain}"

        atom_count = len(refs)
        footer_right = f"{atom_count} atom{'s' if atom_count != 1 else ''} · {brief.strategy.replace('_', '-')}"

        return {
            "colors": {
                "background": colors.get("background", "#FAF8F5"),
                "accent_primary": colors.get("accent_primary", "#B5654A"),
                "text_primary": colors.get("text_primary", "#2C2825"),
                "text_secondary": colors.get("text_secondary", "#6B6560"),
            },
            "typography": {
                "body": typography.get("body", "Geist, system-ui, sans-serif"),
                "mono": typography.get("mono", "Geist Mono, ui-monospace, monospace"),
            },
            "domain_tag": domain_tag,
            "thesis": brief.thesis,
            "atom_blocks": atom_blocks,
            "overflow_line": overflow_line,
            "source_slug": source_slug,
            "footer_right": footer_right,
        }

    def _fill_tldr(self, atom: Optional[Any]) -> Optional[str]:
        if atom is None or self.tldr_filler is None:
            return None
        return self.tldr_filler.fill(atom)
```

- [ ] **Step 4: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_atom_card_renderer.py -v
```

Expected: validation and context-building tests pass. The `test_render_writes_png` test launches Chromium and may take 3-5 seconds; pass means a non-empty PNG is produced.

If `test_render_writes_png` fails because Playwright Chromium isn't installed, re-run `python -m playwright install chromium`.

- [ ] **Step 5: Commit.**

```bash
git add src/renderers/atom_card.py tests/test_atom_card_renderer.py
git commit -m "$(cat <<'EOF'
feat(linkedin): AtomCardRenderer

Tier 1 renderer that produces the atom-card visual from a PostBrief:
loads brand tokens, resolves atoms (with TldrFiller fallback for
missing tldr), caps at 3 distilled blocks with "+N more" overflow,
renders the Jinja2 HTML template, and screenshots it at 1080×1080
via Playwright headless Chromium.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: CLI integration

**Files:**
- Modify: `src/cli/draft_post.py`
- Modify: `tests/test_cli_draft_post.py`

- [ ] **Step 1: Update CLI to use AtomCardRenderer.**

Open `src/cli/draft_post.py`. In `_generate`, after the `TextGenerator` line, also pass `sources_registry`:

Find:
```python
    client = _make_anthropic_client()
    gen = TextGenerator(client=client, loader=loader)
```

Replace with:
```python
    from sources.registry import SourcesRegistry

    sources_path = Path(os.environ.get("LINKEDIN_SOURCES_REGISTRY", project_root / "sources.yml"))
    sources_registry = SourcesRegistry(sources_path)

    client = _make_anthropic_client()
    gen = TextGenerator(client=client, loader=loader, sources_registry=sources_registry)
```

In `_advance`, replace the entire renderer block. Find:
```python
    if brief.visual_tier == "1_diagram":
        loader = AtomLoader(atom_source)
        graph = ConnectionGraph(loader.load_all())
        renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
        out_dir = project_root / "backlog" / slug
        validation_errors = renderer.validate(brief)
        edgeless = any("edgeless" in e.lower() for e in validation_errors)
        if edgeless and not args.force:
            print(
                "WARNING: Tier 1 diagram skipped — no connection atoms exist among the chosen atoms.",
                file=sys.stderr,
            )
            print(
                "  Bundle advanced to gate2_pending without a visual. Use --force to render anyway.",
                file=sys.stderr,
            )
            brief.visual_asset_paths = []
            brief.status = Status.GATE2_PENDING
            storage.write(brief)
            state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine", note="edgeless_tier1_skipped")
        else:
            result = renderer.render(brief, out_dir)
            brief.visual_asset_paths = [str(p) for p in result.asset_paths]
            brief.status = Status.GATE2_PENDING
            storage.write(brief)
            state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine")
    else:
```

Replace with:
```python
    if brief.visual_tier == "1_diagram":
        from renderers.atom_card import AtomCardRenderer
        from sources.registry import SourcesRegistry
        from sources.tldr_filler import TldrFiller

        loader = AtomLoader(atom_source)
        sources_path = Path(os.environ.get("LINKEDIN_SOURCES_REGISTRY", project_root / "sources.yml"))
        sources_registry = SourcesRegistry(sources_path)

        import anthropic
        client = anthropic.Anthropic()
        tldr_filler = TldrFiller(client=client)

        renderer = AtomCardRenderer(
            loader=loader,
            sources_registry=sources_registry,
            brand_spec_path=brand_spec,
            tldr_filler=tldr_filler,
        )
        out_dir = project_root / "backlog" / slug
        validation_errors = renderer.validate(brief)
        if validation_errors and not args.force:
            print("Renderer validation errors:", file=sys.stderr)
            for e in validation_errors:
                print(f"  - {e}", file=sys.stderr)
            print("Use --force to render anyway (will likely fail).", file=sys.stderr)
            return 5
        result = renderer.render(brief, out_dir)
        brief.visual_asset_paths = [str(p) for p in result.asset_paths]
        brief.status = Status.GATE2_PENDING
        storage.write(brief)
        state_log.record(slug, "gate1_approved", "gate2_pending", actor="engine")
    else:
```

Also remove the `from renderers.diagram import DiagramRenderer` line from the imports section of `_advance` and the `from connection_graph import ConnectionGraph` line if it's only used by the deleted block (check — `ConnectionGraph` may still be needed in `_generate`; if so, leave it).

- [ ] **Step 2: Update CLI test for new behavior.**

Open `tests/test_cli_draft_post.py`. Two changes:

(a) Find any test that asserts on the v1.0.1 edgeless guard. Common patterns to search for: `"edgeless_tier1_skipped"`, `"WARNING: Tier 1 diagram skipped"`, `"--force"` in the context of an edgeless test. Delete those assertions or the entire test function if the test only exists to exercise the edgeless guard.

(b) Find any test that mocks `DiagramRenderer` or imports `from renderers.diagram`. Update the import path to `from renderers.atom_card import AtomCardRenderer` and the patch target string to `"renderers.atom_card.AtomCardRenderer"`. Also update any kwarg-name assertions: the renderer no longer takes `graph=`; instead it takes `sources_registry=` and `tldr_filler=`. The test should pass with the same overall flow — only the renderer class name and kwargs change.

No new test is added in this task. The existing CLI tests already exercise the gate1 → gate2 flow; swapping the renderer class is sufficient coverage.

- [ ] **Step 3: Run CLI tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_cli_draft_post.py -v
```

Expected: tests pass. Any test that explicitly asserted the v1.0.1 edgeless-skip behavior should be updated or deleted (the behavior is gone).

- [ ] **Step 4: Commit.**

```bash
git add src/cli/draft_post.py tests/test_cli_draft_post.py
git commit -m "$(cat <<'EOF'
feat(linkedin): CLI uses AtomCardRenderer for Tier 1

_advance now instantiates AtomCardRenderer with SourcesRegistry +
TldrFiller and renders unconditionally. The v1.0.1 edgeless guard is
removed (the new renderer no longer has a graph-topology failure
mode). _generate passes SourcesRegistry into TextGenerator so
source-type-aware anchoring fires at draft time.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Strategy default flips

**Files:**
- Modify: `src/strategies/two_atom_bridge.py`
- Modify: `src/strategies/convergence_finder.py`
- Modify: `tests/test_two_atom_bridge.py`
- Modify: `tests/test_convergence_finder.py`

- [ ] **Step 1: Update failing assertion in two_atom_bridge test.**

Open `tests/test_two_atom_bridge.py`. Find the test that asserts `visual_tier == "0_text"` (likely named `test_default_visual_tier_is_text` or similar). Change the expected value to `"1_diagram"`:

```python
def test_default_visual_tier_is_diagram():
    # ... existing setup ...
    assert brief.visual_tier == "1_diagram"
```

- [ ] **Step 2: Update convergence_finder test similarly.**

Open `tests/test_convergence_finder.py`. Update any default-tier assertion from `"2_carousel"` to `"1_diagram"`.

- [ ] **Step 3: Run tests, verify fail.**

```bash
PYTHONPATH=src pytest tests/test_two_atom_bridge.py tests/test_convergence_finder.py -v
```

Expected: the updated assertions FAIL — strategies still emit the old defaults.

- [ ] **Step 4: Update two_atom_bridge default.**

Open `src/strategies/two_atom_bridge.py`. Find:

```python
            # Two-atom bridges default to text-only: a 2-node graphviz render
            # never adds information the sentence didn't already carry.
            # Override with --tier=1 to force a diagram when you genuinely want one.
            visual_tier="0_text",
```

Replace with:

```python
            visual_tier="1_diagram",
```

(Comment removed — the rationale no longer applies. v1.1 atom-card renderer handles 2 atoms cleanly.)

- [ ] **Step 5: Update convergence_finder default.**

Open `src/strategies/convergence_finder.py`. Find:

```python
            visual_tier="2_carousel",
```

Replace with:

```python
            visual_tier="1_diagram",
```

- [ ] **Step 6: Run tests, verify pass.**

```bash
PYTHONPATH=src pytest tests/test_two_atom_bridge.py tests/test_convergence_finder.py -v
```

Expected: all tests pass.

- [ ] **Step 7: Commit.**

```bash
git add src/strategies/two_atom_bridge.py src/strategies/convergence_finder.py tests/test_two_atom_bridge.py tests/test_convergence_finder.py
git commit -m "$(cat <<'EOF'
feat(linkedin): flip two_atom_bridge + convergence_finder to Tier 1

The atom-card renderer handles 2-3 atoms cleanly, so both strategies
default back to visual_tier=1_diagram. cluster_reveal stays at
2_carousel (deferred to v1.2).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: visual-discipline skill update

**Files:**
- Modify: `.claude/skills/linkedin/visual-discipline/SKILL.md`

This skill ships in `.claude/skills/`, not under `01-projects/linkedin/`. It still ships in the same commit since it's part of the v1.1 contract.

- [ ] **Step 1: Replace Tier 1 rules in protocol section.**

Open `.claude/skills/linkedin/visual-discipline/SKILL.md`. Find the protocol step about Tier 1 rules (currently inside `## Protocol` step 2):

```markdown
2. **Validate brief against tier rules:**
   - Tier 1: ≤6 nodes, every node has ≥1 edge, aspect ratio 1:1 or 4:5.
```

Replace with:

```markdown
2. **Validate brief against tier rules:**
   - Tier 1: ≤3 distilled atom blocks (4+ atoms apply overflow rule); non-empty thesis (extracted from `<THESIS>` or first-sentence fallback); `tldr` resolved for each shown atom (front-matter or LLM fill succeeded); source slug present in footer; aspect ratio 1:1.
```

- [ ] **Step 2: Replace anti-pattern table row for "Max 6 nodes".**

In the same file, find:

```markdown
| Max 6 nodes per diagram | Cognitive load; Miller's 7±2 minus margin |
| Edge labels when typed | Untyped edges are weakest connection-graph signal |
| No floating nodes (every node has ≥1 edge). |
```

Replace with:

```markdown
| ≤3 distilled atoms per card | Cognitive load on a 1:1 LinkedIn feed image |
| Non-empty thesis | Card needs a hero line for scroll-stop |
| Source slug in footer | "Visible system" payload must be present |
```

(Delete the "Edge labels" and "No floating nodes" lines — both obsolete.)

- [ ] **Step 3: Update Example 1.**

Find `### Example 1 — Tier 1 diagram approval`. Replace its body to reflect the new template:

```markdown
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
```

- [ ] **Step 4: Update Example 2.**

Find `### Example 2 — Tier 1 rejection`. Replace:

```markdown
### Example 2 — Tier 1 rejection (empty thesis)

Input: brief with 3 atoms but `brief.thesis == ""` (extraction fell back to empty, body had no usable first sentence).

Process:
1. Validate: thesis empty → FAIL.
2. Return validation error before invoking renderer.

Output: error surfaced to user; renderer not invoked; bundle stays in gate1_approved with a logged warning.
```

- [ ] **Step 5: Commit.**

```bash
git add .claude/skills/linkedin/visual-discipline/SKILL.md
git commit -m "$(cat <<'EOF'
docs(linkedin): visual-discipline skill — Tier 1 rules v1.1

Replaces graphviz-era rules (≤6 nodes, ≥1 edge per node, edge labels)
with atom-card rules (≤3 distilled blocks, non-empty thesis, tldr
resolved per shown atom, source slug in footer, 1:1 aspect). Examples
updated to match the new template.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: Delete graphviz renderer + cleanup

**Files:**
- Delete: `src/renderers/diagram.py`
- Delete: `tests/test_diagram_renderer.py`

- [ ] **Step 1: Confirm no remaining imports.**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin
grep -rn "from renderers.diagram\|renderers\.diagram\|DiagramRenderer\b" src/ tests/ || echo "no remaining references"
```

Expected: `no remaining references`. If anything appears, replace it (likely in `src/cli/linkedin_status.py` or other CLIs).

- [ ] **Step 2: Delete the files.**

```bash
git rm src/renderers/diagram.py tests/test_diagram_renderer.py
```

- [ ] **Step 3: Run the full test suite.**

```bash
PYTHONPATH=src pytest tests/ -v
```

Expected: all tests pass (no import errors, no missing references).

- [ ] **Step 4: Commit.**

```bash
git commit -m "$(cat <<'EOF'
chore(linkedin): delete graphviz renderer

DiagramRenderer is superseded by AtomCardRenderer. The 3-floating-ovals
failure mode is gone with it; no opt-in keepalive (if a future feature
needs a network diagram, ship it as a separate renderer).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: End-to-end smoke test (user-run)

This task is user-executed and records its result in the decision log. Engineer running the plan should hand the commands to the user after Task 13 commits.

- [ ] **Step 1: Run the smoke commands.**

```bash
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
LINKEDIN_SOURCES_REGISTRY=/Users/gozzynwogbo/second-brain/01-projects/linkedin/sources.yml \
python3 -m cli.draft_post --strategy=source_spotlight --source='Richard Rumelt, 2011' --no-render
```

Expected: bundle written, status `text_ready`. Inspect `backlog/<slug>/text.md` — body should include the full Rumelt bio sentence (from sources.yml) and NOT include `<THESIS>` tags. `meta.json` should have non-empty `thesis`.

- [ ] **Step 2: Advance and render.**

```bash
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
LINKEDIN_SOURCES_REGISTRY=/Users/gozzynwogbo/second-brain/01-projects/linkedin/sources.yml \
python3 -m cli.draft_post --advance <slug-from-step-1>
```

Expected: renderer launches Chromium, writes `backlog/<slug>/diagram.png` (1080×1080). Bundle status advances to `gate2_pending`.

- [ ] **Step 3: Open the PNG and inspect.**

```bash
open backlog/<slug>/diagram.png
```

Visual checks:
- Meta row reads "FROM SECOND BRAIN" on the left, "DOMAIN//STRATEGY" on the right.
- Thesis is the display-type hero, ≤2 lines.
- 3 atom blocks with terracotta dot, name, and distillation each.
- No dividers between atom blocks.
- Footer shows "richard-rumelt, 2011" and "3 atoms · source-spotlight".

If the smoke output looks good, append to `01-projects/linkedin/docs/decision-log.md`:

```markdown
## 2026-05-XX — v1.1 smoke result (user-run)

[Write 3-5 sentences on what shipped well, what didn't, follow-ups deferred to v1.1.x.]
```

- [ ] **Step 4: Merge to main when smoke passes.**

```bash
cd /Users/gozzynwogbo/second-brain
git checkout main
git merge --no-ff feat/linkedin-engine-v1.1
git push origin main
```

If a v1.1.x patch turns out to be needed (the v1.0 cycle needed two), follow the same patch-before-ship pattern: branch off `feat/linkedin-engine-v1.1.1`, fix, re-smoke, merge.

---

## Self-review

The plan covers:

- [x] Spec §2 (visual template): Tasks 8, 9 (template + renderer + overflow rule + scaling).
- [x] Spec §2.3 (single-atom case): same template handles it; no special branch needed; renderer test covers `_brief(["a"])`.
- [x] Spec §3.1 (atom v2.2 tldr): Task 3.
- [x] Spec §3.2 (sources registry): Task 4.
- [x] Spec §3.3 (PostBrief.thesis): Task 2.
- [x] Spec §3.4 (LLM fallback for missing tldr): Task 5 (TldrFiller) + Task 9 (wired in renderer).
- [x] Spec §4.1 (THESIS tags): Task 6 (extractor) + Task 7 (generator integration).
- [x] Spec §4.2 (source-type-aware anchor): Task 7 (voice prompt + per-atom source lookup in user prompt).
- [x] Spec §5 (Playwright renderer): Tasks 1, 8, 9.
- [x] Spec §5.4 (deletions): Task 13.
- [x] Spec §6 (strategy default flips): Task 11.
- [x] Spec §7 (visual-discipline skill update): Task 12.
- [x] Spec §8 (failure modes): covered across tasks 5, 6, 9 with degraded-render + warn behaviors.
- [x] Spec §10 (smoke test): Task 14.

Types and signatures referenced across tasks:
- `Atom.tldr: Optional[str]` (Task 3) consumed by `AtomCardRenderer` (Task 9) and `TldrFiller.fill` (Task 5). ✓
- `PostBrief.thesis: str` (Task 2) consumed by `AtomCardRenderer.validate` and template context (Task 9). ✓
- `SourcesRegistry.lookup(str) → Optional[SourceEntry]` (Task 4) consumed by `TextGenerator.generate` (Task 7). ✓
- `TldrFiller(client, model).fill(atom) → Optional[str]` (Task 5) consumed by `AtomCardRenderer._fill_tldr` (Task 9). ✓
- `extract_thesis(body) → ExtractionResult(thesis, clean_body, warning)` (Task 6) consumed by `TextGenerator.generate` (Task 7). ✓

No placeholders, TBDs, or "implement similar to" references. Every code step contains the actual code to write.

---

*Companion docs:*
- *Design spec: `2026-05-25-tier1-redesign-design.md`*
- *Original engine design: `2026-05-24-linkedin-engine-design.md`*
- *Decision log: `decision-log.md`*
