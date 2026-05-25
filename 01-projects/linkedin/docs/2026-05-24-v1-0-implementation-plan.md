# LinkedIn Engine v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a working LinkedIn content engine that produces one Tier 1 post end-to-end (atom selection → drafted text → atom-graph diagram → reviewable bundle on disk), with conversational + slash-command interface.

**Architecture:** Python module at `01-projects/linkedin/src/`. Strategy modules read atoms from `02-knowledge/`, produce a `PostBrief`. Text generator calls Claude API constrained by voice rules. Diagram renderer uses graphviz. Filesystem storage adapter writes bundle folders to `01-projects/linkedin/backlog/`. Two slash commands (`/draft-post`, `/linkedin-status`) wrap the CLI entry points. Anti-repeat enforced via state files (`atom-usage.json`, `connection-usage.json`).

**Tech Stack:** Python 3.11+, `graphviz` (Python binding + system binary), `python-frontmatter`, `pyyaml`, `anthropic` SDK, `pytest` + `pytest-mock`.

**Companion docs:**
- Design spec: `01-projects/linkedin/docs/2026-05-24-linkedin-engine-design.md`
- Command reference: `01-projects/linkedin/docs/command-reference.md`

**Scope of this plan:** v1.0 only. Tier 2 (carousel), Tier 3 (video), Supabase migration, scheduler integration, and analytics are out of scope — separate plans.

---

## Phase A — Project scaffolding

### Task A1: Create project directory tree

**Files:**
- Create: `01-projects/linkedin/src/__init__.py`
- Create: `01-projects/linkedin/src/strategies/__init__.py`
- Create: `01-projects/linkedin/src/renderers/__init__.py`
- Create: `01-projects/linkedin/src/storage/__init__.py`
- Create: `01-projects/linkedin/src/linter/__init__.py`
- Create: `01-projects/linkedin/src/usage/__init__.py`
- Create: `01-projects/linkedin/src/cli/__init__.py`
- Create: `01-projects/linkedin/tests/__init__.py`
- Create: `01-projects/linkedin/backlog/.gitkeep`
- Create: `01-projects/linkedin/state/.gitkeep`
- Create: `01-projects/linkedin/logs/.gitkeep`

- [ ] **Step 1: Create directories and empty init files**

```bash
cd /Users/gozzynwogbo/second-brain
mkdir -p 01-projects/linkedin/{src/{strategies,renderers,storage,linter,usage,cli},tests,backlog,state,logs}
touch 01-projects/linkedin/src/__init__.py
touch 01-projects/linkedin/src/{strategies,renderers,storage,linter,usage,cli}/__init__.py
touch 01-projects/linkedin/tests/__init__.py
touch 01-projects/linkedin/{backlog,state,logs}/.gitkeep
```

- [ ] **Step 2: Verify structure**

```bash
find 01-projects/linkedin -type d | sort
```

Expected: 12 directories listed including `src/`, `src/strategies/`, `src/renderers/`, etc.

- [ ] **Step 3: Commit**

```bash
git add -f 01-projects/linkedin/
git commit -m "feat(linkedin): scaffold v1.0 project directory tree"
```

Note: `-f` because `01-projects/*` is gitignored. Confirm with user before this commit; alternative is to leave the project uncommitted and rely on local files only.

---

### Task A2: Project-level CLAUDE.md

**Files:**
- Create: `01-projects/linkedin/CLAUDE.md`

- [ ] **Step 1: Write CLAUDE.md**

```markdown
# CLAUDE.md — LinkedIn Engine

This file documents conventions for the LinkedIn content engine. The engine is
designed to function standalone when extracted from the second-brain vault.

## Purpose

On-demand engine that produces LinkedIn-ready post bundles (text + visual)
from the second-brain atom graph. See `docs/2026-05-24-linkedin-engine-design.md`
for full design.

## Project structure

- `src/` — Python implementation
  - `strategies/` — atom selection → PostBrief
  - `renderers/` — PostBrief → visual asset (Tier 1 only in v1.0)
  - `storage/` — bundle persistence (filesystem in v1.0)
  - `linter/` — voice rule enforcement
  - `usage/` — cooldown tracking + scoring
  - `cli/` — `/draft-post` and `/linkedin-status` entry points
- `tests/` — pytest suite
- `backlog/` — generated post bundles (one folder per post)
- `state/` — atom-usage.json, connection-usage.json, rejections.jsonl, approvals.jsonl
- `logs/` — state.jsonl, cost.jsonl, errors.jsonl
- `brand-spec.md` — visual brand tokens (placeholder in v1.0; replaced by brand revamp)

## Conventions

- All Python code is type-hinted. Pyright-strict where feasible.
- Voice rules enforced via `src/linter/rules.yml`. Edit YAML, not code.
- State transitions ALWAYS go through the storage adapter, never direct JSON writes.
- Atom source path is configurable: defaults to `../../02-knowledge/` relative to project root.
- When extracted from the vault, point the atom source config at any directory of atom markdown files.

## How to run

```
python -m linkedin_engine.cli.draft_post [args]
python -m linkedin_engine.cli.linkedin_status [args]
```

The slash commands at `.claude/commands/draft-post.md` and `.claude/commands/linkedin-status.md` wrap these.

## Testing

```
pytest tests/ -v
```

## Voice rules

See vault-level `CLAUDE.md` §3. Engine enforces a subset programmatically via the voice linter.
```

- [ ] **Step 2: Commit**

