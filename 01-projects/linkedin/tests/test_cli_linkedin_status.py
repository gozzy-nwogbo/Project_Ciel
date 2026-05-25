from cli.linkedin_status import main
from models import AtomRef, PostBrief, Status, utc_now
from storage.filesystem import FilesystemAdapter


def test_backlog_lists_pending(project_root, monkeypatch, capsys):
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    storage = FilesystemAdapter(project_root)
    now = utc_now()
    brief = PostBrief(
        id="b1", slug="2026-05-24-pending",
        created_at=now, updated_at=now,
        strategy="source_spotlight", strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary")],
        angle="x", visual_tier="1_diagram",
        status=Status.TEXT_READY, draft_text="text",
    )
    storage.write(brief)
    exit_code = main(["--backlog"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "2026-05-24-pending" in out
    assert "text_ready" in out
