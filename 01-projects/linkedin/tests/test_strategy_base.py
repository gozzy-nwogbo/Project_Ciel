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
