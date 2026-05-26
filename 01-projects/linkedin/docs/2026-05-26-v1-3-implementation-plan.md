# LinkedIn Engine v1.3 Implementation Plan: Atom-Coherence Scoring

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace `convergence_finder`'s tag-overlap atom selection with embedding-based coherence scoring. The three atoms returned by the strategy will have minimum pairwise cosine similarity ≥ 0.35 (configurable). When no triple clears the threshold, the strategy raises with a diagnostic payload (best min-sim found + top 3 candidate slug triples) so the user can recalibrate or pick a different topic.

**Architecture:** A new `src/embeddings/` module owns the OpenAI provider, the JSON-on-disk cache, and the coherence math. `StrategyContext` gains an optional `embedder: Embedder | None` field. `convergence_finder.generate_brief` is rewritten to (1) filter atoms by topic + cooldowns + ≥3-distinct-domain check (unchanged), (2) lazy-populate the cache for any newly-touched atoms, (3) enumerate every `(domain-triple × atom-per-domain)` combination, (4) score each by min pairwise cosine sim, (5) pick the highest-min triple, (6) raise with diagnostic payload if no triple clears threshold. The graph-connectivity heuristic is dropped entirely.

**Tech stack:** Python 3.11+ (existing), `openai>=1.40` (new dependency), JSON cache file at `01-projects/linkedin/.cache/atom-embeddings.json`, pytest (existing). No DB, no batching, no async.

**Spec reference:** `decision-log.md` entry "2026-05-26 — v1.3 design: atom-coherence scoring for convergence_finder"

