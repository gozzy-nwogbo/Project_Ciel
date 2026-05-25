"""Append-only rejection log."""
from __future__ import annotations

import json
from pathlib import Path

from models import utc_now


class RejectionLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        post_id: str,
        atoms_used: list[str],
        strategy: str,
        angle: str,
        draft_text: str,
        reason: str = "",
        signal: str = "killed_by_user",
    ) -> None:
        entry = {
            "post_id": post_id,
            "rejected_at": utc_now().isoformat(),
            "atoms_used": atoms_used,
            "strategy": strategy,
            "angle": angle,
            "draft_text": draft_text,
            "rejection_reason": reason,
            "rejection_signal": signal,
        }
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
