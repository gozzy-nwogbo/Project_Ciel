import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cli.draft_post import main as draft_post_main
from models import Status
from storage.filesystem import FilesystemAdapter


def test_full_pipeline_two_atom_bridge(atom_source, project_root, brand_spec, monkeypatch):
    """End-to-end: generate two_atom_bridge draft, advance through Gate 1, render diagram, mark posted."""
    pytest.importorskip("playwright.sync_api")
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text=(
            "Built a small engine this week that picks two atoms from my second brain "
            "and asks where they overlap. <THESIS>Same gear runs in different machines.</THESIS> "
            "Surfaced a tie between feedback loops in auth design and feedback loops in pedagogy. "
            "Wondering what other domains the same gear runs in. " * 2
        ))]
    )

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic), \
         patch("anthropic.Anthropic", return_value=mock_anthropic):
        # 1. Generate
        rc = draft_post_main([
            "--strategy=two_atom_bridge",
            "--atom-a=sample-concept",
            "--atom-b=third-concept",
        ])
        assert rc == 0

        # 2. Identify the bundle
        storage = FilesystemAdapter(project_root)
        slugs = storage.list_slugs()
        bundle_slug = next(s for s in slugs if "bridge" in s)
        brief = storage.read(bundle_slug)
        assert brief.status is Status.TEXT_READY
        assert (project_root / "backlog" / bundle_slug / "text.md").exists()

        # 3. Advance through Gate 1.
        # v1.2: two_atom_bridge defaults to 1_diagram at 4:5, so a PNG is
        # rendered during advancement and visual_asset_paths is populated.
        rc = draft_post_main(["--advance", bundle_slug])
        assert rc == 0

        brief = storage.read(bundle_slug)
        assert brief.status is Status.GATE2_PENDING
        assert len(brief.visual_asset_paths) == 1
        assert brief.aspect_ratio == "4:5"
        assert brief.panel_label in {
            "SHARED MECHANISM", "STRUCTURAL ANALOGUE", "INVERSE PAIR", "BRIDGE",
        }

        # 4. Approvals log has an entry with edit_delta
        approvals_path = project_root / "state" / "approvals.jsonl"
        assert approvals_path.exists()
        entry = json.loads(approvals_path.read_text().strip())
        assert entry["edit_delta"]["magnitude"] in {"minor", "moderate", "major"}

        # 5. Atom usage tracker registered the atoms
        atom_usage = json.loads((project_root / "state" / "atom-usage.json").read_text())
        assert "sample-concept" in atom_usage
        assert "third-concept" in atom_usage

        # 6. Mark posted
        rc = draft_post_main(["--mark-posted", bundle_slug, "--url=https://linkedin.com/posts/x"])
        assert rc == 0
        brief = storage.read(bundle_slug)
        assert brief.status is Status.POSTED
        assert brief.published_url == "https://linkedin.com/posts/x"


def test_full_pipeline_convergence_finder(atom_source, project_root, brand_spec, monkeypatch):
    """End-to-end: generate convergence_finder draft for 'decision making', advance through Gate 1, render diagram."""
    pytest.importorskip("playwright.sync_api")
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    # Fixture corpus has three 'decision making' atoms across design, engineering, and leadership domains.
    topic = "decision making"

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text=(
            "Pulled three atoms from my second brain this week, all tagged decision making. "
            "<THESIS>Same constraint, three different masks.</THESIS> "
            "Design calls it satisficing. Engineering calls it good-enough architecture. "
            "Leadership calls it bounded rationality. "
            "<CLAIM>Every field rediscovered that perfect is the enemy of shipped.</CLAIM> "
            "Wondering what the fourth domain looks like. " * 2
        ))]
    )

    class _ConstantEmbedder:
        def embed(self, text):
            return [1.0, 0.0, 0.0]

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic), \
         patch("cli.draft_post._make_embedder", return_value=_ConstantEmbedder()), \
         patch("anthropic.Anthropic", return_value=mock_anthropic):
        # 1. Generate
        rc = draft_post_main([
            "--strategy=convergence_finder",
            f"--topic={topic}",
        ])
        assert rc == 0

        # 2. Identify the bundle
        storage = FilesystemAdapter(project_root)
        slugs = storage.list_slugs()
        bundle_slug = next(s for s in slugs if "convergence" in s)
        brief = storage.read(bundle_slug)
        assert brief.status is Status.TEXT_READY
        assert (project_root / "backlog" / bundle_slug / "text.md").exists()

        # Brief must reference atoms from at least 3 distinct domains.
        assert len(brief.atoms_used) >= 3

        # 3. Advance through Gate 1.
        # convergence_finder defaults to 1_diagram at 4:5, so a PNG is rendered
        # during advancement and visual_asset_paths is populated.
        rc = draft_post_main(["--advance", bundle_slug])
        assert rc == 0

        brief = storage.read(bundle_slug)
        assert brief.status is Status.GATE2_PENDING
        assert brief.visual_tier == "1_diagram"
        assert brief.aspect_ratio == "4:5"
        assert brief.panel_label.startswith("CONVERGES ON · ")
        assert topic.upper() in brief.panel_label
        assert len(brief.visual_asset_paths) == 1
        assert brief.visual_asset_paths[0].endswith(".png")


def test_kill_flow(atom_source, project_root, brand_spec, monkeypatch):
    """Kill flow: generate, reject, verify rejection log + status."""
    monkeypatch.setenv("LINKEDIN_ATOM_SOURCE", str(atom_source))
    monkeypatch.setenv("LINKEDIN_PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("LINKEDIN_BRAND_SPEC", str(brand_spec))

    mock_anthropic = MagicMock()
    mock_anthropic.messages.create.return_value = MagicMock(
        content=[MagicMock(text="text " * 100)]
    )

    with patch("cli.draft_post._make_anthropic_client", return_value=mock_anthropic):
        draft_post_main([
            "--strategy=two_atom_bridge",
            "--atom-a=sample-concept",
            "--atom-b=third-concept",
        ])
        storage = FilesystemAdapter(project_root)
        slug = next(s for s in storage.list_slugs() if "bridge" in s)

        rc = draft_post_main(["--kill", slug, "--reason=angle felt too generic"])
        assert rc == 0

        brief = storage.read(slug)
        assert brief.status is Status.REJECTED

        rejections = (project_root / "state" / "rejections.jsonl").read_text().strip().splitlines()
        assert any("generic" in json.loads(line)["rejection_reason"] for line in rejections)