```bash
git add -f 01-projects/linkedin/CLAUDE.md
git commit -m "feat(linkedin): add project-level CLAUDE.md"
```

---

### Task A3: Placeholder brand-spec.md

**Files:**
- Create: `01-projects/linkedin/brand-spec.md`

- [ ] **Step 1: Write placeholder brand spec**

```markdown
# Brand Spec — PLACEHOLDER

**Status:** Placeholder for v1.0. Will be replaced by brand revamp workstream output.

## Tokens

```yaml
colors:
  accent_primary: "#1F1F1F"     # placeholder neutral
  accent_secondary: "#737373"
  background: "#FFFFFF"
  edge_default: "#737373"
  edge_mechanism: "#1F1F1F"
  edge_analogical: "#737373"    # dashed
  text_primary: "#1F1F1F"
  text_secondary: "#525252"

typography:
  body: "system-ui, -apple-system, sans-serif"
  display: "system-ui, -apple-system, sans-serif"
  mono: "ui-monospace, monospace"
  size_body: "14px"
  size_label: "11px"
  size_title: "18px"

layout:
  aspect_ratios: ["1:1", "4:5"]
  padding: 32
  node_padding: 12
  edge_thickness_default: 1.5
  edge_thickness_emphasis: 2.5

anti_patterns:
  - "no center-radial-gradient backgrounds"
  - "no drop shadows on nodes"
  - "no all-caps labels"
  - "minimum 16px between adjacent nodes"
```

## Notes

Once the brand revamp workstream completes, replace this file (or symlink it) to the brand revamp output. All renderers read tokens from this file; nothing in code hardcodes brand decisions.
```

- [ ] **Step 2: Commit**

```bash
git add -f 01-projects/linkedin/brand-spec.md
git commit -m "feat(linkedin): add placeholder brand-spec (replaced by brand revamp later)"
```

---

### Task A4: pyproject.toml + requirements

**Files:**
- Create: `01-projects/linkedin/pyproject.toml`
- Create: `01-projects/linkedin/requirements.txt`
- Create: `01-projects/linkedin/requirements-dev.txt`

- [ ] **Step 1: Write pyproject.toml**

```toml
[project]
name = "linkedin-engine"
version = "0.1.0"
description = "On-demand LinkedIn content engine driven by second-brain atom graph"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.40.0",
    "graphviz>=0.20.3",
    "python-frontmatter>=1.1.0",
    "pyyaml>=6.0.2",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --tb=short"
```

- [ ] **Step 2: Write requirements.txt (pinned for reproducibility)**

```
anthropic==0.40.0
graphviz==0.20.3
python-frontmatter==1.1.0
PyYAML==6.0.2
```

- [ ] **Step 3: Write requirements-dev.txt**

```
-r requirements.txt
pytest==8.3.4
pytest-mock==3.14.0
```

- [ ] **Step 4: Verify graphviz system binary is installed**

```bash
which dot || echo "MISSING: brew install graphviz"
```

