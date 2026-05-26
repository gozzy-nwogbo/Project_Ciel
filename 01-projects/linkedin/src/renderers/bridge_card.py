"""Tier 1 BridgeCardRenderer (Playwright + Jinja2). Bridge A at 4:5."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from atom_loader import AtomLoader
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_TEMPLATE_DIR = Path(__file__).parent / "templates"

_ATOM_TEXT_MAX_CHARS = 110
_THESIS_LARGE_MAX_CHARS = 60
_THESIS_LARGE_FONT = "78px"
_THESIS_SMALL_FONT = "60px"

_VIEWPORT_BY_RATIO = {"1:1": (1080, 1080), "4:5": (1080, 1350)}


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rstrip()
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.") + "…"


class BridgeCardRenderer:
    tier = 1

    def __init__(
        self,
        loader: AtomLoader,
        sources_registry: Optional[Any],
        brand_spec_path: Path,
        tldr_filler: Optional[Any] = None,
    ):
        self.loader = loader
        self.sources_registry = sources_registry
        self.brand = load_brand_spec(brand_spec_path)
        self.tldr_filler = tldr_filler
        self._env = Environment(
            loader=FileSystemLoader(_TEMPLATE_DIR),
            autoescape=select_autoescape(["html"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def validate(self, brief: PostBrief) -> list[str]:
        errors: list[str] = []
        if not (brief.thesis or "").strip():
            errors.append("thesis must be non-empty")
        if len(brief.atoms_used) != 2:
            errors.append("bridge renderer requires exactly 2 atoms")
        if not (brief.panel_label or "").strip():
            errors.append("panel_label must be non-empty")
        if not (brief.panel_claim or "").strip():
            errors.append("panel_claim must be non-empty")
        if brief.aspect_ratio != "4:5":
            errors.append("bridge renderer requires aspect_ratio == \"4:5\"")
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        from playwright.sync_api import sync_playwright

        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._build_template_context(brief)
        template = self._env.get_template("bridge_card.html.j2")
        html = template.render(**ctx)

        viewport_w, viewport_h = _VIEWPORT_BY_RATIO[brief.aspect_ratio]
        png_path = out_dir / "diagram.png"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": viewport_w, "height": viewport_h})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(
                path=str(png_path),
                full_page=False,
                clip={"x": 0, "y": 0, "width": viewport_w, "height": viewport_h},
            )
            browser.close()

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered bridge-card in {elapsed:.2f}s"],
        )

    # ---------- internals ----------

    def _build_template_context(self, brief: PostBrief) -> dict:
        colors = self.brand.get("colors", {})
        typography = self.brand.get("typography", {})

        atom_a_ref, atom_b_ref = brief.atoms_used
        atom_a_full = self.loader.load_one(atom_a_ref.slug)
        atom_b_full = self.loader.load_one(atom_b_ref.slug)

        def _block(atom, ref) -> dict:
            name = atom.title if atom else ref.slug
            domain = (atom.domain if atom else None) or ""
            tldr = (atom.tldr if atom else None) or self._fill_tldr(atom) or ""
            return {
                "name": name,
                "domain": domain,
                "tldr": _truncate_at_word_boundary(tldr, _ATOM_TEXT_MAX_CHARS),
            }

        atom_a = _block(atom_a_full, atom_a_ref)
        atom_b = _block(atom_b_full, atom_b_ref)

        thesis_font_size = (
            _THESIS_LARGE_FONT if len(brief.thesis) <= _THESIS_LARGE_MAX_CHARS
            else _THESIS_SMALL_FONT
        )

        domain_tag = "bridge"
        if atom_a["domain"] and atom_b["domain"]:
            domain_tag = f"bridge // {atom_a['domain']} × {atom_b['domain']}"

        return {
            "colors": {
                "background": colors.get("background", "#FAF8F5"),
                "accent_primary": colors.get("accent_primary", "#B5654A"),
                "text_primary": colors.get("text_primary", "#2C2825"),
                "text_secondary": colors.get("text_secondary", "#6B6560"),
                "surface_subtle": colors.get("surface_subtle", "#F3F0EB"),
                "border": colors.get("border", "#E8E4DF"),
            },
            "typography": {
                "body": typography.get("body", "Geist, system-ui, sans-serif"),
                "mono": typography.get("mono", "Geist Mono, ui-monospace, monospace"),
            },
            "domain_tag": domain_tag,
            "thesis": brief.thesis,
            "thesis_font_size": thesis_font_size,
            "atom_a": atom_a,
            "atom_b": atom_b,
            "panel_label": brief.panel_label,
            "panel_claim": brief.panel_claim,
        }

    def _fill_tldr(self, atom: Optional[Any]) -> Optional[str]:
        if atom is None or self.tldr_filler is None:
            return None
        return self.tldr_filler.fill(atom)
