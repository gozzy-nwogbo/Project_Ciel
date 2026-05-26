"""Tests for the Tier 1 renderer registry."""
from pathlib import Path
import pytest

from renderers.registry import for_strategy
from renderers.atom_card import AtomCardRenderer
from renderers.bridge_card import BridgeCardRenderer
from renderers.convergence_card import ConvergenceCardRenderer


@pytest.fixture
def brand_spec(tmp_path: Path) -> Path:
    b = tmp_path / "brand-spec.md"
    b.write_text("```yaml\ncolors: {}\ntypography: {}\n```\n")
    return b


def test_source_spotlight_returns_atom_card_renderer(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    r = for_strategy(
        "source_spotlight",
        loader=AtomLoader(tmp_path),
        sources_registry=None,
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    assert isinstance(r, AtomCardRenderer)


def test_two_atom_bridge_returns_bridge_card_renderer(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    r = for_strategy(
        "two_atom_bridge",
        loader=AtomLoader(tmp_path),
        sources_registry=None,
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    assert isinstance(r, BridgeCardRenderer)


def test_convergence_finder_returns_convergence_card_renderer(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    r = for_strategy(
        "convergence_finder",
        loader=AtomLoader(tmp_path),
        sources_registry=None,
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    assert isinstance(r, ConvergenceCardRenderer)


def test_unknown_strategy_raises(tmp_path, brand_spec):
    from atom_loader import AtomLoader
    with pytest.raises(ValueError, match="No Tier 1 renderer"):
        for_strategy(
            "cluster_reveal",
            loader=AtomLoader(tmp_path),
            sources_registry=None,
            brand_spec_path=brand_spec,
            tldr_filler=None,
        )