Expected: path to `dot` binary, OR the "MISSING" message (run `brew install graphviz` if missing).

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/pyproject.toml 01-projects/linkedin/requirements.txt 01-projects/linkedin/requirements-dev.txt
git commit -m "feat(linkedin): add Python project config + dependencies"
```

---

### Task A5: Pytest config + test fixtures

**Files:**
- Create: `01-projects/linkedin/tests/conftest.py`
- Create: `01-projects/linkedin/tests/fixtures/atoms/concepts/sample-concept.md`
- Create: `01-projects/linkedin/tests/fixtures/atoms/connections/sample-bridge.md`

- [ ] **Step 1: Write conftest.py with shared fixtures**

```python
"""Shared pytest fixtures for linkedin engine tests."""
import shutil
from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def atom_source(tmp_path: Path) -> Path:
    """Copy fixture atoms to a tmp dir; return the dir path."""
    dest = tmp_path / "atoms"
    shutil.copytree(FIXTURES_DIR / "atoms", dest)
    return dest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Bare project root with state/, backlog/, logs/ subfolders."""
    for sub in ("state", "backlog", "logs"):
        (tmp_path / sub).mkdir()
    return tmp_path


@pytest.fixture
def brand_spec(tmp_path: Path) -> Path:
    """Minimal brand-spec for renderer tests."""
    path = tmp_path / "brand-spec.md"
    path.write_text(
        '```yaml\n'
        'colors:\n'
        '  accent_primary: "#1F1F1F"\n'
        '  background: "#FFFFFF"\n'
        '  edge_default: "#737373"\n'
        'typography:\n'
        '  body: "sans-serif"\n'
        '  size_label: "11px"\n'
        'layout:\n'
        '  padding: 32\n'
        '  node_padding: 12\n'
        '```\n'
    )
    return path
```

- [ ] **Step 2: Write a sample concept atom fixture**

```bash
mkdir -p 01-projects/linkedin/tests/fixtures/atoms/{concepts,connections}
```

Then create `01-projects/linkedin/tests/fixtures/atoms/concepts/sample-concept.md`:

```markdown
---
title: Sample Concept
type: concept
source_date: 2026-05-01
tags: [sample, testing]
domain: testing
origin: test-fixture
---

A sample concept used in fixture tests. Body content is intentionally short.
```

- [ ] **Step 3: Write a sample connection atom fixture**

`01-projects/linkedin/tests/fixtures/atoms/connections/sample-bridge.md`:

```markdown
---
title: sample-bridge
type: connection
source_date: 2026-05-01
from: Sample Concept
to: Another Concept
connection_type: mechanism
---

The two concepts share a feedback-loop mechanism.
```

- [ ] **Step 4: Run pytest to confirm it discovers tests cleanly (no tests yet, no failures)**

```bash
cd 01-projects/linkedin && pytest tests/ -v
```

Expected: `no tests ran` or similar — exit code 5 acceptable, fixtures load without error.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/tests/
git commit -m "test(linkedin): pytest config + shared fixtures + sample atoms"
```

---

## Phase B — Atom-front-matter v2.1

### Task B1: Add connection_type field to atom standard

**Files:**
- Modify: `.claude/standards/atom-front-matter.md`

- [ ] **Step 1: Read current standard to find insertion point**

```bash
grep -n "connection atoms" /Users/gozzynwogbo/second-brain/.claude/standards/atom-front-matter.md | head -5
```

Expected: line numbers locating the connection-specific section.

- [ ] **Step 2: Add `connection_type` field to the optional-fields table**

Locate the "Optional fields" table in `.claude/standards/atom-front-matter.md`. Add this row to the table:

```markdown
| `connection_type` | enum | Type of relationship (see §Connection types). Optional; defaults to `general`. | `connection_type: mechanism` |
```

- [ ] **Step 3: Append a Connection types section to the standard**

Append to the end of `.claude/standards/atom-front-matter.md`:

```markdown
---

## Connection types (v2.1)

Connection atoms may include an optional `connection_type` field. Value is one of:

| Type | Meaning |
|---|---|
| `mechanism` | Both endpoints implement the same underlying mechanism |
| `analogical` | Different domains, structurally similar |
| `causal` | One sets up or produces the other |
| `inverse` | Opposites in a meaningful way |
| `compositional` | One is a part of the other / they compose |
| `genealogical` | One historically came from the other |
| `critique` | One refines or pushes against the other |
| `epistemic` | Same thing seen from different ways of knowing |
| `general` | Untyped (default for legacy and unclassified) |

Migration: no breaking change. Legacy connection atoms with no `connection_type`
field are treated as `general`. New connections should declare a type.
```

- [ ] **Step 4: Commit**

```bash
git add .claude/standards/atom-front-matter.md
git commit -m "feat(atoms): atom-front-matter v2.1 — optional connection_type field with 8 typed values"
```

---

## Phase C — Core models and loading

### Task C1: PostBrief dataclass

**Files:**
- Create: `01-projects/linkedin/src/models.py`
- Create: `01-projects/linkedin/tests/test_models.py`

- [ ] **Step 1: Write failing test for PostBrief construction and serialization**

```python
# tests/test_models.py
import json
from datetime import datetime, timezone

from linkedin_engine.models import PostBrief, AtomRef, Status


def test_postbrief_roundtrip():
    brief = PostBrief(
        id="abc-123",
        slug="2026-05-24-sample",
        created_at=datetime(2026, 5, 24, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 24, tzinfo=timezone.utc),
        strategy="source_spotlight",
        strategy_params={"source": "Nate B. Jones", "atom_count": 3},
        atoms_used=[AtomRef(slug="x", role="primary", source="Nate B. Jones")],
        angle="Three ideas from X all touch Y.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    payload = brief.to_dict()
    restored = PostBrief.from_dict(payload)
    assert restored.slug == "2026-05-24-sample"
    assert restored.atoms_used[0].slug == "x"
    assert restored.status is Status.DRAFTING
    # JSON round-trip
    encoded = json.dumps(payload, default=str)
    decoded = json.loads(encoded)
    assert decoded["strategy"] == "source_spotlight"
```

- [ ] **Step 2: Run test to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_models.py -v
```

Expected: FAIL with `ModuleNotFoundError: linkedin_engine`.

- [ ] **Step 3: Wire the package import path**

Add to `01-projects/linkedin/pyproject.toml` under `[project]`:

```toml
[tool.setuptools.packages.find]
where = ["src"]
namespaces = false

[tool.setuptools.package-dir]
linkedin_engine = "src"
```

Actually simpler: skip setuptools wiring. Use `conftest.py` to add `src/` to sys.path. Append to `tests/conftest.py`:

```python
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

Note: changes the import path from `linkedin_engine.models` to just `models`. Update the test accordingly:

```python
from models import PostBrief, AtomRef, Status
```

- [ ] **Step 4: Implement `src/models.py`**

```python
"""Core data models for the LinkedIn engine."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class Status(str, Enum):
    DRAFTING = "drafting"
    TEXT_READY = "text_ready"
    GATE1_APPROVED = "gate1_approved"
    RENDERING = "rendering"
    GATE2_PENDING = "gate2_pending"
    READY_TO_POST = "ready_to_post"
    POSTED = "posted"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class AtomRef:
    slug: str
    role: str  # "primary" | "auxiliary"
    source: Optional[str] = None


@dataclass
class TextConstraints:
    voice_rules: list[str] = field(default_factory=list)
    word_range: tuple[int, int] = (80, 200)


