"""Coherence-driven selection tests for convergence_finder."""
import os
import shutil
from pathlib import Path

import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.convergence_finder import ConvergenceFinder
from usage.atom_usage import AtomUsageTracker


COHERENT_MAPPING = {
    "Coherent X": [1.0, 0.0, 0.0],
    "Coherent Y": [0.99, 0.14, 0.0],
    "Coherent Z": [0.98, 0.20, 0.0],
    "Decoy Z":    [0.0, 0.0, 1.0],
}


class _MappedEmbedder:
    """Returns the vector mapped for each text by title-prefix substring match."""
    def __init__(self, mapping: dict[str, list[float]]):
        self.mapping = mapping
        self.calls: list[str] = []

    def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        for prefix, vec in self.mapping.items():
            if prefix in text:
                return vec
        raise AssertionError(f"_MappedEmbedder has no mapping for: {text[:80]}")


@pytest.fixture
def coherence_atom_source(tmp_path: Path) -> Path:
    """Copy only the coherence_basic fixture subset to a clean tmp dir."""
    src = Path(__file__).parent / "fixtures" / "atoms" / "coherence_basic"
    dest = tmp_path / "atoms"
    dest.mkdir()
    for f in src.glob("*.md"):
        shutil.copy(f, dest / f.name)
    return dest


@pytest.fixture
def coherence_project_root(tmp_path: Path) -> Path:
    for sub in ("state", "backlog", "logs"):
        (tmp_path / sub).mkdir(exist_ok=True)
    return tmp_path


def _ctx(atom_source, project_root, embedder):
    os.environ["LINKEDIN_PROJECT_ROOT"] = str(project_root)
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
        embedder=embedder,
    )


def test_coherence_picks_highest_min_triple(coherence_atom_source, coherence_project_root):
    """Decoy-Z is orthogonal to the coherent trio. Strategy picks (X, Y, Z) over any triple containing Decoy."""
    embedder = _MappedEmbedder(COHERENT_MAPPING)
    ctx = _ctx(coherence_atom_source, coherence_project_root, embedder)
    strategy = ConvergenceFinder()

    brief = strategy.generate_brief(ctx, {"topic": "feedback"})

    chosen_slugs = sorted([ref.slug for ref in brief.atoms_used])
    assert chosen_slugs == ["coherent-x", "coherent-y", "coherent-z"]
    # Score persisted in strategy_params.
    assert brief.strategy_params["min_sim"] > 0.9


def test_coherence_raises_when_no_triple_clears_threshold(
    coherence_atom_source, coherence_project_root
):
    """Force a high threshold that no triple can clear. Error must carry diagnostic payload."""
    embedder = _MappedEmbedder(COHERENT_MAPPING)
    ctx = _ctx(coherence_atom_source, coherence_project_root, embedder)
    strategy = ConvergenceFinder()

    with pytest.raises(ValueError) as exc_info:
        strategy.generate_brief(ctx, {"topic": "feedback", "min_sim": 0.999})

    msg = str(exc_info.value)
    assert "coherence threshold" in msg
    assert "best min_sim" in msg
    assert "top_3" in msg
    assert "threshold=0.999" in msg


def test_env_var_overrides_default_threshold(
    coherence_atom_source, coherence_project_root, monkeypatch
):
    """LINKEDIN_CONVERGENCE_MIN_SIM env var sets the threshold when no param given."""
    monkeypatch.setenv("LINKEDIN_CONVERGENCE_MIN_SIM", "0.999")
    embedder = _MappedEmbedder(COHERENT_MAPPING)
    ctx = _ctx(coherence_atom_source, coherence_project_root, embedder)
    strategy = ConvergenceFinder()

    with pytest.raises(ValueError, match="threshold=0.999"):
        strategy.generate_brief(ctx, {"topic": "feedback"})


def test_lazy_cache_populates_during_run_and_skips_on_repeat(
    coherence_atom_source, coherence_project_root
):
    """First run embeds every candidate. Second run hits cache: zero new embed calls."""
    embedder = _MappedEmbedder(COHERENT_MAPPING)
    ctx = _ctx(coherence_atom_source, coherence_project_root, embedder)
    strategy = ConvergenceFinder()

    _ = strategy.generate_brief(ctx, {"topic": "feedback"})
    first_call_count = len(embedder.calls)
    assert first_call_count == 4, "expected 4 embeds for 4 atoms on first run"

    # Reset cooldowns so the same atoms are eligible again.
    ctx.atom_tracker._state = {"atoms": {}}

    _ = strategy.generate_brief(ctx, {"topic": "feedback"})
    assert len(embedder.calls) == first_call_count, "cache hit should not add embed calls"
