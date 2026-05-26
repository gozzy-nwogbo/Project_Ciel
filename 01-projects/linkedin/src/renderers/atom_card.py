"""Tier 1 atom-card renderer (Playwright + Jinja2)."""
from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from atom_loader import AtomLoader
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_TEMPLATE_DIR = Path(__file__).parent / "templates"

# Visual budget caps — keep the 1080×1080 canvas safe even if upstream
# tldrs or thesis lines overshoot.
_ATOM_TEXT_MAX_CHARS = 80
_THESIS_LARGE_MAX_CHARS = 60       # ≤60 chars uses 78px (2-line fit)
_THESIS_LARGE_FONT = "78px"
_THESIS_SMALL_FONT = "60px"


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    """Truncate to max_chars at the last whitespace boundary, append ellipsis."""
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rstrip()
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.") + "…"


_YEAR_SUFFIX_RE = re.compile(r",\s*\d{4}\s*$")


def _strip_citation_year(source: str) -> str:
    """Drop a trailing ", YYYY" from a source slug for visual display.

    Atom `source:` / `origin:` fields use citation form like
    "W. Chan Kim & Renee Mauborgne, 2014" so the engine can match into
    sources.yml. The visual should display the author(s) only — the year
    is metadata, not content.
    """
    return _YEAR_SUFFIX_RE.sub("", source).rstrip()


class AtomCardRenderer:
    tier = 1

    def __init__(
        self,
        loader: AtomLoader,
        sources_registry: Any,
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
        if not brief.atoms_used:
            errors.append("at least 1 atom required")
        if not (brief.thesis or "").strip():
            errors.append("thesis must be non-empty (set brief.thesis before render)")
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        from playwright.sync_api import sync_playwright

        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        ctx = self._build_template_context(brief)
        template = self._env.get_template("atom_card.html.j2")
        html = template.render(**ctx)

        png_path = out_dir / "diagram.png"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1080})
            page.set_content(html, wait_until="networkidle")
            page.screenshot(path=str(png_path), full_page=False, clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
            browser.close()

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered atom-card with {len(ctx['atom_blocks'])} atom blocks in {elapsed:.2f}s"],
        )

    # ---------- internals ----------

    def _build_template_context(self, brief: PostBrief) -> dict:
        colors = self.brand.get("colors", {})
        typography = self.brand.get("typography", {})

        refs = brief.atoms_used
        first_three = refs[:3]
        overflow = refs[3:]

        atom_blocks = []
        for ref in first_three:
            atom = self.loader.load_one(ref.slug)
            name = atom.title if atom else ref.slug
            tldr = (atom.tldr if atom else None) or self._fill_tldr(atom)
            if tldr:
                tldr = _truncate_at_word_boundary(tldr, _ATOM_TEXT_MAX_CHARS)
            atom_blocks.append({"name": name, "text": tldr})

        overflow_line = None
        if overflow:
            slugs = ", ".join(r.slug for r in overflow)
            overflow_line = f"+ {len(overflow)} more atoms inside the post · {slugs}"

        # Source for footer: first cited source from atoms.
        # Prefer atom.source / atom.origin; fall back to ref.source so callers
        # can override at the brief level.
        source_slug = ""
        for ref in refs:
            atom = self.loader.load_one(ref.slug)
            src: Optional[str] = None
            if atom:
                src = atom.source or atom.origin
            if not src:
                src = ref.source
            if src:
                source_slug = _strip_citation_year(src)
                break

        # Domain tag — try first atom's domain, fall back to strategy name.
        domain_tag = "second-brain"
        if refs:
            first_atom = self.loader.load_one(refs[0].slug)
            if first_atom and first_atom.domain:
                domain_tag = f"domain//{first_atom.domain}"

        atom_count = len(refs)
        footer_right = f"{atom_count} atom{'s' if atom_count != 1 else ''} · {brief.strategy.replace('_', '-')}"

        thesis_font_size = (
            _THESIS_LARGE_FONT if len(brief.thesis) <= _THESIS_LARGE_MAX_CHARS
            else _THESIS_SMALL_FONT
        )

        return {
            "colors": {
                "background": colors.get("background", "#FAF8F5"),
                "accent_primary": colors.get("accent_primary", "#B5654A"),
                "text_primary": colors.get("text_primary", "#2C2825"),
                "text_secondary": colors.get("text_secondary", "#6B6560"),
            },
            "typography": {
                "body": typography.get("body", "Geist, system-ui, sans-serif"),
                "mono": typography.get("mono", "Geist Mono, ui-monospace, monospace"),
            },
            "domain_tag": domain_tag,
            "thesis": brief.thesis,
            "thesis_font_size": thesis_font_size,
            "atom_blocks": atom_blocks,
            "overflow_line": overflow_line,
            "source_slug": source_slug,
            "footer_right": footer_right,
        }

    def _fill_tldr(self, atom: Optional[Any]) -> Optional[str]:
        if atom is None or self.tldr_filler is None:
            return None
        return self.tldr_filler.fill(atom)
