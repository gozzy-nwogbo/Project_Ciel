import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.cluster_reveal import ClusterReveal
from usage.atom_usage import AtomUsageTracker


def _ctx(atom_source, project_root):
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
    )


def test_cluster_reveal_finds_tag_cluster(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ClusterReveal()
    brief = strategy.generate_brief(ctx, {"cluster_anchor": "storytelling"})
    assert brief.strategy == "cluster_reveal"
    assert len(brief.atoms_used) >= 4


def test_cluster_reveal_too_small_fails(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ClusterReveal()
    with pytest.raises(ValueError, match="too small"):
        strategy.generate_brief(ctx, {"cluster_anchor": "nonexistent-tag"})
