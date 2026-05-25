from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.source_spotlight import SourceSpotlight
from usage.atom_usage import AtomUsageTracker


def test_source_spotlight_returns_brief(atom_source, project_root):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json")
    ctx = StrategyContext(loader=loader, graph=graph, atom_tracker=tracker)

    strategy = SourceSpotlight()
    brief = strategy.generate_brief(ctx, {"source": "test-fixture", "atom_count": 2})

    assert brief.strategy == "source_spotlight"
    assert len(brief.atoms_used) >= 2
    assert "test-fixture" in brief.angle or brief.strategy_params["source"] == "test-fixture"
    assert all(ref.role == "primary" for ref in brief.atoms_used)


def test_source_spotlight_excludes_cooldown(atom_source, project_root):
    loader = AtomLoader(atom_source)
    graph = ConnectionGraph(loader.load_all())
    tracker = AtomUsageTracker(project_root / "state" / "atom-usage.json")
    tracker.mark_used("sample-concept", role="primary", post_id="prev")
    ctx = StrategyContext(loader=loader, graph=graph, atom_tracker=tracker)

    strategy = SourceSpotlight()
    brief = strategy.generate_brief(ctx, {"source": "test-fixture", "atom_count": 2})
    slugs = {ref.slug for ref in brief.atoms_used}
    assert "sample-concept" not in slugs
