"""cluster_reveal — name an emergent theme across ≥4 recently-captured atoms."""
from __future__ import annotations

import uuid

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext, eligible_atoms


class ClusterReveal:
    name = "cluster_reveal"
    MIN_CLUSTER_SIZE = 4

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        cluster_anchor = params.get("cluster_anchor")
        since = params.get("since")

        candidates = ctx.loader.load_all()
        if cluster_anchor:
            candidates = [a for a in candidates if cluster_anchor in a.tags and a.type != "connection"]
        elif since:
            since_date = since
            candidates = [
                a for a in candidates
                if a.type != "connection" and a.source_date and a.source_date >= since_date
            ]
        else:
            raise ValueError("cluster_reveal requires 'cluster_anchor' or 'since'")

        candidates = eligible_atoms(candidates, ctx.atom_tracker, role="primary")
        if len(candidates) < self.MIN_CLUSTER_SIZE:
            raise ValueError(
                f"Cluster too small: need ≥{self.MIN_CLUSTER_SIZE}, have {len(candidates)}"
            )

        candidates.sort(key=lambda a: a.source_date or "", reverse=True)
        chosen = candidates[: self.MIN_CLUSTER_SIZE + 2]

        theme = cluster_anchor or self._infer_theme(chosen)
        angle = (
            f"I keep capturing notes about {theme} without realizing. "
            f"Here's the pattern across {len(chosen)} of them."
        )

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-cluster-{theme.replace(' ', '-')}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"cluster_anchor": cluster_anchor, "since": since, "theme": theme},
            atoms_used=[AtomRef(slug=a.slug, role="primary") for a in chosen],
            angle=angle,
            visual_tier="2_carousel",
            status=Status.DRAFTING,
            topic_tags=sorted({t for a in chosen for t in a.tags}),
        )

    def _infer_theme(self, atoms: list) -> str:
        from collections import Counter
        tag_counts = Counter(t for a in atoms for t in a.tags)
        if not tag_counts:
            return "an unnamed pattern"
        return tag_counts.most_common(1)[0][0]
