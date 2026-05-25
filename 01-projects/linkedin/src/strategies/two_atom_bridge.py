"""two_atom_bridge — surface the shared mechanism across two atoms from different domains."""
from __future__ import annotations

import uuid

from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import StrategyContext


class TwoAtomBridge:
    name = "two_atom_bridge"

    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief:
        slug_a = params.get("atom_a")
        slug_b = params.get("atom_b")
        if not slug_a or not slug_b:
            raise ValueError("two_atom_bridge requires 'atom_a' and 'atom_b'")
        atom_a = ctx.loader.load_one(slug_a)
        atom_b = ctx.loader.load_one(slug_b)
        if not atom_a or not atom_b:
            raise ValueError(f"Unknown atom slug(s): {slug_a}, {slug_b}")
        if atom_a.domain and atom_b.domain and atom_a.domain == atom_b.domain:
            raise ValueError(
                f"Atoms share same domain '{atom_a.domain}' — bridge requires different domains"
            )

        connection_type = "general"
        claim = ""
        for edge in ctx.graph.edges_for(slug_a):
            if {edge.from_slug, edge.to_slug} == {slug_a, slug_b}:
                connection_type = edge.connection_type
                claim = edge.claim
                break

        if ctx.connection_tracker and ctx.connection_tracker.is_in_cooldown(slug_a, slug_b):
            raise ValueError(
                f"Connection {slug_a} <-> {slug_b} is in cooldown"
            )

        angle = self._compose_angle(atom_a, atom_b, connection_type)
        now = utc_now()
        return PostBrief(
            id=str(uuid.uuid4()),
            slug=f"{now.strftime('%Y-%m-%d')}-bridge-{slug_a}-{slug_b}",
            created_at=now,
            updated_at=now,
            strategy=self.name,
            strategy_params={
                "atom_a": slug_a,
                "atom_b": slug_b,
                "connection_type": connection_type,
                "claim": claim,
            },
            atoms_used=[
                AtomRef(slug=slug_a, role="primary"),
                AtomRef(slug=slug_b, role="primary"),
            ],
            angle=angle,
            visual_tier="1_diagram",
            status=Status.DRAFTING,
            topic_tags=sorted(set(atom_a.tags + atom_b.tags)),
        )

    def _compose_angle(self, a, b, connection_type: str) -> str:
        domain_a = a.domain or "this domain"
        domain_b = b.domain or "another domain"
        if connection_type == "mechanism":
            return f"{domain_a} and {domain_b} are running the same mechanism."
        if connection_type == "analogical":
            return f"{a.title} and {b.title} are structural analogues across {domain_a} and {domain_b}."
        if connection_type == "inverse":
            return f"{a.title} and {b.title} are inverses — and the contrast clarifies both."
        return f"{a.title} and {b.title} touch in a way most people miss."