@dataclass
class PostBrief:
    id: str
    slug: str
    created_at: datetime
    updated_at: datetime
    strategy: str
    strategy_params: dict[str, Any]
    atoms_used: list[AtomRef]
    angle: str
    visual_tier: str  # "1_diagram" | "2_carousel" | "3_video"
    status: Status
    text_constraints: TextConstraints = field(default_factory=TextConstraints)
    draft_text: str = ""
    approved_text: str = ""
    edit_delta: Optional[dict[str, Any]] = None
    visual_brief: dict[str, Any] = field(default_factory=dict)
    visual_asset_paths: list[str] = field(default_factory=list)
    series: Optional[str] = None
    topic_tags: list[str] = field(default_factory=list)
    target_platforms: list[str] = field(default_factory=lambda: ["linkedin_profile"])
    status_history: list[dict[str, Any]] = field(default_factory=list)
    # v2 fields, nullable in v1
    scheduled_time: Optional[datetime] = None
    scheduler_platform: Optional[str] = None
    scheduler_post_id: Optional[str] = None
    published_url: Optional[str] = None
    metrics: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        if self.scheduled_time:
            d["scheduled_time"] = self.scheduled_time.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PostBrief":
        atoms = [AtomRef(**a) for a in d.get("atoms_used", [])]
        constraints = TextConstraints(**d.get("text_constraints", {}))
        return cls(
            id=d["id"],
            slug=d["slug"],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
            strategy=d["strategy"],
            strategy_params=d.get("strategy_params", {}),
            atoms_used=atoms,
            angle=d.get("angle", ""),
            visual_tier=d.get("visual_tier", "1_diagram"),
            status=Status(d["status"]),
            text_constraints=constraints,
            draft_text=d.get("draft_text", ""),
            approved_text=d.get("approved_text", ""),
            edit_delta=d.get("edit_delta"),
            visual_brief=d.get("visual_brief", {}),
            visual_asset_paths=d.get("visual_asset_paths", []),
            series=d.get("series"),
            topic_tags=d.get("topic_tags", []),
            target_platforms=d.get("target_platforms", ["linkedin_profile"]),
            status_history=d.get("status_history", []),
            scheduled_time=datetime.fromisoformat(d["scheduled_time"]) if d.get("scheduled_time") else None,
            scheduler_platform=d.get("scheduler_platform"),
            scheduler_post_id=d.get("scheduler_post_id"),
            published_url=d.get("published_url"),
            metrics=d.get("metrics"),
        )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_models.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/models.py 01-projects/linkedin/tests/test_models.py 01-projects/linkedin/tests/conftest.py
git commit -m "feat(linkedin): PostBrief dataclass + JSON round-trip"
```

---

### Task C2: AtomLoader

**Files:**
- Create: `01-projects/linkedin/src/atom_loader.py`
- Create: `01-projects/linkedin/tests/test_atom_loader.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_atom_loader.py
from pathlib import Path

from atom_loader import Atom, AtomLoader


def test_loads_concept_atom(atom_source: Path):
    loader = AtomLoader(atom_source)
    atoms = loader.load_all()
    titles = [a.title for a in atoms]
    assert "Sample Concept" in titles


def test_filter_by_source(atom_source: Path):
    loader = AtomLoader(atom_source)
    atoms = loader.load_by_source("test-fixture")
    assert all(a.origin == "test-fixture" for a in atoms)


def test_atom_has_slug(atom_source: Path):
    loader = AtomLoader(atom_source)
    atoms = loader.load_all()
    concept = next(a for a in atoms if a.title == "Sample Concept")
    assert concept.slug == "sample-concept"
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_atom_loader.py -v
```

Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `src/atom_loader.py`**

```python
"""Load atoms (concepts, frameworks, principles, connections) from a vault directory."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import frontmatter


@dataclass
class Atom:
    slug: str               # filename stem (kebab-case)
    title: str
    type: str               # "concept" | "framework" | "principle" | "connection"
    source_date: str
    body: str
    tags: list[str] = field(default_factory=list)
    domain: Optional[str] = None
    origin: Optional[str] = None
    source: Optional[str] = None
    path: Optional[Path] = None
    # connection-specific
    from_atom: Optional[str] = None
    to_atom: Optional[str] = None
    connection_type: str = "general"


class AtomLoader:
    """Reads atom markdown files from a directory tree."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def load_all(self) -> list[Atom]:
        atoms: list[Atom] = []
        for path in self.root.rglob("*.md"):
            try:
                atom = self._parse(path)
                if atom:
                    atoms.append(atom)
            except Exception:
                continue
        return atoms

    def load_by_source(self, source: str) -> list[Atom]:
        return [a for a in self.load_all() if a.origin == source or a.source == source]

    def load_by_tag(self, tag: str) -> list[Atom]:
        return [a for a in self.load_all() if tag in a.tags]

    def load_one(self, slug: str) -> Optional[Atom]:
        return next((a for a in self.load_all() if a.slug == slug), None)

    def _parse(self, path: Path) -> Optional[Atom]:
        post = frontmatter.load(path)
        meta = post.metadata
        if "title" not in meta or "type" not in meta:
            return None
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
            path=path,
            from_atom=meta.get("from"),
            to_atom=meta.get("to"),
            connection_type=meta.get("connection_type", "general"),
        )
```

- [ ] **Step 4: Install python-frontmatter and run test**

```bash
cd 01-projects/linkedin && pip install -r requirements-dev.txt && pytest tests/test_atom_loader.py -v
```

Expected: PASS all three tests.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/atom_loader.py 01-projects/linkedin/tests/test_atom_loader.py
git commit -m "feat(linkedin): AtomLoader reads vault atom markdown into typed objects"
```

---

### Task C3: ConnectionGraph helper

**Files:**
- Create: `01-projects/linkedin/src/connection_graph.py`
- Create: `01-projects/linkedin/tests/test_connection_graph.py`
- Modify: `01-projects/linkedin/tests/fixtures/atoms/concepts/another-concept.md` (NEW)

