"""source_spotlight strategy — N atoms from one source + secondary domain finder."""
from __future__ import annotations

import random
import uuid
from collections import Counter
from datetime import datetime
from typing import Optional

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext, eligible_atoms


class SourceSpotlight:
    name = "source_spotlight"

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        source = params.get("source")
        if not source:
            raise ValueError("source_spotlight requires 'source' param")
        atom_count = int(params.get("atom_count", 3))

        candidates = [
            a for a in ctx.loader.load_by_source(source)
            if a.type != "connection"
        ]
        candidates = eligible_atoms(candidates, ctx.atom_tracker, role="primary")
        if len(candidates) < atom_count:
            raise ValueError(
                f"Not enough eligible atoms for source '{source}': "
                f"need {atom_count}, have {len(candidates)}"
            )

        candidates.sort(key=lambda a: a.source_date or "", reverse=True)
        picks = candidates[: atom_count * 2]
        random.shuffle(picks)
        chosen = picks[:atom_count]

        secondary_domain = self._find_secondary_domain(ctx, chosen)
        angle = self._compose_angle(source, secondary_domain, chosen)

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=self._make_slug(now, source),
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"source": source, "atom_count": atom_count, "secondary_domain": secondary_domain},
            atoms_used=[AtomRef(slug=a.slug, role="primary", source=source) for a in chosen],
            angle=angle,
            visual_tier="1_diagram",
            status=Status.DRAFTING,
            topic_tags=sorted({t for a in chosen for t in a.tags}),
        )

    def _find_secondary_domain(self, ctx: StrategyContext, chosen: list) -> Optional[str]:
        """Find a domain that ≥2 of the chosen atoms connect to (via their neighbors)."""
        neighbor_domains: Counter[str] = Counter()
        chosen_slugs = {a.slug for a in chosen}
        chosen_domains = {a.domain for a in chosen if a.domain}
        for atom in chosen:
            for neighbor_slug in ctx.graph.neighbors(atom.slug):
                if neighbor_slug in chosen_slugs:
                    continue
                neighbor = ctx.loader.load_one(neighbor_slug)
                if not neighbor or not neighbor.domain:
                    continue
                if neighbor.domain in chosen_domains:
                    continue
                neighbor_domains[neighbor.domain] += 1
        if not neighbor_domains:
            return None
        top, count = neighbor_domains.most_common(1)[0]
        return top if count >= 2 else None

    def _compose_angle(self, source: str, secondary: Optional[str], chosen: list) -> str:
        n = len(chosen)
        if secondary:
            return f"{n} ideas from {source} all touch {secondary}. Here's why that matters."
        joined = ", ".join(a.title for a in chosen)
        return f"{n} ideas from {source} — {joined} — sharing one pattern."

    def _make_slug(self, now: datetime, source: str) -> str:
        date = now.strftime("%Y-%m-%d")
        source_slug = source.lower().replace(" ", "-").replace(".", "")
        return f"{date}-{source_slug}-spotlight"
