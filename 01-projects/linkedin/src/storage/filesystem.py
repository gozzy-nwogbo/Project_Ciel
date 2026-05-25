"""Filesystem-backed storage adapter (v1.0)."""
from __future__ import annotations

import json
from pathlib import Path

from models import PostBrief, Status, utc_now


class FilesystemAdapter:
    def __init__(self, project_root: Path):
        self.root = Path(project_root)
        self.backlog = self.root / "backlog"
        self.backlog.mkdir(parents=True, exist_ok=True)

    def _bundle_dir(self, slug: str) -> Path:
        return self.backlog / slug

    def write(self, brief: PostBrief) -> None:
        bundle = self._bundle_dir(brief.slug)
        bundle.mkdir(parents=True, exist_ok=True)
        (bundle / "meta.json").write_text(
            json.dumps(brief.to_dict(), indent=2, default=str)
        )
        text = brief.approved_text or brief.draft_text or ""
        (bundle / "text.md").write_text(text + ("\n" if text and not text.endswith("\n") else ""))

    def read(self, slug: str) -> PostBrief:
        bundle = self._bundle_dir(slug)
        meta = json.loads((bundle / "meta.json").read_text())
        return PostBrief.from_dict(meta)

    def list_slugs(self) -> list[str]:
        return sorted([p.name for p in self.backlog.iterdir() if p.is_dir()])

    def update_status(self, slug: str, new_status: Status, actor: str = "user") -> PostBrief:
        brief = self.read(slug)
        brief.status = new_status
        brief.updated_at = utc_now()
        brief.status_history.append({
            "status": new_status.value,
            "timestamp": brief.updated_at.isoformat(),
            "actor": actor,
        })
        self.write(brief)
        return brief

    def delete(self, slug: str) -> None:
        bundle = self._bundle_dir(slug)
        if bundle.exists():
            for child in bundle.iterdir():
                child.unlink()
            bundle.rmdir()
