"""Coherence math: cosine similarity, min-pairwise, triple ranking."""
from __future__ import annotations

import itertools
import math
from typing import Sequence

from atom_loader import Atom


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Standard cosine similarity. Returns 0.0 if either vector is zero-norm."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def min_pairwise_similarity(vecs: Sequence[Sequence[float]]) -> float:
    """Minimum cosine similarity across all unique pairs in vecs."""
    pairs = itertools.combinations(vecs, 2)
    sims = [cosine_similarity(a, b) for a, b in pairs]
    return min(sims) if sims else 0.0


def rank_triples(
    domain_to_atoms: dict[str, list[Atom]],
    embeddings: dict[str, list[float]],
) -> list[tuple[float, tuple[Atom, Atom, Atom]]]:
    """Enumerate every (domain-triple x atom-per-domain) combination.

    Returns (min_pairwise_similarity, atom_triple) tuples sorted descending
    by score, with deterministic tiebreak by sorted slug tuple ascending.
    """
    domains = sorted(domain_to_atoms.keys())
    results: list[tuple[float, tuple[Atom, Atom, Atom]]] = []

    for d_triple in itertools.combinations(domains, 3):
        atom_lists = [domain_to_atoms[d] for d in d_triple]
        for atom_triple in itertools.product(*atom_lists):
            vecs = [embeddings[a.slug] for a in atom_triple]
            score = min_pairwise_similarity(vecs)
            results.append((score, atom_triple))

    results.sort(key=lambda r: (-r[0], tuple(sorted(a.slug for a in r[1]))))
    return results
