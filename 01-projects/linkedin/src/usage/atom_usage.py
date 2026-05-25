"""Atom cooldown tracking."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


class AtomUsageTracker:
    def __init__(self, path: Path, cooldown_days_primary: int = 30, cooldown_days_auxiliary: int = 7):
        self.path = Path(path)
        self.cooldown_primary = timedelta(days=cooldown_days_primary)
        self.cooldown_aux = timedelta(days=cooldown_days_auxiliary)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}")

    def _load(self) -> dict:
        return json.loads(self.path.read_text())

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def mark_used(self, atom_slug: str, role: str, post_id: str, at: Optional[datetime] = None) -> None:
        data = self._load()
        history = data.setdefault(atom_slug, [])
        history.append({
            "post_id": post_id,
            "role": role,
            "at": (at or datetime.now(timezone.utc)).isoformat(),
        })
        self._save(data)

    def is_in_cooldown(self, atom_slug: str, role: str) -> bool:
        data = self._load()
        history = data.get(atom_slug, [])
        if not history:
            return False
        cooldown = self.cooldown_primary if role == "primary" else self.cooldown_aux
        now = datetime.now(timezone.utc)
        for entry in history:
            if entry["role"] != role:
                continue
            entry_time = datetime.fromisoformat(entry["at"])
            if now - entry_time < cooldown:
                return True
        return False
