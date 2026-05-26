"""Tier 1 ConvergenceCardRenderer (Playwright + Jinja2). Convergence C at 4:5."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from atom_loader import AtomLoader
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_TEMPLATE_DIR = Path(__file__).parent / "templates"

_ATOM_TEXT_MAX_CHARS = 60
_THESIS_LARGE_MAX_CHARS = 60
_THESIS_LARGE_FONT = "78px"
_THESIS_SMALL_FONT = "60px"
_MAX_FUNNEL_ATOMS = 3

_VIEWPORT_BY_RATIO = {"1:1": (1080, 1080), "4:5": (1080, 1350)}


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rstrip()
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.") + "…"


class ConvergenceCardRenderer:
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
        if len(brief.atoms_used) < 3:
            errors.append("convergence renderer requires at least 3 atoms")
        if not (brief.panel_label or "").strip():
            errors.append("panel_label must be non-empty")
        if not (brief.panel_claim or "").strip():
            errors.append("panel_claim must be non-empty")
        if brief.aspect_ratio != "4:5":
            errors.append("convergence renderer requires aspect_ratio == \"4:5\"")
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        from playwright.sync_api import sync_playwright

        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._build_template_context(brief)
        template = self._env.get_template("convergence_card.html.j2")
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
            logs=[f"Rendered convergence-card in {elapsed:.2f}s"],
        )

    # ---------- internals ----------

    def _build_template_context(self, brief: PostBrief) -> dict:
        colors = self.brand.get("colors", {})
        typography = self.brand.get("typography", {})

        refs = brief.atoms_used[:_MAX_FUNNEL_ATOMS]
        atom_blocks = []
        seen_domains: set[str] = set()
        for ref in refs:
            atom = self.loader.load_one(ref.slug)
            name = atom.title if atom else ref.slug
            domain = (atom.domain if atom else None) or ""
            tldr = (atom.tldr if atom else None) or self._fill_tldr(atom) or ""
            tldr = _truncate_at_word_boundary(tldr, _ATOM_TEXT_MAX_CHARS)
            atom_blocks.append({"name": name, "domain": domain, "tldr": tldr})
            if domain:
                seen_domains.add(domain)

        thesis_font_size = (
            _THESIS_LARGE_FONT if len(brief.thesis) <= _THESIS_LARGE_MAX_CHARS
            else _THESIS_SMALL_FONT
        )

        total_atoms = len(brief.atoms_used)
        domain_count = len(seen_domains)
        footer_left = f"{total_atoms} atoms · {domain_count} domains"
        domain_tag = f"convergence // {domain_count} domains"

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
            "atom_blocks": atom_blocks,
            "panel_label": brief.panel_label,
            "panel_claim": brief.panel_claim,
            "footer_left": footer_left,
        }

    def _fill_tldr(self, atom: Optional[Any]) -> Optional[str]:
        if atom is None or self.tldr_filler is None:
            return None
        return self.tldr_filler.fill(atom)
