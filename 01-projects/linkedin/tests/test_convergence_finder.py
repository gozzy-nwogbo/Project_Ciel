import os

import pytest

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from strategies.base import StrategyContext
from strategies.convergence_finder import ConvergenceFinder
from usage.atom_usage import AtomUsageTracker


class _ConstantEmbedder:
    """Returns the same unit vector for every text. All pairs score 1.0."""
    def embed(self, text: str) -> list[float]:
        return [1.0, 0.0, 0.0]


def _ctx(atom_source, project_root):
    # Cache lives under project_root/.cache; tmp project_root keeps tests isolated.
    os.environ["LINKEDIN_PROJECT_ROOT"] = str(project_root)
    loader = AtomLoader(atom_source)
    return StrategyContext(
        loader=loader,
        graph=ConnectionGraph(loader.load_all()),
        atom_tracker=AtomUsageTracker(project_root / "state" / "atom-usage.json"),
        embedder=_ConstantEmbedder(),
    )


def test_finds_three_domains(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.strategy == "convergence_finder"
    domains = {ctx.loader.load_one(ref.slug).domain for ref in brief.atoms_used}
    assert len(domains) >= 3


def test_default_visual_tier_is_diagram(atom_source, project_root):
    """v1.2: convergence defaults to Tier 1 diagram at 4:5."""
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.visual_tier == "1_diagram"


def test_convergence_brief_uses_tier1_diagram_at_4x5(atom_source, project_root):
    """v1.2: convergence_finder defaults to Tier 1 atom-card at 4:5."""
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.visual_tier == "1_diagram"
    assert brief.aspect_ratio == "4:5"
    assert brief.panel_claim == ""


def test_convergence_panel_label_composes_from_topic(atom_source, project_root):
    """panel_label is 'CONVERGES ON · {topic.upper()}'."""
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "trust"})
    assert brief.panel_label == "CONVERGES ON · TRUST"


def test_convergence_panel_label_uppercases_multiword_topic(atom_source, project_root):
    """Topic with spaces is uppercased verbatim."""
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    brief = strategy.generate_brief(ctx, {"topic": "decision making"})
    assert brief.panel_label == "CONVERGES ON · DECISION MAKING"


def test_fails_when_no_convergence(atom_source, project_root):
    ctx = _ctx(atom_source, project_root)
    strategy = ConvergenceFinder()
    with pytest.raises(ValueError, match="too narrow"):
        strategy.generate_brief(ctx, {"topic": "totally-unused-tag"})
