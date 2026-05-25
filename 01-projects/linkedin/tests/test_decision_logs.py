import json
from pathlib import Path

from usage.approval_log import ApprovalLog
from usage.rejection_log import RejectionLog


def test_rejection_log(project_root: Path):
    log = RejectionLog(project_root / "state" / "rejections.jsonl")
    log.record(
        post_id="p1",
        atoms_used=["a", "b"],
        strategy="two_atom_bridge",
        angle="...",
        draft_text="draft",
        reason="angle too abstract",
        signal="killed_by_user",
    )
    lines = (project_root / "state" / "rejections.jsonl").read_text().strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["rejection_signal"] == "killed_by_user"


def test_approval_log_with_delta(project_root: Path):
    log = ApprovalLog(project_root / "state" / "approvals.jsonl")
    log.record(
        post_id="p2",
        atoms_used=["a", "b"],
        strategy="source_spotlight",
        angle="...",
        draft_text="draft body",
        approved_text="draft body. extra.",
        approved_visual_tier=1,
        tier_changed_at_gate1=False,
    )
    entry = json.loads((project_root / "state" / "approvals.jsonl").read_text().strip())
    assert entry["edit_delta"]["magnitude"] in {"minor", "moderate", "major"}
    assert "diff" in entry["edit_delta"]
