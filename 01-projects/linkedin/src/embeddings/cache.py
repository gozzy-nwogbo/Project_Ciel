"""Persistent embedding cache with hash-based invalidation."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Protocol


class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class EmbeddingCache:
    """JSON-on-disk cache: {slug: {body_hash, embedding}}."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._data: dict[str, dict] = {}
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def get_or_embed(self, slug: str, text: str, embedder: Embedder) -> list[float]:
        h = _hash(text)
        entry = self._data.get(slug)
        if entry and entry.get("body_hash") == h:
            return list(entry["embedding"])

        vec = embedder.embed(text)
        self._data[slug] = {"body_hash": h, "embedding": vec}
        self._save()
        return vec

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(self._data, f)
            os.replace(tmp_path, self.path)
        except Exception:
            tmp = Path(tmp_path)
            if tmp.exists():
                tmp.unlink()
            raise