- [ ] **Step 1: Add a second concept fixture so connections have both endpoints**

Create `01-projects/linkedin/tests/fixtures/atoms/concepts/another-concept.md`:

```markdown
---
title: Another Concept
type: concept
source_date: 2026-05-02
tags: [sample, testing]
domain: testing
origin: test-fixture
---

A second concept for connection tests.
```

- [ ] **Step 2: Write failing test**

```python
# tests/test_connection_graph.py
from atom_loader import AtomLoader
from connection_graph import ConnectionGraph


def test_edges_for_atom(atom_source):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    edges = graph.edges_for("sample-concept")
    assert len(edges) == 1
    edge = edges[0]
    assert edge.from_title == "Sample Concept"
    assert edge.to_title == "Another Concept"
    assert edge.connection_type == "mechanism"


def test_edges_by_type(atom_source):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    mech_edges = graph.edges_by_type("mechanism")
    assert len(mech_edges) == 1
```

- [ ] **Step 3: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_connection_graph.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 4: Implement `src/connection_graph.py`**

```python
"""Build a connection graph from loaded atoms."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from atom_loader import Atom


@dataclass
class Edge:
    from_slug: str
    to_slug: str
    from_title: str
    to_title: str
    connection_type: str
    claim: str               # body of the connection atom


def _slugify(title: str) -> str:
    return title.lower().replace(" ", "-")


class ConnectionGraph:
    def __init__(self, atoms: Iterable[Atom]):
        atoms_list = list(atoms)
        self._title_to_slug = {a.title: a.slug for a in atoms_list if a.type != "connection"}
        self._slug_to_atom = {a.slug: a for a in atoms_list if a.type != "connection"}
        self.edges: list[Edge] = []
        for a in atoms_list:
            if a.type != "connection" or not (a.from_atom and a.to_atom):
                continue
            from_slug = self._title_to_slug.get(a.from_atom) or _slugify(a.from_atom)
            to_slug = self._title_to_slug.get(a.to_atom) or _slugify(a.to_atom)
            self.edges.append(Edge(
                from_slug=from_slug,
                to_slug=to_slug,
                from_title=a.from_atom,
                to_title=a.to_atom,
                connection_type=a.connection_type,
                claim=a.body.strip(),
            ))

    def edges_for(self, slug: str) -> list[Edge]:
        return [e for e in self.edges if e.from_slug == slug or e.to_slug == slug]

    def edges_by_type(self, connection_type: str) -> list[Edge]:
        return [e for e in self.edges if e.connection_type == connection_type]

    def neighbors(self, slug: str) -> list[str]:
        result: set[str] = set()
        for e in self.edges_for(slug):
            other = e.to_slug if e.from_slug == slug else e.from_slug
            result.add(other)
        return sorted(result)
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_connection_graph.py -v
```

Expected: PASS both tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/connection_graph.py 01-projects/linkedin/tests/test_connection_graph.py 01-projects/linkedin/tests/fixtures/
git commit -m "feat(linkedin): ConnectionGraph builds typed edges from connection atoms"
```

---

## Phase D — Storage adapter

### Task D1: FilesystemAdapter — write + read

**Files:**
- Create: `01-projects/linkedin/src/storage/base.py`
- Create: `01-projects/linkedin/src/storage/filesystem.py`
- Create: `01-projects/linkedin/tests/test_filesystem_storage.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_filesystem_storage.py
from datetime import datetime, timezone
from pathlib import Path

from models import AtomRef, PostBrief, Status
from storage.filesystem import FilesystemAdapter


def _make_brief() -> PostBrief:
    now = datetime.now(timezone.utc)
    return PostBrief(
        id="brief-1",
        slug="2026-05-24-test-bridge",
        created_at=now,
        updated_at=now,
        strategy="two_atom_bridge",
        strategy_params={"atom_a": "sample-concept", "atom_b": "another-concept"},
        atoms_used=[
            AtomRef(slug="sample-concept", role="primary"),
            AtomRef(slug="another-concept", role="primary"),
        ],
        angle="Two atoms walk into a bridge.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        draft_text="Draft body text.",
    )


def test_write_then_read(project_root: Path):
    adapter = FilesystemAdapter(project_root)
    brief = _make_brief()
    adapter.write(brief)
    loaded = adapter.read("2026-05-24-test-bridge")
    assert loaded.slug == brief.slug
    assert loaded.angle == brief.angle


def test_write_creates_text_md(project_root: Path):
    adapter = FilesystemAdapter(project_root)
    brief = _make_brief()
    adapter.write(brief)
    bundle = project_root / "backlog" / "2026-05-24-test-bridge"
    assert (bundle / "meta.json").exists()
    assert (bundle / "text.md").exists()
    assert "Draft body text" in (bundle / "text.md").read_text()


def test_list_returns_all(project_root: Path):
    adapter = FilesystemAdapter(project_root)
    adapter.write(_make_brief())
    slugs = adapter.list_slugs()
    assert "2026-05-24-test-bridge" in slugs
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_filesystem_storage.py -v
```

Expected: FAIL — `ModuleNotFoundError`.

- [ ] **Step 3: Implement `src/storage/base.py`**

```python
"""Storage adapter protocol."""
from __future__ import annotations

from typing import Protocol

from models import PostBrief, Status


class StorageAdapter(Protocol):
    def write(self, brief: PostBrief) -> None: ...
    def read(self, slug: str) -> PostBrief: ...
    def list_slugs(self) -> list[str]: ...
    def update_status(self, slug: str, new_status: Status, actor: str = "user") -> PostBrief: ...
    def delete(self, slug: str) -> None: ...
