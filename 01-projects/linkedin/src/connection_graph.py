"""Build a connection graph from loaded atoms."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from atom_loader import Atom


@dataclass
class Edge:
    from_slug: str
    to_slug: str
    from_title: str
    to_title: str
    connection_type: str
    claim: str               # body of the connection atom


def _slugify(title: str) -> str:
    return title.lower().replace(" ", "-")


class ConnectionGraph:
    def __init__(self, atoms: Iterable[Atom]):
        atoms_list = list(atoms)
        self._title_to_slug = {a.title: a.slug for a in atoms_list if a.type != "connection"}
        self._slug_to_atom = {a.slug: a for a in atoms_list if a.type != "connection"}
        self.edges: list[Edge] = []
        for a in atoms_list:
            if a.type != "connection" or not (a.from_atom and a.to_atom):
                continue
            from_slug = self._title_to_slug.get(a.from_atom) or _slugify(a.from_atom)
            to_slug = self._title_to_slug.get(a.to_atom) or _slugify(a.to_atom)
            self.edges.append(Edge(
                from_slug=from_slug,
                to_slug=to_slug,
                from_title=a.from_atom,
                to_title=a.to_atom,
                connection_type=a.connection_type,
                claim=a.body.strip(),
            ))

    def edges_for(self, slug: str) -> list[Edge]:
        return [e for e in self.edges if e.from_slug == slug or e.to_slug == slug]

    def edges_by_type(self, connection_type: str) -> list[Edge]:
        return [e for e in self.edges if e.connection_type == connection_type]

    def neighbors(self, slug: str) -> list[str]:
        result: set[str] = set()
        for e in self.edges_for(slug):
            other = e.to_slug if e.from_slug == slug else e.from_slug
            result.add(other)
        return sorted(result)
