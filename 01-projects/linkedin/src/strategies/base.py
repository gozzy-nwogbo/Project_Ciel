"""Strategy base — interface + shared helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from atom_loader import Atom, AtomLoader
from connection_graph import ConnectionGraph
from models import PostBrief
from usage.atom_usage import AtomUsageTracker
from usage.connection_usage import ConnectionUsageTracker


@dataclass
class StrategyContext:
    loader: AtomLoader
    graph: ConnectionGraph
    atom_tracker: AtomUsageTracker
    connection_tracker: ConnectionUsageTracker | None = None


class Strategy(Protocol):
    name: str
    def generate_brief(self, ctx: StrategyContext, params: dict) -> PostBrief: ...


def eligible_atoms(atoms: Iterable[Atom], tracker: AtomUsageTracker, role: str) -> list[Atom]:
    return [
        a for a in atoms
        if a.type != "connection" and not tracker.is_in_cooldown(a.slug, role=role)
    ]


def domains(atoms: Iterable[Atom]) -> set[str]:
    """Return the set of domain tags across a group of atoms."""
    result: set[str] = set()
    for a in atoms:
        if a.domain:
            result.add(a.domain)
        for tag in a.tags:
            result.add(tag)
    return result
