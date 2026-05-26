"""Load atoms (concepts, frameworks, principles, connections) from a vault directory."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import frontmatter


@dataclass
class Atom:
    slug: str               # filename stem (kebab-case)
    title: str
    type: str               # "concept" | "framework" | "principle" | "connection"
    source_date: str
    body: str
    tags: list[str] = field(default_factory=list)
    domain: Optional[str] = None
    origin: Optional[str] = None
    source: Optional[str] = None
    tldr: Optional[str] = None
    path: Optional[Path] = None
    # connection-specific
    from_atom: Optional[str] = None
    to_atom: Optional[str] = None
    connection_type: str = "general"


class AtomLoader:
    """Reads atom markdown files from a directory tree."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def load_all(self) -> list[Atom]:
        atoms: list[Atom] = []
        for path in self.root.rglob("*.md"):
            try:
                atom = self._parse(path)
                if atom:
                    atoms.append(atom)
            except Exception:
                continue
        return atoms

    def load_by_source(self, source: str) -> list[Atom]:
        return [a for a in self.load_all() if a.origin == source or a.source == source]

    def load_by_tag(self, tag: str) -> list[Atom]:
        return [a for a in self.load_all() if tag in a.tags]

    def load_one(self, slug: str) -> Optional[Atom]:
        return next((a for a in self.load_all() if a.slug == slug), None)

    def _parse(self, path: Path) -> Optional[Atom]:
        post = frontmatter.load(path)
        meta = post.metadata
        if "title" not in meta or "type" not in meta:
            return None
        return Atom(
            slug=path.stem,
            title=meta["title"],
            type=meta["type"],
            source_date=str(meta.get("source_date", "")),
            body=post.content,
            tags=list(meta.get("tags", []) or []),
            domain=meta.get("domain"),
            origin=meta.get("origin"),
            source=meta.get("source"),
            tldr=meta.get("tldr"),
            path=path,
            from_atom=meta.get("from"),
            to_atom=meta.get("to"),
            connection_type=meta.get("connection_type", "general"),
        )
