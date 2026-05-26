"""convergence_finder — pick 3 atoms from 3 domains with coherent embeddings."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from embeddings.cache import EmbeddingCache
from embeddings.coherence import rank_triples
from embeddings.provider import OpenAIEmbedder
from models import AtomRef, PostBrief, Status, utc_now
from strategies.base import Embedder, StrategyContext, eligible_atoms


DEFAULT_MIN_SIM = 0.35


def _resolve_threshold(params: dict) -> float:
    if "min_sim" in params:
        return float(params["min_sim"])
    env_val = os.environ.get("LINKEDIN_CONVERGENCE_MIN_SIM")
    if env_val:
        return float(env_val)
    return DEFAULT_MIN_SIM


def _resolve_cache_path() -> Path:
    root = os.environ.get("LINKEDIN_PROJECT_ROOT", ".")
    return Path(root) / ".cache" / "atom-embeddings.json"


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
            if a.domain:
                domain_to_atoms.setdefault(a.domain, []).append(a)

        if len(domain_to_atoms) < self.MIN_DOMAINS:
            raise ValueError(
                f"Atom corpus may be too narrow for '{topic}': "
                f"found {len(domain_to_atoms)} domain(s), need >= {self.MIN_DOMAINS}"
            )

        embedder: Embedder = ctx.embedder or OpenAIEmbedder()
        cache = EmbeddingCache(_resolve_cache_path())
        embeddings: dict[str, list[float]] = {}
        for atoms in domain_to_atoms.values():
            for atom in atoms:
                text = f"{atom.title}\n\n{atom.body}"
                embeddings[atom.slug] = cache.get_or_embed(atom.slug, text, embedder)

        ranked = rank_triples(domain_to_atoms, embeddings)
        if not ranked:
            raise ValueError(f"No candidate triples for topic '{topic}'.")

        threshold = _resolve_threshold(params)
        best_score, best_triple = ranked[0]

        if best_score < threshold:
            top_3 = [
                {"slugs": sorted([a.slug for a in triple]), "min_sim": round(score, 4)}
                for score, triple in ranked[:3]
            ]
            raise ValueError(
                f"No triple meets coherence threshold for '{topic}': "
                f"best min_sim={best_score:.4f}, threshold={threshold}. "
                f"top_3={top_3}"
            )

        chosen = list(best_triple)
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
            strategy_params={
                "topic": topic,
                "domains": domains,
                "min_sim": round(best_score, 4),
            },
            atoms_used=[AtomRef(slug=a.slug, role="primary") for a in chosen],
            angle=angle,
            visual_tier="1_diagram",
            aspect_ratio="4:5",
            panel_label=f"CONVERGES ON · {topic.upper()}",
            status=Status.DRAFTING,
            topic_tags=[topic],
        )
