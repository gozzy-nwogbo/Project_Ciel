import json
from unittest.mock import MagicMock, patch

from cli.draft_post import main


def test_main_invokes_strategy_writes_bundle(atom_source, project_root, brand_spec, monkeypatch):
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Generated post body. " * 30)]
    )

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic):
        exit_code = main([
            "--strategy=two_atom_bridge",
            "--atom-a=sample-concept",
            "--atom-b=third-concept",
            "--no-render",
        ])

    assert exit_code == 0
    backlog = project_root / "backlog"
    assert any(p.is_dir() for p in backlog.iterdir())
    bundle = next(p for p in backlog.iterdir() if p.is_dir())
    meta = json.loads((bundle / "meta.json").read_text())
    assert meta["strategy"] == "two_atom_bridge"
    assert meta["status"] in ("text_ready", "drafting")