**Working tree:** Create branch `feat/linkedin-engine-v1.3` from current `main` (tip after PR #3 merge) before Task 1.

---

## File map

**Create:**

- `src/embeddings/__init__.py`. Module init.
- `src/embeddings/provider.py`. `OpenAIEmbedder` class. Wraps `openai.embeddings.create(model="text-embedding-3-small", input=text)`. Synchronous, no batching (corpus is small).
- `src/embeddings/cache.py`. `EmbeddingCache` class. Loads/saves JSON at the cache path. Hashes body text via SHA-256. Method `get_or_embed(slug, text, embedder) -> list[float]` returns cached vector if hash matches, else embeds + writes + returns.
- `src/embeddings/coherence.py`. Pure functions: `cosine_similarity(a, b) -> float`, `min_pairwise_similarity(vecs) -> float`, `rank_triples(domain_to_atoms, embeddings) -> list[tuple[float, tuple[Atom, Atom, Atom]]]` (returns descending by min-sim, deterministic tiebreak by sorted slug tuple).
- `tests/test_embedding_cache.py`. Cache hit on hash match, cache miss on hash mismatch, file persistence round-trip, atomic write (write to temp then rename).
- `tests/test_coherence.py`. Cosine math on hand-computed vectors, min-pairwise edge cases (identical vectors → 1.0, orthogonal → 0.0), triple ranking order, deterministic tiebreak.
- `tests/test_convergence_finder_coherence.py`. New tests with a `FakeEmbedder` injecting controlled vectors. Covers: happy path picks highest-min triple, threshold-fail path raises with payload, env-var override, lazy cache populate during a run.
- `.gitignore` (project-local at `01-projects/linkedin/.gitignore`). Add `.cache/` line.

**Modify:**

- `requirements.txt`. Add `openai>=1.40`.
- `src/strategies/base.py`. Define `Embedder` Protocol with `embed(text: str) -> list[float]`. Add `embedder: Embedder | None = None` to `StrategyContext`.
- `src/strategies/convergence_finder.py`. Rewrite `generate_brief`. Drop graph-connectivity per-domain ranking. Use injected embedder (lazy-default to `OpenAIEmbedder` if `ctx.embedder is None`). Enumerate full candidate space, rank by min-sim, raise diagnostic error when below threshold. Log min-sim outcome to `logs/state.jsonl` (use whatever logging facility the rest of the engine already uses; check `src/storage/` or `src/cli/draft_post.py` for the pattern).
- `src/cli/draft_post.py`. Construct an `OpenAIEmbedder` and pass it into `StrategyContext` (or lazy-construct on demand; whichever matches the existing context-construction style there).
- `tests/test_convergence_finder.py`. Update existing tests to inject a fake embedder. The "needs ≥3 domains" test stays. The "picks first 3 by domain" assertion gets reframed as "picks highest-min triple given this embedder."
- `01-projects/linkedin/CLAUDE.md`. Add a note under Conventions: `convergence_finder` requires `OPENAI_API_KEY` and writes to `.cache/atom-embeddings.json`. Env var `LINKEDIN_CONVERGENCE_MIN_SIM` overrides the 0.35 default.

**Leave alone:**

- `src/strategies/two_atom_bridge.py`, `src/strategies/source_spotlight.py`. Coherence scoring is convergence-only in v1.3.
- All renderers, voice linter, text generator, tldr filler.
- All other strategy tests.
- `src/connection_graph.py`. Convergence stops calling `ctx.graph.edges_for(...)` but the graph stays in `StrategyContext` for other strategies.

---

## Task 1: Branch + green baseline

**Files:** None. Branch creation only.

- [ ] **Step 1: Create the branch from current main.**

```bash
cd /Users/gozzynwogbo/second-brain
git checkout main && git pull --ff-only && git checkout -b feat/linkedin-engine-v1.3
```

Expected: branch `feat/linkedin-engine-v1.3` created at the current `main` tip (post-PR-#3, post-v1.2.2 merge).

- [ ] **Step 2: Confirm 114/114 baseline.**

```bash
cd 01-projects/linkedin
PYTHONPATH=src pytest tests/ -v 2>&1 | tail -10
```

Expected: `114 passed`.

- [ ] **Step 3: No commit. Branch is the only artifact.**

---

## Task 2: Dependencies + gitignore

**Files:**
- Modify: `01-projects/linkedin/requirements.txt`
- Create: `01-projects/linkedin/.gitignore`

- [ ] **Step 1: Add `openai>=1.40` to requirements.**

Edit `requirements.txt`. After the last existing line, add:

```
openai>=1.40
```

- [ ] **Step 2: Install the new dependency.**

```bash
cd 01-projects/linkedin
pip install openai>=1.40
```

Expected: `Successfully installed openai-1.X.X` or `Requirement already satisfied`. If the user already has it via open-brain or another project, this is a no-op.

- [ ] **Step 3: Add `.cache/` to project gitignore.**

Check whether `01-projects/linkedin/.gitignore` exists. If yes, append `.cache/` on a new line. If no, create the file with:

```
.cache/
```

- [ ] **Step 4: Commit.**

```bash
git add requirements.txt .gitignore
git commit -m "feat(linkedin): v1.3 add openai dep + gitignore embeddings cache"
```

---

## Task 3: Coherence math (pure functions, test-first)

**Files:**
- Create: `src/embeddings/__init__.py` (empty)
- Create: `src/embeddings/coherence.py`
- Create: `tests/test_coherence.py`

- [ ] **Step 1: Write failing tests in `tests/test_coherence.py`.**

```python
"""Pure-function tests for the coherence module."""
import math

import pytest


def test_cosine_similarity_identical_vectors():
    from embeddings.coherence import cosine_similarity
    v = [0.6, 0.8]  # unit vector
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    from embeddings.coherence import cosine_similarity
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_opposite():
    from embeddings.coherence import cosine_similarity
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_min_pairwise_similarity_three_vectors():
    from embeddings.coherence import min_pairwise_similarity
    # Two close vectors and one orthogonal: min pairwise = 0
    vecs = [[1.0, 0.0], [0.99, 0.14], [0.0, 1.0]]
    assert min_pairwise_similarity(vecs) == pytest.approx(0.0, abs=0.15)


def test_min_pairwise_similarity_all_identical():
    from embeddings.coherence import min_pairwise_similarity
    v = [0.6, 0.8]
    assert min_pairwise_similarity([v, v, v]) == pytest.approx(1.0)


def test_rank_triples_picks_highest_min():
    """Given two candidate triples, the higher-min triple ranks first."""
    from embeddings.coherence import rank_triples
    from atom_loader import Atom

    a = Atom(slug="a", title="A", type="concept", source_date="", body="", domain="x")
    b = Atom(slug="b", title="B", type="concept", source_date="", body="", domain="y")
    c = Atom(slug="c", title="C", type="concept", source_date="", body="", domain="z")
    d = Atom(slug="d", title="D", type="concept", source_date="", body="", domain="z")

    # Embeddings: a, b, c are tightly aligned. d is orthogonal to a.
    embeddings = {
        "a": [1.0, 0.0],
        "b": [0.99, 0.14],
        "c": [0.98, 0.20],
        "d": [0.0, 1.0],
    }
    domain_to_atoms = {"x": [a], "y": [b], "z": [c, d]}

    ranked = rank_triples(domain_to_atoms, embeddings)
    top_score, top_triple = ranked[0]
    top_slugs = sorted([atom.slug for atom in top_triple])
    assert top_slugs == ["a", "b", "c"], f"expected (a,b,c) triple to win, got {top_slugs}"
    assert top_score > 0.9


def test_rank_triples_deterministic_tiebreak():
    """When two triples score equally, sort key is the slug tuple."""
    from embeddings.coherence import rank_triples
    from atom_loader import Atom

    # All atoms have identical embeddings → all triples tie at 1.0.
    a1 = Atom(slug="a1", title="", type="concept", source_date="", body="", domain="x")
    a2 = Atom(slug="a2", title="", type="concept", source_date="", body="", domain="x")
    b = Atom(slug="b", title="", type="concept", source_date="", body="", domain="y")
    c = Atom(slug="c", title="", type="concept", source_date="", body="", domain="z")

    v = [1.0, 0.0]
    embeddings = {"a1": v, "a2": v, "b": v, "c": v}
    domain_to_atoms = {"x": [a1, a2], "y": [b], "z": [c]}

    ranked = rank_triples(domain_to_atoms, embeddings)
    # Both triples tie; deterministic order means (a1,b,c) comes before (a2,b,c).
    first_slugs = sorted([atom.slug for atom in ranked[0][1]])
    second_slugs = sorted([atom.slug for atom in ranked[1][1]])
    assert first_slugs == ["a1", "b", "c"]
    assert second_slugs == ["a2", "b", "c"]
```

- [ ] **Step 2: Run the failing tests.**

```bash
PYTHONPATH=src pytest tests/test_coherence.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'embeddings'`.

- [ ] **Step 3: Implement `src/embeddings/__init__.py`.**

Empty file (Python package marker).

- [ ] **Step 4: Implement `src/embeddings/coherence.py`.**

```python
"""Coherence math: cosine similarity, min-pairwise, triple ranking."""
from __future__ import annotations

import itertools
import math
from typing import Sequence

from atom_loader import Atom


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Standard cosine similarity. Returns 0.0 if either vector is zero-norm."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def min_pairwise_similarity(vecs: Sequence[Sequence[float]]) -> float:
    """Minimum cosine similarity across all unique pairs in vecs."""
    pairs = itertools.combinations(vecs, 2)
    sims = [cosine_similarity(a, b) for a, b in pairs]
    return min(sims) if sims else 0.0


def rank_triples(
    domain_to_atoms: dict[str, list[Atom]],
    embeddings: dict[str, list[float]],
) -> list[tuple[float, tuple[Atom, Atom, Atom]]]:
    """Enumerate every (domain-triple x atom-per-domain) combination.

    Returns a list of (min_pairwise_similarity, atom_triple) sorted
    descending by score with deterministic slug-tuple tiebreak.
    """
    domains = sorted(domain_to_atoms.keys())
    results: list[tuple[float, tuple[Atom, Atom, Atom]]] = []

    for d_triple in itertools.combinations(domains, 3):
        atom_lists = [domain_to_atoms[d] for d in d_triple]
        for atom_triple in itertools.product(*atom_lists):
            vecs = [embeddings[a.slug] for a in atom_triple]
            score = min_pairwise_similarity(vecs)
            results.append((score, atom_triple))

    # Sort: high score first; tiebreak by sorted slug tuple ascending.
    results.sort(key=lambda r: (-r[0], tuple(sorted(a.slug for a in r[1]))))
    return results
```

- [ ] **Step 5: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_coherence.py -v
```

Expected: all 7 tests pass.

- [ ] **Step 6: Full suite stays green.**

```bash
PYTHONPATH=src pytest tests/ 2>&1 | tail -5
```

Expected: `121 passed` (114 + 7).

- [ ] **Step 7: Commit.**

```bash
git add src/embeddings/ tests/test_coherence.py
git commit -m "feat(linkedin): v1.3 add embeddings.coherence pure functions"
```

---

## Task 4: Cache layer (test-first)

**Files:**
- Create: `src/embeddings/cache.py`
- Create: `tests/test_embedding_cache.py`

- [ ] **Step 1: Write failing tests in `tests/test_embedding_cache.py`.**

```python
"""Tests for the embedding cache layer."""
import json
from pathlib import Path

import pytest


class FakeEmbedder:
    """Returns a stable vector based on the text; counts calls."""
    def __init__(self):
        self.calls = 0

    def embed(self, text: str) -> list[float]:
        self.calls += 1
        # Length-based vector for stability in tests.
        return [float(len(text)), 0.0, 1.0]


def test_cache_miss_calls_embedder_and_persists(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()

    vec = cache.get_or_embed("slug1", "hello world", embedder)

    assert vec == [11.0, 0.0, 1.0]
    assert embedder.calls == 1
    # Persisted to disk.
    saved = json.loads(cache_path.read_text())
    assert "slug1" in saved
    assert "body_hash" in saved["slug1"]
    assert saved["slug1"]["embedding"] == [11.0, 0.0, 1.0]


def test_cache_hit_does_not_call_embedder(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()

    _ = cache.get_or_embed("slug1", "hello world", embedder)
    _ = cache.get_or_embed("slug1", "hello world", embedder)

    assert embedder.calls == 1, "second call should hit cache"


def test_cache_hash_mismatch_re_embeds(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()

    _ = cache.get_or_embed("slug1", "hello", embedder)  # vec = [5.0, ...]
    vec2 = cache.get_or_embed("slug1", "hello world", embedder)  # body changed

    assert embedder.calls == 2
    assert vec2 == [11.0, 0.0, 1.0]


def test_cache_survives_round_trip(tmp_path: Path):
    """A new cache instance reads the persisted JSON on init."""
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()
    _ = cache.get_or_embed("slug1", "hello", embedder)

    cache2 = EmbeddingCache(cache_path)
    vec = cache2.get_or_embed("slug1", "hello", FakeEmbedder())  # fresh embedder

    assert vec == [5.0, 0.0, 1.0]


def test_cache_creates_parent_directory(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    nested = tmp_path / "deep" / "nested" / "embeddings.json"
    cache = EmbeddingCache(nested)
    _ = cache.get_or_embed("slug1", "x", FakeEmbedder())
    assert nested.exists()
```

- [ ] **Step 2: Run failing tests.**

```bash
PYTHONPATH=src pytest tests/test_embedding_cache.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'embeddings.cache'`.

- [ ] **Step 3: Implement `src/embeddings/cache.py`.**

```python
"""Persistent embedding cache with hash-based invalidation."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Protocol


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """JSON-on-disk cache: {slug: {body_hash, embedding}}."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._data: dict[str, dict] = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def get_or_embed(self, slug: str, text: str, embedder: Embedder) -> list[float]:
        h = _hash(text)
        entry = self._data.get(slug)
        if entry and entry.get("body_hash") == h:
            return list(entry["embedding"])

        vec = embedder.embed(text)
        self._data[slug] = {"body_hash": h, "embedding": vec}
        self._save()
        return vec

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic write: tempfile in same directory, then rename.
        fd, tmp_path = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(self._data, f)
            os.replace(tmp_path, self.path)
        except Exception:
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()
            raise
```

- [ ] **Step 4: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_embedding_cache.py -v
```

Expected: all 5 tests pass.

- [ ] **Step 5: Commit.**

```bash
git add src/embeddings/cache.py tests/test_embedding_cache.py
git commit -m "feat(linkedin): v1.3 add EmbeddingCache with hash-based invalidation"
```

---

## Task 5: OpenAI provider (mocked tests)

**Files:**
- Create: `src/embeddings/provider.py`
- Create: `tests/test_embedding_provider.py`

- [ ] **Step 1: Write failing tests with mocked `openai.OpenAI` client.**

```python
"""Tests for the OpenAI embedder. Mocks the openai client to avoid hitting the API."""
from unittest.mock import MagicMock, patch


def test_openai_embedder_calls_text_embedding_3_small():
    from embeddings.provider import OpenAIEmbedder

    fake_response = MagicMock()
    fake_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    fake_client = MagicMock()
    fake_client.embeddings.create.return_value = fake_response

    with patch("embeddings.provider.OpenAI", return_value=fake_client):
        embedder = OpenAIEmbedder(api_key="sk-test")
        vec = embedder.embed("hello world")

    assert vec == [0.1, 0.2, 0.3]
    fake_client.embeddings.create.assert_called_once()
    call_kwargs = fake_client.embeddings.create.call_args.kwargs
    assert call_kwargs["model"] == "text-embedding-3-small"
    assert call_kwargs["input"] == "hello world"


def test_openai_embedder_uses_env_var_when_no_key_passed(monkeypatch):
    from embeddings.provider import OpenAIEmbedder

    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    with patch("embeddings.provider.OpenAI") as MockClient:
        _ = OpenAIEmbedder()
    # The OpenAI client itself reads OPENAI_API_KEY when api_key is None,
    # so we only assert that we don't pass an explicit empty/None.
    init_kwargs = MockClient.call_args.kwargs
    assert init_kwargs.get("api_key") in ("sk-from-env", None)


def test_openai_embedder_raises_if_no_key_anywhere(monkeypatch):
    from embeddings.provider import OpenAIEmbedder
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    import pytest
    with pytest.raises((ValueError, RuntimeError)):
        _ = OpenAIEmbedder()
```

- [ ] **Step 2: Run failing tests.**

Expected: FAIL with `ModuleNotFoundError: No module named 'embeddings.provider'`.

- [ ] **Step 3: Implement `src/embeddings/provider.py`.**

```python
"""OpenAI embedding provider. Wraps text-embedding-3-small."""
from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI


MODEL = "text-embedding-3-small"


class OpenAIEmbedder:
    """Synchronous OpenAI embedder. One text in, one vector out."""

    def __init__(self, api_key: Optional[str] = None):
        resolved = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved:
            raise ValueError(
                "OpenAIEmbedder requires OPENAI_API_KEY in env or api_key kwarg."
            )
        self._client = OpenAI(api_key=resolved)

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=MODEL, input=text)
        return list(response.data[0].embedding)
```

- [ ] **Step 4: Run the tests.**

```bash
PYTHONPATH=src pytest tests/test_embedding_provider.py -v
```

Expected: all 3 tests pass.

- [ ] **Step 5: Commit.**

```bash
git add src/embeddings/provider.py tests/test_embedding_provider.py
git commit -m "feat(linkedin): v1.3 add OpenAIEmbedder for text-embedding-3-small"
```

---

## Task 6: Rewrite convergence_finder

**Files:**
- Modify: `src/strategies/base.py` (add Embedder Protocol + StrategyContext.embedder)
- Modify: `src/strategies/convergence_finder.py` (full rewrite of generate_brief)
- Create: `tests/test_convergence_finder_coherence.py`
- Modify: `tests/test_convergence_finder.py` (adapt existing tests to new logic)

- [ ] **Step 1: Extend `src/strategies/base.py` with `Embedder` Protocol + context field.**

Read the current file. Add the Embedder Protocol below the existing imports:

```python
from typing import Iterable, Protocol


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...
```

Add the optional field to `StrategyContext`:

```python
@dataclass
class StrategyContext:
    loader: AtomLoader
    graph: ConnectionGraph
    atom_tracker: AtomUsageTracker
    connection_tracker: ConnectionUsageTracker | None = None
    embedder: Embedder | None = None
```

- [ ] **Step 2: Write failing tests in `tests/test_convergence_finder_coherence.py`.**

```python
"""Coherence-driven selection tests for convergence_finder."""
from pathlib import Path

import pytest


class FakeEmbedder:
    """Returns the vector mapped for each text, identified by substring match.

    Tests pre-register text-prefix -> vector mappings.
    """
    def __init__(self, mapping: dict[str, list[float]]):
        self.mapping = mapping
        self.calls: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        for prefix, vec in self.mapping.items():
            if prefix in text:
                return vec
        raise AssertionError(f"FakeEmbedder has no mapping for: {text[:80]}")


def _make_ctx(tmp_path: Path, atoms_dir_name: str, embedder):
    """Build a StrategyContext pointing at a tmp atoms directory."""
    import os
    from atom_loader import AtomLoader
    from connection_graph import ConnectionGraph
    from strategies.base import StrategyContext
    from usage.atom_usage import AtomUsageTracker

    atoms_dir = Path(__file__).parent / "fixtures" / "atoms" / atoms_dir_name
    loader = AtomLoader(atoms_dir)
    graph = ConnectionGraph(loader.load_all())
    tracker = AtomUsageTracker(state_path=tmp_path / "atom-usage.json")
    # Point cache at tmp so we don't pollute real .cache/.
    os.environ["LINKEDIN_PROJECT_ROOT"] = str(tmp_path)
    return StrategyContext(loader=loader, graph=graph, atom_tracker=tracker, embedder=embedder)


def test_coherence_picks_highest_min_triple(tmp_path, monkeypatch):
    """Given a topic where one triple has clearly higher min-sim, pick it."""
    # NOTE: this test depends on a fixtures/atoms/coherence_basic/ tree
    # to be added in step 5. Three coherent atoms (x/y/z domains) + one
    # decoy atom in domain z that embeds orthogonally to the others.
    pytest.skip("requires fixtures/atoms/coherence_basic/ (added in step 5)")


def test_coherence_raises_when_no_triple_clears_threshold(tmp_path, monkeypatch):
    """Diagnostic payload includes best min-sim, threshold, top 3 slug triples."""
    pytest.skip("requires fixtures/atoms/coherence_basic/ (added in step 5)")


def test_env_var_overrides_default_threshold(tmp_path, monkeypatch):
    pytest.skip("requires fixtures/atoms/coherence_basic/ (added in step 5)")


def test_lazy_cache_populates_during_run(tmp_path, monkeypatch):
    """First convergence run embeds every candidate; second run hits cache."""
    pytest.skip("requires fixtures/atoms/coherence_basic/ (added in step 5)")
```

(The skips become unskips after fixtures land in step 5. The plan tests the skeleton + import paths in step 3.)

- [ ] **Step 3: Confirm the skipped tests collect cleanly.**

```bash
PYTHONPATH=src pytest tests/test_convergence_finder_coherence.py -v
```

Expected: 4 SKIPPED, no collection errors.

- [ ] **Step 4: Rewrite `src/strategies/convergence_finder.py`.**

Replace the whole file with:

```python
"""convergence_finder — pick 3 atoms from 3 domains with coherent embeddings."""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from embeddings.cache import EmbeddingCache
from embeddings.coherence import rank_triples
from embeddings.provider import OpenAIEmbedder
from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import Embedder, StrategyContext, eligible_atoms


DEFAULT_MIN_SIM = 0.35


def _resolve_threshold(params: dict) -> float:
    if "min_sim" in params:
        return float(params["min_sim"])
    env_val = os.environ.get("LINKEDIN_CONVERGENCE_MIN_SIM")
    if env_val:
        return float(env_val)
    return DEFAULT_MIN_SIM


def _resolve_cache_path() -> Path:
    root = os.environ.get("LINKEDIN_PROJECT_ROOT", ".")
    return Path(root) / ".cache" / "atom-embeddings.json"


def _log_min_sim(slug: str, topic: str, min_sim: float, threshold: float) -> None:
    """Append a one-line log entry to logs/state.jsonl. Best-effort."""
    root = os.environ.get("LINKEDIN_PROJECT_ROOT", ".")
    log_path = Path(root) / "logs" / "state.jsonl"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "event": "convergence_coherence",
            "topic": topic,
            "slug": slug,
            "min_sim": round(min_sim, 4),
            "threshold": threshold,
        }
        with log_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


class ConvergenceFinder:
    name = "convergence_finder"
    MIN_DOMAINS = 3

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        topic = params.get("topic")
        if not topic:
            raise ValueError("convergence_finder requires 'topic' param")

        # 1. Topic filter (unchanged).
        all_atoms = ctx.loader.load_all()
        topic_touchers = [
            a for a in all_atoms
            if a.type != "connection"
            and (topic in a.tags or topic in (a.title or "").lower() or topic in (a.body or "").lower())
        ]
        topic_touchers = eligible_atoms(topic_touchers, ctx.atom_tracker, role="primary")

        # 2. Group by domain.
        domain_to_atoms: dict[str, list] = {}
        for a in topic_touchers:
            if a.domain:
                domain_to_atoms.setdefault(a.domain, []).append(a)

        if len(domain_to_atoms) < self.MIN_DOMAINS:
            raise ValueError(
                f"Atom corpus may be too narrow for '{topic}': "
                f"found {len(domain_to_atoms)} domain(s), need >= {self.MIN_DOMAINS}"
            )

        # 3. Embed every candidate (lazy via cache).
        embedder: Embedder = ctx.embedder or OpenAIEmbedder()
        cache = EmbeddingCache(_resolve_cache_path())
        embeddings: dict[str, list[float]] = {}
        for atoms in domain_to_atoms.values():
            for atom in atoms:
                text = f"{atom.title}\n\n{atom.body}"
                embeddings[atom.slug] = cache.get_or_embed(atom.slug, text, embedder)

        # 4. Rank all (domain-triple x atom-per-domain) candidates.
        ranked = rank_triples(domain_to_atoms, embeddings)
        if not ranked:
            raise ValueError(
                f"No candidate triples for topic '{topic}'."
            )

        threshold = _resolve_threshold(params)
        best_score, best_triple = ranked[0]

        if best_score < threshold:
            top_3 = [
                {"slugs": sorted([a.slug for a in triple]), "min_sim": round(score, 4)}
                for score, triple in ranked[:3]
            ]
            raise ValueError(
                f"No triple meets coherence threshold for '{topic}': "
                f"best min_sim={best_score:.4f}, threshold={threshold}. "
                f"top_3={top_3}"
            )

        chosen = list(best_triple)
        domains = [a.domain for a in chosen]
        angle = (
            f"{topic.capitalize()} shows up in {', '.join(domains[:-1])}, "
            f"and {domains[-1]}. {len(chosen)} solutions to the same problem."
        )

        # Log for empirical calibration.
        for atom in chosen:
            _log_min_sim(atom.slug, topic, best_score, threshold)

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-convergence-{topic.replace(' ', '-')}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"topic": topic, "domains": domains, "min_sim": round(best_score, 4)},
            atoms_used=[AtomRef(slug=a.slug, role="primary") for a in chosen],
            angle=angle,
            visual_tier="1_diagram",
            aspect_ratio="4:5",
            panel_label=f"CONVERGES ON · {topic.upper()}",
            status=Status.DRAFTING,
            topic_tags=[topic],
        )
```

- [ ] **Step 5: Add fixtures for the coherence tests.**

Create `tests/fixtures/atoms/coherence_basic/` with four atoms:

- `coherent-x.md`:

```markdown
---
title: Coherent X
type: concept
source_date: 2026-05-26
tags: [feedback]
domain: psychology
origin: test-fixture
---

A coherent concept about feedback in psychology.
```

- `coherent-y.md`:

```markdown
---
title: Coherent Y
type: concept
source_date: 2026-05-26
tags: [feedback]
domain: engineering
origin: test-fixture
---

A coherent concept about feedback in engineering.
```

- `coherent-z.md`:

```markdown
---
title: Coherent Z
type: concept
source_date: 2026-05-26
tags: [feedback]
domain: design
origin: test-fixture
---

A coherent concept about feedback in design.
```

- `decoy-z.md`:

```markdown
---
title: Decoy Z
type: concept
source_date: 2026-05-26
tags: [feedback]
domain: design
origin: test-fixture
---

An incoherent decoy in the design domain.
```

- [ ] **Step 6: Un-skip the tests and implement them.**

Replace the four `pytest.skip(...)` lines in `tests/test_convergence_finder_coherence.py` with real test bodies. The `FakeEmbedder` mapping should assign tight vectors to coherent-x/y/z and an orthogonal vector to decoy-z. For the threshold-fail test, set all three coherent vectors farther apart so no triple clears 0.5 with `min_sim=0.5` override.

Suggested embedder mappings (in test code):

```python
COHERENT_MAPPING = {
    "Coherent X": [1.0, 0.0, 0.0],
    "Coherent Y": [0.99, 0.14, 0.0],
    "Coherent Z": [0.98, 0.20, 0.0],
    "Decoy Z":    [0.0, 0.0, 1.0],
}
```

Verify: highest-min triple picks {Coherent X, Coherent Y, Coherent Z}, decoy is rejected, min-sim ~0.95.

For threshold-fail: pass `min_sim=0.99` via params; assert `ValueError` with `top_3` and `best min_sim` in message.

For env-var override: monkeypatch `LINKEDIN_CONVERGENCE_MIN_SIM=0.5` and confirm the strategy reads it.

For lazy cache: assert `len(embedder.calls) == 4` on first run, then construct a new strategy invocation with the same atoms and assert `embedder.calls == 4` still (cache hit, no new embed calls).

- [ ] **Step 7: Run the coherence-finder tests.**

```bash
PYTHONPATH=src pytest tests/test_convergence_finder_coherence.py -v
```

Expected: 4 PASS.

- [ ] **Step 8: Update `tests/test_convergence_finder.py`.**

Read the existing file. Existing tests need a `FakeEmbedder` injected via `StrategyContext`. Any test asserting "first 3 domains" or "most-connected per domain" needs reframing: the new contract is "highest min-pairwise cosine triple given this embedder."

Keep:
- "needs >= 3 domains" → still passes, raises before embedding.

Replace:
- "picks first 3 by domain" → assert specific triple is chosen given fake-embedder mappings.
- "picks most-connected per domain" → delete or replace with coherence-based equivalent.

- [ ] **Step 9: Run the whole convergence test set.**

```bash
PYTHONPATH=src pytest tests/test_convergence_finder.py tests/test_convergence_finder_coherence.py -v
```

Expected: all green.

- [ ] **Step 10: Run the full suite.**

```bash
PYTHONPATH=src pytest tests/ 2>&1 | tail -10
```

Expected: ~125–129 passed (depending on how many tests were adapted vs added).

- [ ] **Step 11: Commit.**

```bash
git add src/strategies/base.py src/strategies/convergence_finder.py \
        tests/fixtures/atoms/coherence_basic/ \
        tests/test_convergence_finder.py tests/test_convergence_finder_coherence.py
git commit -m "feat(linkedin): v1.3 rewrite convergence_finder to coherence-based selection"
```

---

## Task 7: Wire CLI + docs

**Files:**
- Modify: `src/cli/draft_post.py`
- Modify: `01-projects/linkedin/CLAUDE.md`

- [ ] **Step 1: Wire `OpenAIEmbedder` into the CLI's StrategyContext construction.**

Read the existing context-construction in `src/cli/draft_post.py`. Add the embedder field. Lazy construction is fine: only build it when needed.

Pattern:

```python
from embeddings.provider import OpenAIEmbedder
# ...
embedder = None
if strategy == "convergence_finder":
    embedder = OpenAIEmbedder()  # reads OPENAI_API_KEY from env
ctx = StrategyContext(..., embedder=embedder)
```

- [ ] **Step 2: Update `01-projects/linkedin/CLAUDE.md` under Conventions.**

Add a bullet after the existing voice-prompt convention:

```markdown
- `convergence_finder` (v1.3+) selects atom triples by semantic coherence using OpenAI `text-embedding-3-small`. Requires `OPENAI_API_KEY` in env. Embeddings cached at `.cache/atom-embeddings.json` (gitignored). Default coherence threshold is 0.35 min pairwise cosine; override via `LINKEDIN_CONVERGENCE_MIN_SIM` env var or `--min-sim` CLI param. If no triple clears the threshold, the strategy raises with diagnostic payload (best min-sim, top 3 candidate slug triples).
```

- [ ] **Step 3: Commit.**

```bash
git add src/cli/draft_post.py 01-projects/linkedin/CLAUDE.md
git commit -m "feat(linkedin): v1.3 wire OpenAIEmbedder into CLI + document conventions"
```

---

## Task 8: Smoke test (user-run)

This task is run by the user. The orchestrator produces the commands; the user executes them and reports results.

**Prerequisites:**
- `OPENAI_API_KEY` exists in `.env` (already present per CLAUDE.md §2).
- `.cache/atom-embeddings.json` does NOT exist yet (this run will populate it).

**Re-run the topic that failed in v1.2.2 ('feedback'):**

```bash
cd /Users/gozzynwogbo/second-brain
./01-projects/linkedin/bin/draft-post --strategy=convergence_finder --topic=feedback
```

**Expected behavior, three outcomes:**

1. **Cleaner triple than v1.2.2.** The strategy picks a different (more semantically coherent) trio than `shallowing-hypothesis + npd-for-ai + door-shut-door-open`. Min-sim logged in `logs/state.jsonl` should be > 0.35.

2. **Same triple but logged.** If the v1.2.2 trio actually clears 0.35, that recalibrates expectations (threshold too liberal). Log entry tells us by how much.

3. **Threshold error.** If no triple clears 0.35, the diagnostic payload tells the user (a) what was the best score, (b) which 3 candidate triples were closest. User decides: lower threshold via env var, or accept that 'feedback' is too diffuse for convergence.

**After smoke, append to `decision-log.md`:**

```markdown
## 2026-05-26 — v1.3 smoke result

Topic: feedback. Atoms picked: <slugs>. Min-sim: <score>. Threshold: 0.35.
Visual: <clean | strained>. Text: <user-feedback>.
Calibration note: <threshold-too-liberal | threshold-correct | threshold-too-strict>.
```

---

## Task 9: PR + merge

- [ ] **Step 1: Push branch and open PR.**

```bash
git push -u origin feat/linkedin-engine-v1.3
gh pr create --title "feat(linkedin): v1.3 atom-coherence scoring for convergence_finder" \
  --body "$(cat <<'EOF'
## Summary

- Replaces tag-overlap atom selection with embedding-based coherence scoring in `convergence_finder`.
- Adds `src/embeddings/` module: OpenAI provider, JSON cache with hash invalidation, coherence math.
- Drops the graph-connectivity heuristic; enumerates all (domain-triple x atom-per-domain) candidates and picks highest min-pairwise cosine similarity.
- Threshold 0.35 default; configurable via `LINKEDIN_CONVERGENCE_MIN_SIM`. Hard error with diagnostic payload when no triple clears.

## Test plan
- [ ] All ~125 tests pass (114 baseline + ~11 new).
- [ ] Smoke run on topic 'feedback' produces a cleaner trio than v1.2.2 OR a threshold error with diagnostic payload.
- [ ] `.cache/atom-embeddings.json` populated after smoke; gitignored.

EOF
)"
```

- [ ] **Step 2: Merge after user review.**

```bash
gh pr merge <PR#> --merge --delete-branch
```

---

## Risk + reversibility notes

- **Reversible if it ships and disappoints.** All changes are scoped to `convergence_finder` + new `embeddings/` module. Reverting the strategy file restores tag-overlap selection. The cache file can be deleted without consequence (will rebuild on next run).
- **External cost.** First convergence run after merge embeds ~all atoms touching the topic (lazy, per-topic). Whole-vault embed only happens if the user runs many topics. At $0.02 per 1M tokens × ~200 tokens per atom × ~500 atoms = ~$0.002 max. Effectively free.
- **Failure mode if `OPENAI_API_KEY` missing.** `OpenAIEmbedder.__init__` raises `ValueError` with clear message. The CLI surfaces this. Caller fixes env and retries.
- **Cache corruption.** If `.cache/atom-embeddings.json` becomes malformed, `EmbeddingCache.__init__` resets to empty dict and the next run rebuilds. No data loss (cache is derived).
- **Threshold over-tuning risk.** If threshold gets set too high and rejects every triple, the diagnostic payload gives the user the best-found score so they can lower it deliberately. The env var makes this a one-line override during smoke iteration.
