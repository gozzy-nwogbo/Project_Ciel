"""Tier 1 diagram renderer (graphviz)."""
from __future__ import annotations

import time
from pathlib import Path

import graphviz

from atom_loader import AtomLoader
from connection_graph import ConnectionGraph
from models import PostBrief
from renderers.base import RenderResult, load_brand_spec


_EDGE_STYLE_BY_TYPE = {
    "mechanism": {"style": "solid", "penwidth": "2.5"},
    "analogical": {"style": "dashed", "penwidth": "1.5"},
    "causal": {"style": "solid", "penwidth": "1.8", "arrowhead": "vee"},
    "inverse": {"style": "solid", "penwidth": "1.5", "arrowhead": "diamond"},
    "compositional": {"style": "solid", "penwidth": "1.5"},
    "genealogical": {"style": "solid", "penwidth": "1.2"},
    "critique": {"style": "dashed", "penwidth": "1.5", "arrowhead": "tee"},
    "epistemic": {"style": "dotted", "penwidth": "1.5"},
    "general": {"style": "solid", "penwidth": "1.0"},
}


class DiagramRenderer:
    tier = 1

    def __init__(self, loader: AtomLoader, graph: ConnectionGraph, brand_spec_path: Path):
        self.loader = loader
        self.graph = graph
        self.brand = load_brand_spec(brand_spec_path)

    def validate(self, brief: PostBrief) -> list[str]:
        errors: list[str] = []
        n = len(brief.atoms_used)
        if n > 6:
            errors.append(f"Diagram cannot have more than 6 nodes (got {n})")
        if n < 1:
            errors.append("Diagram needs at least 1 node")
        if n >= 2:
            slugs = {ref.slug for ref in brief.atoms_used}
            edges_in_subgraph = [
                e for e in self.graph.edges
                if e.from_slug in slugs and e.to_slug in slugs
            ]
            if not edges_in_subgraph:
                errors.append(
                    "Edgeless diagram: no connection atoms exist among the chosen "
                    f"{n} atoms. Floating nodes are not shippable; choose a different "
                    "strategy, add connection atoms, or skip the Tier 1 visual."
                )
        return errors

    def render(self, brief: PostBrief, out_dir: Path) -> RenderResult:
        start = time.time()
        errors = self.validate(brief)
        if errors:
            raise ValueError(f"Renderer validation failed: {errors}")
        out_dir.mkdir(parents=True, exist_ok=True)

        colors = self.brand.get("colors", {})
        typo = self.brand.get("typography", {})
        layout = self.brand.get("layout", {})

        dot = graphviz.Digraph(
            "linkedin_diagram",
            graph_attr={
                "bgcolor": colors.get("background", "#FFFFFF"),
                "pad": str(layout.get("padding", 24) / 24),
                "rankdir": "LR" if brief.visual_brief.get("diagram_layout") == "bridge" else "TB",
            },
            node_attr={
                "shape": "box",
                "style": "rounded,filled",
                "fillcolor": colors.get("background", "#FFFFFF"),
                "color": colors.get("accent_primary", "#1F1F1F"),
                "fontname": typo.get("body", "sans-serif"),
                "fontsize": str(typo.get("size_label", "11px")).replace("px", ""),
                "fontcolor": colors.get("text_primary", "#1F1F1F"),
                "margin": "0.2,0.1",
            },
            edge_attr={
                "color": colors.get("edge_default", "#737373"),
                "fontname": typo.get("body", "sans-serif"),
                "fontsize": str(typo.get("size_label", "11px")).replace("px", ""),
            },
        )

        slugs_in_brief = {ref.slug for ref in brief.atoms_used}
        for ref in brief.atoms_used:
            atom = self.loader.load_one(ref.slug)
            label = (atom.title if atom else ref.slug)
            dot.node(ref.slug, label=label)

        for edge in self.graph.edges:
            if edge.from_slug in slugs_in_brief and edge.to_slug in slugs_in_brief:
                style = _EDGE_STYLE_BY_TYPE.get(edge.connection_type, _EDGE_STYLE_BY_TYPE["general"])
                label = edge.connection_type if edge.connection_type != "general" else ""
                dot.edge(edge.from_slug, edge.to_slug, label=label, **style)

        png_path = out_dir / "diagram.png"
        svg_path = out_dir / "diagram.svg"
        dot.format = "png"
        dot.render(filename="diagram", directory=out_dir, cleanup=True)
        dot.format = "svg"
        dot.render(filename="diagram", directory=out_dir, cleanup=True)

        elapsed = time.time() - start
        return RenderResult(
            asset_paths=[png_path, svg_path],
            cost=0.0,
            duration_s=elapsed,
            logs=[f"Rendered {len(slugs_in_brief)} nodes in {elapsed:.2f}s"],
        )
