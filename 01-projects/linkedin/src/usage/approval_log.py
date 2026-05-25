"""Append-only approval log with edit_delta computation."""
from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Optional

from models import utc_now


def _classify_magnitude(diff_ratio: float) -> str:
    if diff_ratio < 0.10:
        return "minor"
    if diff_ratio < 0.40:
        return "moderate"
    return "major"


def compute_edit_delta(draft: str, approved: str) -> dict:
    diff = "\n".join(difflib.unified_diff(
        draft.splitlines(),
        approved.splitlines(),
        lineterm="",
        fromfile="draft",
        tofile="approved",
    ))
    matcher = difflib.SequenceMatcher(None, draft, approved)
    distance = 1.0 - matcher.ratio()
    return {
        "diff": diff,
        "magnitude": _classify_magnitude(distance),
        "ratio": distance,
    }


class ApprovalLog:
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
        approved_text: str,
        approved_visual_tier: int,
        tier_changed_at_gate1: bool = False,
        posted_at: Optional[str] = None,
    ) -> None:
        entry = {
            "post_id": post_id,
            "approved_at": utc_now().isoformat(),
            "atoms_used": atoms_used,
            "strategy": strategy,
            "angle": angle,
            "draft_text": draft_text,
            "approved_text": approved_text,
            "edit_delta": compute_edit_delta(draft_text, approved_text),
            "approved_visual_tier": approved_visual_tier,
            "tier_changed_at_gate1": tier_changed_at_gate1,
            "posted_at": posted_at,
            "performance": None,
        }
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
