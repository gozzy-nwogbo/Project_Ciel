"""JSONL append-only state transition log."""
from __future__ import annotations

import json
from pathlib import Path

from models import utc_now


class StateLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, slug: str, from_status: str, to_status: str, actor: str = "user", note: str = "") -> None:
        entry = {
            "timestamp": utc_now().isoformat(),
            "slug": slug,
            "from_status": from_status,
            "to_status": to_status,
            "actor": actor,
            "note": note,
        }
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
