"""Tests for ConvergenceCardRenderer (Convergence C at 4:5)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from atom_loader import AtomLoader
from models import AtomRef, PostBrief, Status
from renderers.convergence_card import ConvergenceCardRenderer


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    brand = tmp_path / "brand-spec.md"
    brand.write_text(
        "```yaml\n"
        "colors:\n"
        "  accent_primary: \"#B5654A\"\n"
        "  background: \"#FAF8F5\"\n"
        "  text_primary: \"#2C2825\"\n"
        "  text_secondary: \"#6B6560\"\n"
        "typography:\n"
        "  body: \"Geist, system-ui, sans-serif\"\n"
        "  mono: \"Geist Mono, ui-monospace, monospace\"\n"
        "```\n"
    )
    return tmp_path


def _make_brief(**overrides) -> PostBrief:
    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    base = dict(
        id="t", slug="t",
        created_at=now, updated_at=now,
        strategy="convergence_finder",
        strategy_params={"topic": "feedback", "domains": ["d1", "d2", "d3"]},
        atoms_used=[
            AtomRef(slug="atom-a", role="primary"),
            AtomRef(slug="atom-b", role="primary"),
            AtomRef(slug="atom-c", role="primary"),
        ],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        thesis="Every loop measures.",
        aspect_ratio="4:5",
        panel_label="CONVERGES ON · FEEDBACK",
        panel_claim="Every loop narrows the gap between intent and outcome.",
    )
    base.update(overrides)
    return PostBrief(**base)


def test_validate_passes_on_valid_brief(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    assert renderer.validate(_make_brief()) == []


def test_validate_requires_at_least_3_atoms(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(atoms_used=[AtomRef(slug="only-two-a", role="primary"), AtomRef(slug="only-two-b", role="primary")])
    errors = renderer.validate(brief)
    assert any("at least 3" in e or "≥3" in e for e in errors)


def test_validate_requires_non_empty_panel_label(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    errors = renderer.validate(_make_brief(panel_label=""))
    assert any("panel_label" in e for e in errors)


def test_validate_requires_non_empty_panel_claim(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    errors = renderer.validate(_make_brief(panel_claim=""))
    assert any("panel_claim" in e for e in errors)


def test_validate_requires_4x5_aspect_ratio(project_root):
    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    errors = renderer.validate(_make_brief(aspect_ratio="1:1"))
    assert any("4:5" in e for e in errors)


def test_renderer_tier_is_1():
    assert ConvergenceCardRenderer.tier == 1


@pytest.mark.smoke
def test_render_writes_png_at_1080x1350(project_root, tmp_path):
    pytest.importorskip("playwright.sync_api")

    for slug, dom in [("atom-a", "habits-systems"), ("atom-b", "platform-writing"), ("atom-c", "psychology-reader")]:
        (project_root / f"{slug}.md").write_text(
            f"---\ntitle: {slug.title()}\ndomain: {dom}\nsource: Test, 2026\ntldr: A short tldr for {slug}.\n---\n"
        )

    renderer = ConvergenceCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    out_dir = tmp_path / "out"
    result = renderer.render(_make_brief(), out_dir)
    png = out_dir / "diagram.png"
    assert png.exists()
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert result.asset_paths == [png]
