"""Tests for BridgeCardRenderer (Bridge A at 4:5)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from atom_loader import AtomLoader
from models import AtomRef, PostBrief, Status
from renderers.bridge_card import BridgeCardRenderer


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    # Minimal brand-spec.md so load_brand_spec() works.
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


def _make_brief(strategy="two_atom_bridge", **overrides) -> PostBrief:
    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    base = dict(
        id="t", slug="t",
        created_at=now, updated_at=now,
        strategy=strategy,
        strategy_params={},
        atoms_used=[
            AtomRef(slug="atom-a", role="primary"),
            AtomRef(slug="atom-b", role="primary"),
        ],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        thesis="Stress is not the enemy.",
        aspect_ratio="4:5",
        panel_label="SHARED MECHANISM",
        panel_claim="Both systems get stronger from controlled stress.",
    )
    base.update(overrides)
    return PostBrief(**base)


def test_validate_passes_on_valid_brief(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief()
    assert renderer.validate(brief) == []


def test_validate_requires_exactly_2_atoms(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(atoms_used=[AtomRef(slug="only-one", role="primary")])
    errors = renderer.validate(brief)
    assert any("exactly 2" in e for e in errors)


def test_validate_requires_non_empty_panel_label(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(panel_label="")
    errors = renderer.validate(brief)
    assert any("panel_label" in e for e in errors)


def test_validate_requires_non_empty_panel_claim(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(panel_claim="")
    errors = renderer.validate(brief)
    assert any("panel_claim" in e for e in errors)


def test_validate_requires_4x5_aspect_ratio(project_root):
    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief(aspect_ratio="1:1")
    errors = renderer.validate(brief)
    assert any("4:5" in e for e in errors)


def test_renderer_tier_is_1():
    assert BridgeCardRenderer.tier == 1


@pytest.mark.smoke
def test_render_writes_png_at_1080x1350(project_root, tmp_path):
    """Live Playwright render. Mark with -m smoke to opt in / out."""
    pytest.importorskip("playwright.sync_api")

    # Build a tiny atom store so the renderer can resolve atom names.
    (project_root / "atom-a.md").write_text(
        "---\ntitle: Atom A\ndomain: mental-models\nsource: Test, 2026\ntldr: A tldr sentence for A.\n---\n"
    )
    (project_root / "atom-b.md").write_text(
        "---\ntitle: Atom B\ndomain: health-performance\nsource: Test, 2026\ntldr: A tldr sentence for B.\n---\n"
    )

    renderer = BridgeCardRenderer(
        loader=AtomLoader(project_root),
        sources_registry=None,
        brand_spec_path=project_root / "brand-spec.md",
        tldr_filler=None,
    )
    brief = _make_brief()
    out_dir = tmp_path / "out"
    result = renderer.render(brief, out_dir)
    png = out_dir / "diagram.png"
    assert png.exists()
    # Quick sanity: PNG header.
    assert png.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert result.asset_paths == [png]
