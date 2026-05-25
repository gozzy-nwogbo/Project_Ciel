import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.convergence_finder import ConvergenceFinder
from usage.atom_usage import AtomUsageTracker


def _ctx(atom_source, project_root):
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
    )


def test_finds_three_domains(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.strategy == "convergence_finder"
    domains = {ctx.loader.load_one(ref.slug).domain for ref in brief.atoms_used}
    assert len(domains) >= 3


def test_default_visual_tier_is_diagram(atom_source, project_root):
    """v1.1: convergence_finder defaults to 1_diagram (atom-card handles 3 atoms)."""
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.visual_tier == "1_diagram"


def test_fails_when_no_convergence(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    with pytest.raises(ValueError, match="too narrow"):
        strategy.generate_brief(ctx, {"topic": "totally-unused-tag"})
