import json
from datetime import datetime, timezone

from models import PostBrief, AtomRef, Status


def test_postbrief_roundtrip():
    brief = PostBrief(
        id="abc-123",
        slug="2026-05-24-sample",
        created_at=datetime(2026, 5, 24, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 24, tzinfo=timezone.utc),
        strategy="source_spotlight",
        strategy_params={"source": "Nate B. Jones", "atom_count": 3},
        atoms_used=[AtomRef(slug="x", role="primary", source="Nate B. Jones")],
        angle="Three ideas from X all touch Y.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    payload = brief.to_dict()
    restored = PostBrief.from_dict(payload)
    assert restored.slug == "2026-05-24-sample"
    assert restored.atoms_used[0].slug == "x"
    assert restored.status is Status.DRAFTING
    encoded = json.dumps(payload, default=str)
    decoded = json.loads(encoded)
    assert decoded["strategy"] == "source_spotlight"


def test_post_brief_round_trip_includes_thesis():
    """PostBrief.thesis is preserved across to_dict / from_dict round-trip."""
    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id="b1",
        slug="2026-05-25-thesis-test",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug="atom-a", role="primary")],
        angle="An angle.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        thesis="Strategy is problem-shaped, not goal-shaped.",
    )
    d = brief.to_dict()
    assert d["thesis"] == "Strategy is problem-shaped, not goal-shaped."
    restored = PostBrief.from_dict(d)
    assert restored.thesis == "Strategy is problem-shaped, not goal-shaped."


def test_post_brief_thesis_defaults_empty():
    """PostBrief.thesis defaults to empty string when not provided."""
    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id="b2",
        slug="x",
        created_at=now,
        updated_at=now,
        strategy="x",
        strategy_params={},
        atoms_used=[],
        angle="",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    assert brief.thesis == ""


def test_postbrief_v12_fields_roundtrip():
    """v1.2 adds aspect_ratio, panel_label, panel_claim. Round-trip through to_dict / from_dict."""
    from datetime import datetime, timezone
    from models import AtomRef, PostBrief, Status

    now = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)
    brief = PostBrief(
        id="t",
        slug="t",
        created_at=now,
        updated_at=now,
        strategy="two_atom_bridge",
        strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary")],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        aspect_ratio="4:5",
        panel_label="SHARED MECHANISM",
        panel_claim="Both systems run the same loop.",
    )
    d = brief.to_dict()
    assert d["aspect_ratio"] == "4:5"
    assert d["panel_label"] == "SHARED MECHANISM"
    assert d["panel_claim"] == "Both systems run the same loop."

    rt = PostBrief.from_dict(d)
    assert rt.aspect_ratio == "4:5"
    assert rt.panel_label == "SHARED MECHANISM"
    assert rt.panel_claim == "Both systems run the same loop."


def test_postbrief_v12_defaults_when_missing():
    """Briefs serialized before v1.2 deserialize with safe defaults."""
    from datetime import datetime, timezone
    from models import PostBrief, Status

    d = {
        "id": "t",
        "slug": "t",
        "created_at": datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "updated_at": datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
        "strategy": "source_spotlight",
        "strategy_params": {},
        "atoms_used": [],
        "angle": "x",
        "visual_tier": "1_diagram",
        "status": "drafting",
    }
    rt = PostBrief.from_dict(d)
    assert rt.aspect_ratio == "1:1"
    assert rt.panel_label == ""
    assert rt.panel_claim == ""