```

- [ ] **Step 4: Implement `src/storage/filesystem.py`**

```python
"""Filesystem-backed storage adapter (v1.0)."""
from __future__ import annotations

import json
from pathlib import Path

from models import PostBrief, Status, utc_now


class FilesystemAdapter:
    def __init__(self, project_root: Path):
        self.root = Path(project_root)
        self.backlog = self.root / "backlog"
        self.backlog.mkdir(parents=True, exist_ok=True)

    def _bundle_dir(self, slug: str) -> Path:
        return self.backlog / slug

    def write(self, brief: PostBrief) -> None:
        bundle = self._bundle_dir(brief.slug)
        bundle.mkdir(parents=True, exist_ok=True)
        (bundle / "meta.json").write_text(
            json.dumps(brief.to_dict(), indent=2, default=str)
        )
        text = brief.approved_text or brief.draft_text or ""
        (bundle / "text.md").write_text(text + ("\n" if text and not text.endswith("\n") else ""))

    def read(self, slug: str) -> PostBrief:
        bundle = self._bundle_dir(slug)
        meta = json.loads((bundle / "meta.json").read_text())
        return PostBrief.from_dict(meta)

    def list_slugs(self) -> list[str]:
        return sorted([p.name for p in self.backlog.iterdir() if p.is_dir()])

    def update_status(self, slug: str, new_status: Status, actor: str = "user") -> PostBrief:
        brief = self.read(slug)
        brief.status = new_status
        brief.updated_at = utc_now()
        brief.status_history.append({
            "status": new_status.value,
            "timestamp": brief.updated_at.isoformat(),
            "actor": actor,
        })
        self.write(brief)
        return brief

    def delete(self, slug: str) -> None:
        bundle = self._bundle_dir(slug)
        if bundle.exists():
            for child in bundle.iterdir():
                child.unlink()
            bundle.rmdir()
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_filesystem_storage.py -v
```

Expected: PASS all three tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/storage/ 01-projects/linkedin/tests/test_filesystem_storage.py
git commit -m "feat(linkedin): FilesystemAdapter writes/reads bundle folders + meta.json"
```

---

### Task D2: Status transitions + state logging

**Files:**
- Modify: `01-projects/linkedin/src/storage/filesystem.py`
- Create: `01-projects/linkedin/src/state_log.py`
- Create: `01-projects/linkedin/tests/test_state_log.py`

- [ ] **Step 1: Write failing test for state log appending**

```python
# tests/test_state_log.py
import json
from datetime import datetime, timezone
from pathlib import Path

from state_log import StateLog


def test_appends_jsonl(project_root: Path):
    log = StateLog(project_root / "logs" / "state.jsonl")
    log.record(slug="x", from_status="drafting", to_status="text_ready", actor="engine")
    log.record(slug="x", from_status="text_ready", to_status="gate1_approved", actor="user")
    lines = (project_root / "logs" / "state.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["slug"] == "x"
    assert first["to_status"] == "text_ready"
    assert "timestamp" in first
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_state_log.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/state_log.py`**

```python
"""JSONL append-only state transition log."""
from __future__ import annotations

import json
from pathlib import Path

from models import utc_now


class StateLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, slug: str, from_status: str, to_status: str, actor: str = "user", note: str = "") -> None:
        entry = {
            "timestamp": utc_now().isoformat(),
            "slug": slug,
            "from_status": from_status,
            "to_status": to_status,
            "actor": actor,
            "note": note,
        }
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_state_log.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/state_log.py 01-projects/linkedin/tests/test_state_log.py
git commit -m "feat(linkedin): append-only state transition log"
```

---

## Phase E — State files (cooldowns + rejection/approval logs)

### Task E1: AtomUsageTracker + ConnectionUsageTracker

**Files:**
- Create: `01-projects/linkedin/src/usage/atom_usage.py`
- Create: `01-projects/linkedin/src/usage/connection_usage.py`
- Create: `01-projects/linkedin/tests/test_usage_trackers.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_usage_trackers.py
from datetime import datetime, timedelta, timezone
from pathlib import Path

from usage.atom_usage import AtomUsageTracker
from usage.connection_usage import ConnectionUsageTracker


def test_atom_cooldown_primary(project_root: Path):
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json", cooldown_days_primary=30)
    tracker.mark_used("sample-concept", role="primary", post_id="p1")
    assert tracker.is_in_cooldown("sample-concept", role="primary") is True
    assert tracker.is_in_cooldown("sample-concept", role="auxiliary") is False


def test_atom_cooldown_expires(project_root: Path):
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json", cooldown_days_primary=30)
    past = datetime.now(timezone.utc) - timedelta(days=31)
    tracker.mark_used("sample-concept", role="primary", post_id="p1", at=past)
    assert tracker.is_in_cooldown("sample-concept", role="primary") is False


def test_connection_cooldown(project_root: Path):
    tracker = ConnectionUsageTracker(project_root / "state" / "connection-usage.json", cooldown_days=60)
    tracker.mark_used("sample-concept", "another-concept", post_id="p1")
    assert tracker.is_in_cooldown("sample-concept", "another-concept") is True
    # order-independent
    assert tracker.is_in_cooldown("another-concept", "sample-concept") is True
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_usage_trackers.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/usage/atom_usage.py`**

