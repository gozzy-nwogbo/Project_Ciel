from datetime import datetime, timezone
from pathlib import Path

from models import AtomRef, PostBrief, Status
from storage.filesystem import FilesystemAdapter


def _make_brief() -> PostBrief:
    now = datetime.now(timezone.utc)
    return PostBrief(
        id="brief-1",
        slug="2026-05-24-test-bridge",
        created_at=now,
        updated_at=now,
        strategy="two_atom_bridge",
        strategy_params={"atom_a": "sample-concept", "atom_b": "another-concept"},
        atoms_used=[
            AtomRef(slug="sample-concept", role="primary"),
            AtomRef(slug="another-concept", role="primary"),
        ],
        angle="Two atoms walk into a bridge.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
        draft_text="Draft body text.",
    )


def test_write_then_read(project_root: Path):
    adapter = FilesystemAdapter(project_root)
    brief = _make_brief()
    adapter.write(brief)
    loaded = adapter.read("2026-05-24-test-bridge")
    assert loaded.slug == brief.slug
    assert loaded.angle == brief.angle


def test_write_creates_text_md(project_root: Path):
    adapter = FilesystemAdapter(project_root)
    brief = _make_brief()
    adapter.write(brief)
    bundle = project_root / "backlog" / "2026-05-24-test-bridge"
    assert (bundle / "meta.json").exists()
    assert (bundle / "text.md").exists()
    assert "Draft body text" in (bundle / "text.md").read_text()


def test_list_returns_all(project_root: Path):
    adapter = FilesystemAdapter(project_root)
    adapter.write(_make_brief())
    slugs = adapter.list_slugs()
    assert "2026-05-24-test-bridge" in slugs
