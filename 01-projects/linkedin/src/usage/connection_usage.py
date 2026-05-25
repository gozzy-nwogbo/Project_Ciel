"""Connection edge cooldown tracking."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


def _edge_key(a: str, b: str) -> str:
    return "|".join(sorted([a, b]))


class ConnectionUsageTracker:
    def __init__(self, path: Path, cooldown_days: int = 60):
        self.path = Path(path)
        self.cooldown = timedelta(days=cooldown_days)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}")

    def _load(self) -> dict:
        return json.loads(self.path.read_text())

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def mark_used(self, atom_a: str, atom_b: str, post_id: str, at: Optional[datetime] = None) -> None:
        data = self._load()
        key = _edge_key(atom_a, atom_b)
        history = data.setdefault(key, [])
        history.append({"post_id": post_id, "at": (at or datetime.now(timezone.utc)).isoformat()})
        self._save(data)

    def is_in_cooldown(self, atom_a: str, atom_b: str) -> bool:
        data = self._load()
        key = _edge_key(atom_a, atom_b)
        history = data.get(key, [])
        if not history:
            return False
        now = datetime.now(timezone.utc)
        return any(now - datetime.fromisoformat(e["at"]) < self.cooldown for e in history)
