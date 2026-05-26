"""Core data models for the LinkedIn engine."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class Status(str, Enum):
    DRAFTING = "drafting"
    TEXT_READY = "text_ready"
    GATE1_APPROVED = "gate1_approved"
    RENDERING = "rendering"
    GATE2_PENDING = "gate2_pending"
    READY_TO_POST = "ready_to_post"
    POSTED = "posted"
    REJECTED = "rejected"
    ARCHIVED = "archived"


@dataclass
class AtomRef:
    slug: str
    role: str  # "primary" | "auxiliary"
    source: Optional[str] = None


@dataclass
class TextConstraints:
    voice_rules: list[str] = field(default_factory=list)
    word_range: tuple[int, int] = (80, 200)


@dataclass
class PostBrief:
    id: str
    slug: str
    created_at: datetime
    updated_at: datetime
    strategy: str
    strategy_params: dict[str, Any]
    atoms_used: list[AtomRef]
    angle: str
    visual_tier: str  # "1_diagram" | "2_carousel" | "3_video"
    status: Status
    text_constraints: TextConstraints = field(default_factory=TextConstraints)
    draft_text: str = ""
    approved_text: str = ""
    thesis: str = ""
    aspect_ratio: str = "1:1"
    panel_label: str = ""
    panel_claim: str = ""
    edit_delta: Optional[dict[str, Any]] = None
    visual_brief: dict[str, Any] = field(default_factory=dict)
    visual_asset_paths: list[str] = field(default_factory=list)
    series: Optional[str] = None
    topic_tags: list[str] = field(default_factory=list)
    target_platforms: list[str] = field(default_factory=lambda: ["linkedin_profile"])
    status_history: list[dict[str, Any]] = field(default_factory=list)
    # v2 fields, nullable in v1
    scheduled_time: Optional[datetime] = None
    scheduler_platform: Optional[str] = None
    scheduler_post_id: Optional[str] = None
    published_url: Optional[str] = None
    metrics: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["created_at"] = self.created_at.isoformat()
        d["updated_at"] = self.updated_at.isoformat()
        if self.scheduled_time:
            d["scheduled_time"] = self.scheduled_time.isoformat()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PostBrief":
        atoms = [AtomRef(**a) for a in d.get("atoms_used", [])]
        constraints = TextConstraints(**d.get("text_constraints", {}))
        return cls(
            id=d["id"],
            slug=d["slug"],
            created_at=datetime.fromisoformat(d["created_at"]),
            updated_at=datetime.fromisoformat(d["updated_at"]),
            strategy=d["strategy"],
            strategy_params=d.get("strategy_params", {}),
            atoms_used=atoms,
            angle=d.get("angle", ""),
            visual_tier=d.get("visual_tier", "1_diagram"),
            status=Status(d["status"]),
            text_constraints=constraints,
            draft_text=d.get("draft_text", ""),
            approved_text=d.get("approved_text", ""),
            thesis=d.get("thesis", ""),
            aspect_ratio=d.get("aspect_ratio", "1:1"),
            panel_label=d.get("panel_label", ""),
            panel_claim=d.get("panel_claim", ""),
            edit_delta=d.get("edit_delta"),
            visual_brief=d.get("visual_brief", {}),
            visual_asset_paths=d.get("visual_asset_paths", []),
            series=d.get("series"),
            topic_tags=d.get("topic_tags", []),
            target_platforms=d.get("target_platforms", ["linkedin_profile"]),
            status_history=d.get("status_history", []),
            scheduled_time=datetime.fromisoformat(d["scheduled_time"]) if d.get("scheduled_time") else None,
            scheduler_platform=d.get("scheduler_platform"),
            scheduler_post_id=d.get("scheduler_post_id"),
            published_url=d.get("published_url"),
            metrics=d.get("metrics"),
        )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
