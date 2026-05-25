import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.two_atom_bridge import TwoAtomBridge
from usage.atom_usage import AtomUsageTracker
from usage.connection_usage import ConnectionUsageTracker


def _ctx(atom_source, project_root):
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
        connection_tracker=ConnectionUsageTracker(project_root / "state" / "connection-usage.json"),
    )


def test_explicit_pair_uses_typed_claim(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = TwoAtomBridge()
    brief = strategy.generate_brief(ctx, {
        "atom_a": "sample-concept",
        "atom_b": "third-concept",
    })
    assert brief.strategy == "two_atom_bridge"
    assert len(brief.atoms_used) == 2
    assert brief.strategy_params.get("connection_type") == "analogical"


def test_default_visual_tier_is_diagram(atom_source, project_root):
    """v1.1: two_atom_bridge defaults to 1_diagram (atom-card handles 2 atoms)."""
    ctx = _ctx(atom_source, project_root)
    strategy = TwoAtomBridge()
    brief = strategy.generate_brief(ctx, {
        "atom_a": "sample-concept",
        "atom_b": "third-concept",
    })
    assert brief.visual_tier == "1_diagram"


def test_same_domain_rejected(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = TwoAtomBridge()
    with pytest.raises(ValueError, match="same domain"):
        strategy.generate_brief(ctx, {
            "atom_a": "sample-concept",
            "atom_b": "another-concept",
        })