```python
"""Atom cooldown tracking."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


class AtomUsageTracker:
    def __init__(self, path: Path, cooldown_days_primary: int = 30, cooldown_days_auxiliary: int = 7):
        self.path = Path(path)
        self.cooldown_primary = timedelta(days=cooldown_days_primary)
        self.cooldown_aux = timedelta(days=cooldown_days_auxiliary)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}")

    def _load(self) -> dict:
        return json.loads(self.path.read_text())

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def mark_used(self, atom_slug: str, role: str, post_id: str, at: Optional[datetime] = None) -> None:
        data = self._load()
        history = data.setdefault(atom_slug, [])
        history.append({
            "post_id": post_id,
            "role": role,
            "at": (at or datetime.now(timezone.utc)).isoformat(),
        })
        self._save(data)

    def is_in_cooldown(self, atom_slug: str, role: str) -> bool:
        data = self._load()
        history = data.get(atom_slug, [])
        if not history:
            return False
        cooldown = self.cooldown_primary if role == "primary" else self.cooldown_aux
        now = datetime.now(timezone.utc)
        for entry in history:
            if entry["role"] != role:
                continue
            entry_time = datetime.fromisoformat(entry["at"])
            if now - entry_time < cooldown:
                return True
        return False
```

- [ ] **Step 4: Implement `src/usage/connection_usage.py`**

```python
"""Connection edge cooldown tracking."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


def _edge_key(a: str, b: str) -> str:
    return "|".join(sorted([a, b]))


class ConnectionUsageTracker:
    def __init__(self, path: Path, cooldown_days: int = 60):
        self.path = Path(path)
        self.cooldown = timedelta(days=cooldown_days)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}")

    def _load(self) -> dict:
        return json.loads(self.path.read_text())

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def mark_used(self, atom_a: str, atom_b: str, post_id: str, at: Optional[datetime] = None) -> None:
        data = self._load()
        key = _edge_key(atom_a, atom_b)
        history = data.setdefault(key, [])
        history.append({"post_id": post_id, "at": (at or datetime.now(timezone.utc)).isoformat()})
        self._save(data)

    def is_in_cooldown(self, atom_a: str, atom_b: str) -> bool:
        data = self._load()
        key = _edge_key(atom_a, atom_b)
        history = data.get(key, [])
        if not history:
            return False
        now = datetime.now(timezone.utc)
        return any(now - datetime.fromisoformat(e["at"]) < self.cooldown for e in history)
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_usage_trackers.py -v
```

Expected: PASS all three tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/usage/atom_usage.py 01-projects/linkedin/src/usage/connection_usage.py 01-projects/linkedin/tests/test_usage_trackers.py
git commit -m "feat(linkedin): atom + connection cooldown trackers"
```

---

### Task E2: RejectionLog + ApprovalLog

**Files:**
- Create: `01-projects/linkedin/src/usage/rejection_log.py`
- Create: `01-projects/linkedin/src/usage/approval_log.py`
- Create: `01-projects/linkedin/tests/test_decision_logs.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_decision_logs.py
import json
from datetime import datetime, timezone
from pathlib import Path

from usage.approval_log import ApprovalLog
from usage.rejection_log import RejectionLog


def test_rejection_log(project_root: Path):
    log = RejectionLog(project_root / "state" / "rejections.jsonl")
    log.record(
        post_id="p1",
        atoms_used=["a", "b"],
        strategy="two_atom_bridge",
        angle="...",
        draft_text="draft",
        reason="angle too abstract",
        signal="killed_by_user",
    )
    lines = (project_root / "state" / "rejections.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["rejection_signal"] == "killed_by_user"


def test_approval_log_with_delta(project_root: Path):
    log = ApprovalLog(project_root / "state" / "approvals.jsonl")
    log.record(
        post_id="p2",
        atoms_used=["a", "b"],
        strategy="source_spotlight",
        angle="...",
        draft_text="draft body",
        approved_text="draft body. extra.",
        approved_visual_tier=1,
        tier_changed_at_gate1=False,
    )
    entry = json.loads((project_root / "state" / "approvals.jsonl").read_text().strip())
    assert entry["edit_delta"]["magnitude"] in {"minor", "moderate", "major"}
    assert "diff" in entry["edit_delta"]
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_decision_logs.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/usage/rejection_log.py`**

```python
"""Append-only rejection log."""
from __future__ import annotations

import json
from pathlib import Path

from models import utc_now


class RejectionLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        post_id: str,
        atoms_used: list[str],
        strategy: str,
        angle: str,
        draft_text: str,
        reason: str = "",
        signal: str = "killed_by_user",
    ) -> None:
        entry = {
            "post_id": post_id,
            "rejected_at": utc_now().isoformat(),
            "atoms_used": atoms_used,
            "strategy": strategy,
            "angle": angle,
            "draft_text": draft_text,
            "rejection_reason": reason,
            "rejection_signal": signal,
        }
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
```

- [ ] **Step 4: Implement `src/usage/approval_log.py`**

```python
"""Append-only approval log with edit_delta computation."""
from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Optional

from models import utc_now


def _classify_magnitude(diff_ratio: float) -> str:
    if diff_ratio < 0.10:
        return "minor"
    if diff_ratio < 0.40:
        return "moderate"
    return "major"


def compute_edit_delta(draft: str, approved: str) -> dict:
    diff = "\n".join(difflib.unified_diff(
        draft.splitlines(),
        approved.splitlines(),
        lineterm="",
        fromfile="draft",
        tofile="approved",
    ))
    matcher = difflib.SequenceMatcher(None, draft, approved)
    distance = 1.0 - matcher.ratio()
    return {
        "diff": diff,
        "magnitude": _classify_magnitude(distance),
        "ratio": distance,
    }


class ApprovalLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        post_id: str,
        atoms_used: list[str],
        strategy: str,
        angle: str,
        draft_text: str,
        approved_text: str,
        approved_visual_tier: int,
        tier_changed_at_gate1: bool = False,
        posted_at: Optional[str] = None,
    ) -> None:
        entry = {
            "post_id": post_id,
            "approved_at": utc_now().isoformat(),
            "atoms_used": atoms_used,
            "strategy": strategy,
            "angle": angle,
            "draft_text": draft_text,
            "approved_text": approved_text,
            "edit_delta": compute_edit_delta(draft_text, approved_text),
            "approved_visual_tier": approved_visual_tier,
            "tier_changed_at_gate1": tier_changed_at_gate1,
            "posted_at": posted_at,
            "performance": None,
        }
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
```

- [ ] **Step 5: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_decision_logs.py -v
```

Expected: PASS both tests.

- [ ] **Step 6: Commit**

```bash
git add -f 01-projects/linkedin/src/usage/rejection_log.py 01-projects/linkedin/src/usage/approval_log.py 01-projects/linkedin/tests/test_decision_logs.py
git commit -m "feat(linkedin): rejection log + approval log with edit_delta computation"
```

---

## Phase F — Strategy base

### Task F1: Strategy ABC + base utilities

**Files:**
- Create: `01-projects/linkedin/src/strategies/base.py`
- Create: `01-projects/linkedin/tests/test_strategy_base.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_strategy_base.py
from pathlib import Path

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext, eligible_atoms
from usage.atom_usage import AtomUsageTracker


def test_eligible_atoms_filters_cooldown(atom_source: Path, project_root: Path):
    loader = AtomLoader(atom_source)
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json", cooldown_days_primary=30)
    tracker.mark_used("sample-concept", role="primary", post_id="x")
    atoms = loader.load_all()
    eligible = eligible_atoms(atoms, tracker, role="primary")
    slugs = {a.slug for a in eligible}
    assert "sample-concept" not in slugs
    assert "another-concept" in slugs


def test_strategy_context_holds_components(atom_source, project_root):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json")
    ctx = StrategyContext(loader=loader, graph=graph, atom_tracker=tracker)
    assert ctx.loader is loader
    assert ctx.graph is graph
```

- [ ] **Step 2: Run to verify failure**

```bash
cd 01-projects/linkedin && pytest tests/test_strategy_base.py -v
```

Expected: FAIL.

- [ ] **Step 3: Implement `src/strategies/base.py`**

```python
"""Strategy base — interface + shared helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from atom_loader import Atom, AtomLoader
from connection_graph import ConnectionGraph
from models import PostBrief
from usage.atom_usage import AtomUsageTracker
from usage.connection_usage import ConnectionUsageTracker


@dataclass
class StrategyContext:
    loader: AtomLoader
    graph: ConnectionGraph
    atom_tracker: AtomUsageTracker
    connection_tracker: ConnectionUsageTracker | None = None


class Strategy(Protocol):
    name: str
    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief: ...


def eligible_atoms(atoms: Iterable[Atom], tracker: AtomUsageTracker, role: str) -> list[Atom]:
    return [
        a for a in atoms
        if a.type != "connection" and not tracker.is_in_cooldown(a.slug, role=role)
    ]


def domains(atoms: Iterable[Atom]) -> set[str]:
    """Return the set of domain tags across a group of atoms."""
    result: set[str] = set()
    for a in atoms:
        if a.domain:
            result.add(a.domain)
        for tag in a.tags:
            result.add(tag)
    return result
```

- [ ] **Step 4: Run test to verify pass**

```bash
cd 01-projects/linkedin && pytest tests/test_strategy_base.py -v
```

Expected: PASS both tests.

- [ ] **Step 5: Commit**

```bash
git add -f 01-projects/linkedin/src/strategies/base.py 01-projects/linkedin/tests/test_strategy_base.py
git commit -m "feat(linkedin): Strategy protocol + eligibility helpers"
```

---

That completes the scaffolding, models, storage, and strategy-base layers. The next pieces (4 strategy implementations, voice linter, text generator, diagram renderer, CLI wiring, end-to-end tests) follow the same TDD pattern but each is substantial enough that I'd rather not stuff them into one mega-doc.

---

## Plan continuation note

This plan file documents **Phases A–F** in full detail (tasks A1–F1). The remaining phases follow the same pattern. To keep the document reviewable and to honor bite-sized scope, I'm continuing in a companion plan file:

**Companion file:** `01-projects/linkedin/docs/2026-05-24-v1-0-implementation-plan-part2.md` covers Phases G–M:

- **Phase G** — 4 strategy implementations (source_spotlight, two_atom_bridge, cluster_reveal, convergence_finder)
- **Phase H** — Voice linter (rules.yml + hard-fail + soft-warn checks)
- **Phase I** — Text generator (Claude API integration)
- **Phase J** — Tier 1 diagram renderer (graphviz)
- **Phase K** — `linkedin-visual-discipline` skill (SKILL.md + registry)
- **Phase L** — CLI entry points + slash command markdown files
- **Phase M** — End-to-end integration tests

Both parts must be completed for v1.0 to ship. Execute Part 1 first.

---

*End of Part 1.*
