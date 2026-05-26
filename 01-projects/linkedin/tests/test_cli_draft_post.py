import json
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from cli.draft_post import main


def _write_minimal_brief(project_root, strategy="two_atom_bridge", visual_tier="1_diagram"):
    """Write a minimal bundle to disk and return the slug."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from models import AtomRef, PostBrief, Status
    from storage.filesystem import FilesystemAdapter

    slug = f"test-{strategy}-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id=str(uuid.uuid4()),
        slug=slug,
        created_at=now,
        updated_at=now,
        strategy=strategy,
        strategy_params={},
        atoms_used=[
            AtomRef(slug="sample-concept", role="primary"),
            AtomRef(slug="third-concept", role="auxiliary"),
        ],
        angle="Test angle for registry dispatch.",
        visual_tier=visual_tier,
        status=Status.TEXT_READY,
        draft_text="This post tests registry dispatch in the CLI. " * 5,
    )
    storage = FilesystemAdapter(project_root)
    storage.write(brief)

    text_path = project_root / "backlog" / slug / "text.md"
    text_path.write_text(brief.draft_text)

    return slug


def test_advance_uses_registry_for_strategy(monkeypatch, tmp_path, brand_spec):
    """_advance must call renderers.registry.for_strategy(brief.strategy, ...) instead of hardcoding AtomCardRenderer."""
    import shutil
    from pathlib import Path

    from cli import draft_post
    from renderers import registry as renderers_registry

    FIXTURES_DIR = Path(__file__).parent / "fixtures"
    atom_source = tmp_path / "atoms"
    shutil.copytree(FIXTURES_DIR / "atoms", atom_source)

    project_root = tmp_path / "project"
    for sub in ("state", "backlog", "logs"):
        (project_root / sub).mkdir(parents=True)

    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    slug = _write_minimal_brief(project_root, strategy="two_atom_bridge", visual_tier="1_diagram")

    seen: dict = {}

    def fake_for_strategy(strategy_name, **kwargs):
        seen["strategy"] = strategy_name

        class StubRenderer:
            def validate(self, brief):
                return []

            def render(self, brief, out_dir):
                from renderers.base import RenderResult
                out_dir.mkdir(parents=True, exist_ok=True)
                png = out_dir / "diagram.png"
                png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)
                return RenderResult(asset_paths=[png], cost=0.0, duration_s=0.0, logs=[])

        return StubRenderer()

    monkeypatch.setattr(renderers_registry, "for_strategy", fake_for_strategy)

    exit_code = main(["--advance", slug, "--force"])

    assert exit_code == 0
    assert seen.get("strategy") == "two_atom_bridge"


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
