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
    """v1.2: bridge defaults to Tier 1 diagram at 4:5."""
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


def test_bridge_brief_uses_tier1_diagram_at_4x5(atom_source, project_root):
    """v1.2: bridge defaults to Tier 1 atom-card at 4:5."""
    ctx = _ctx(atom_source, project_root)
    strategy = TwoAtomBridge()
    brief = strategy.generate_brief(ctx, {
        "atom_a": "sample-concept",
        "atom_b": "third-concept",
    })
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


def test_bridge_unknown_connection_type_falls_back_to_bridge_label(
    atom_source, project_root, monkeypatch
):
    """If a connection edge has an unrecognized connection_type, generate_brief falls back to BRIDGE."""
    from connection_graph import Edge

    ctx = _ctx(atom_source, project_root)

    synthetic_edge = Edge(
        from_slug="sample-concept",
        to_slug="third-concept",
        from_title="Sample Concept",
        to_title="Third Concept",
        connection_type="unknown-type",
        claim="",
    )
    monkeypatch.setattr(ctx.graph, "edges_for", lambda slug: [synthetic_edge])

    brief = TwoAtomBridge().generate_brief(ctx, {
        "atom_a": "sample-concept",
        "atom_b": "third-concept",
    })
    assert brief.panel_label == "BRIDGE"
