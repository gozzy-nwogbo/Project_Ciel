"""Source registry — maps atom source slugs to source-type metadata."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass(frozen=True)
class SourceEntry:
    type: str                       # "book" | "video" | "podcast" | "post"
    author_bio: Optional[str] = None
    work: Optional[str] = None


class SourcesRegistry:
    """Reads sources.yml. Lookups by source slug return SourceEntry or None."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._entries: dict[str, SourceEntry] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open() as f:
            raw = yaml.safe_load(f) or {}
        for key, value in raw.items():
            if not isinstance(value, dict) or "type" not in value:
                continue
            self._entries[key] = SourceEntry(
                type=value["type"],
                author_bio=value.get("author_bio"),
                work=value.get("work"),
            )

    def lookup(self, source: str) -> Optional[SourceEntry]:
        return self._entries.get(source)
