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
