"""convergence_finder — find a topic touched by atoms across ≥3 distinct domains."""
from __future__ import annotations

import uuid

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext, eligible_atoms


class ConvergenceFinder:
    name = "convergence_finder"
    MIN_DOMAINS = 3

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        topic = params.get("topic")
        if not topic:
            raise ValueError("convergence_finder requires 'topic' param")

        all_atoms = ctx.loader.load_all()
        topic_touchers = [
            a for a in all_atoms
            if a.type != "connection"
            and (topic in a.tags or topic in (a.title or "").lower() or topic in (a.body or "").lower())
        ]
        topic_touchers = eligible_atoms(topic_touchers, ctx.atom_tracker, role="primary")

        domain_to_atoms: dict[str, list] = {}
        for a in topic_touchers:
            if not a.domain:
                continue
            domain_to_atoms.setdefault(a.domain, []).append(a)

        if len(domain_to_atoms) < self.MIN_DOMAINS:
            raise ValueError(
                f"Atom corpus may be too narrow for '{topic}': "
                f"found {len(domain_to_atoms)} domain(s), need ≥{self.MIN_DOMAINS}"
            )

        chosen = []
        for domain, atoms in list(domain_to_atoms.items())[:self.MIN_DOMAINS]:
            atoms.sort(key=lambda a: len(ctx.graph.edges_for(a.slug)), reverse=True)
            chosen.append(atoms[0])

        domains = [a.domain for a in chosen]
        angle = (
            f"{topic.capitalize()} shows up in {', '.join(domains[:-1])}, "
            f"and {domains[-1]}. {len(chosen)} solutions to the same problem."
        )

        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-convergence-{topic.replace(' ', '-')}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={"topic": topic, "domains": domains},
            atoms_used=[AtomRef(slug=a.slug, role="primary") for a in chosen],
            angle=angle,
            visual_tier="1_diagram",
            aspect_ratio="4:5",
            panel_label=f"CONVERGES ON · {topic.upper()}",
            status=Status.DRAFTING,
            topic_tags=[topic],
        )
