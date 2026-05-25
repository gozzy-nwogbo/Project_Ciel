from pathlib import Path

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from models import AtomRef, PostBrief, Status, utc_now
from renderers.diagram import DiagramRenderer


def _brief() -> PostBrief:
    now = utc_now()
    return PostBrief(
        id="b1",
        slug="2026-05-24-diagram-test",
        created_at=now,
        updated_at=now,
        strategy="two_atom_bridge",
        strategy_params={"atom_a": "sample-concept", "atom_b": "third-concept", "connection_type": "analogical"},
        atoms_used=[
            AtomRef(slug="sample-concept", role="primary"),
            AtomRef(slug="third-concept", role="primary"),
        ],
        angle="A and B are doing the same job.",
        visual_tier="1_diagram",
        visual_brief={"diagram_layout": "bridge", "diagram_emphasis": "mechanism"},
        status=Status.GATE1_APPROVED,
    )


def test_render_writes_png(atom_source, project_root, brand_spec):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
    out_dir = project_root / "backlog" / "2026-05-24-diagram-test"
    out_dir.mkdir(parents=True)
    result = renderer.render(_brief(), out_dir)
    assert any(p.suffix == ".png" for p in result.asset_paths)
    assert all(Path(p).exists() for p in result.asset_paths)


def test_validate_rejects_too_many_nodes(atom_source, project_root, brand_spec):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
    brief = _brief()
    brief.atoms_used = [AtomRef(slug=f"atom{i}", role="primary") for i in range(7)]
    errors = renderer.validate(brief)
    assert any("more than 6 nodes" in e.lower() for e in errors)


def test_validate_rejects_edgeless_tier1(atom_source, project_root, brand_spec):
    """Tier 1 diagrams must have at least one edge among chosen atoms.
    Surfaced by v1.0 smoke (2026-05-25) — source_spotlight picked 3 Rumelt
    atoms with no connection atoms between them, producing 3 floating ovals."""
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    renderer = DiagramRenderer(loader=loader, graph=graph, brand_spec_path=brand_spec)
    brief = _brief()
    # Replace atoms_used with atoms that have NO connection atoms among them.
    brief.atoms_used = [
        AtomRef(slug="security-trust", role="primary"),
        AtomRef(slug="law-trust", role="primary"),
        AtomRef(slug="child-trust", role="primary"),
    ]
    errors = renderer.validate(brief)
    assert any("no edges" in e.lower() or "edgeless" in e.lower() for e in errors)
