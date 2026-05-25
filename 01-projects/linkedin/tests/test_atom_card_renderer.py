from pathlib import Path
from unittest.mock import MagicMock

from atom_loader import Atom
from models import AtomRef, PostBrief, Status, utc_now
from renderers.atom_card import AtomCardRenderer


def _brief(slugs: list[str], thesis: str = "Locked thesis line.") -> PostBrief:
    now = utc_now()
    return PostBrief(
        id="b1",
        slug="2026-05-25-atomcard-test",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug=s, role="primary", source="Test Source, 2026") for s in slugs],
        angle="An angle.",
        visual_tier="1_diagram",
        status=Status.GATE1_APPROVED,
        thesis=thesis,
    )


def _atom(slug: str, tldr: str | None) -> Atom:
    return Atom(
        slug=slug,
        title=slug.replace("-", " ").title(),
        type="concept",
        source_date="",
        body=f"Body for {slug}.",
        tags=[],
        domain="test",
        source="Test Source, 2026",
        tldr=tldr,
        path=None,
    )


def test_validate_allows_4_plus_atoms_via_overflow_rule(brand_spec):
    """4+ atoms is legal — render path handles via overflow rule. Validate doesn't reject."""
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, "tldr-" + s)

    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    brief = _brief(["a", "b", "c", "d", "e"])
    errors = renderer.validate(brief)
    assert errors == []


def test_validate_rejects_empty_thesis(brand_spec):
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, "tldr-" + s)
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    brief = _brief(["a"], thesis="")
    errors = renderer.validate(brief)
    assert any("thesis" in e.lower() for e in errors)


def test_validate_rejects_zero_atoms(brand_spec):
    loader = MagicMock()
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    brief = _brief([])
    errors = renderer.validate(brief)
    assert any("at least 1" in e.lower() or "zero" in e.lower() for e in errors)


def test_build_template_context_caps_at_three_with_overflow_line(brand_spec):
    """When 4+ atoms, first 3 render normally; remainder become overflow line."""
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, f"tldr-{s}")

    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    brief = _brief(["a", "b", "c", "d", "e"])
    ctx = renderer._build_template_context(brief)
    assert len(ctx["atom_blocks"]) == 3
    assert ctx["atom_blocks"][0]["name"] == "A"
    assert ctx["overflow_line"] is not None
    assert "2 more" in ctx["overflow_line"]
    assert "d" in ctx["overflow_line"]
    assert "e" in ctx["overflow_line"]


def test_build_template_context_no_overflow_for_three_or_fewer(brand_spec):
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, f"tldr-{s}")
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    brief = _brief(["a", "b", "c"])
    ctx = renderer._build_template_context(brief)
    assert len(ctx["atom_blocks"]) == 3
    assert ctx["overflow_line"] is None


def test_missing_tldr_triggers_filler_when_provided(brand_spec):
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, tldr=None)

    filler = MagicMock()
    filler.fill.return_value = "Filled tldr."

    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=filler,
    )
    brief = _brief(["a"])
    ctx = renderer._build_template_context(brief)
    assert ctx["atom_blocks"][0]["text"] == "Filled tldr."
    filler.fill.assert_called_once()


def test_missing_tldr_and_no_filler_renders_name_only(brand_spec):
    loader = MagicMock()
    loader.load_one.side_effect = lambda s: _atom(s, tldr=None)
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    brief = _brief(["a"])
    ctx = renderer._build_template_context(brief)
    assert ctx["atom_blocks"][0]["name"] == "A"
    assert ctx["atom_blocks"][0]["text"] is None


def test_render_writes_png(tmp_path, atom_source, brand_spec):
    """Smoke: actual Playwright invocation produces a PNG file.

    Skip if env says so (SKIP_PLAYWRIGHT_TESTS=1).
    """
    import os
    if os.environ.get("SKIP_PLAYWRIGHT_TESTS"):
        import pytest
        pytest.skip("SKIP_PLAYWRIGHT_TESTS=1")

    from atom_loader import AtomLoader
    loader = AtomLoader(atom_source)

    brief = _brief(["sample-concept"])
    renderer = AtomCardRenderer(
        loader=loader,
        sources_registry=MagicMock(),
        brand_spec_path=brand_spec,
        tldr_filler=None,
    )
    out_dir = tmp_path / "bundle"
    out_dir.mkdir()
    result = renderer.render(brief, out_dir)

    assert any(p.suffix == ".png" for p in result.asset_paths)
    assert all(Path(p).exists() and Path(p).stat().st_size > 0 for p in result.asset_paths)
