from unittest.mock import MagicMock

from atom_loader import AtomLoader
from models import AtomRef, PostBrief, Status, utc_now
from text_generator import TextGenerator


def _brief() -> PostBrief:
    now = utc_now()
    return PostBrief(
        id="b1",
        slug="2026-05-24-x",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={"source": "test-fixture"},
        atoms_used=[AtomRef(slug="sample-concept", role="primary")],
        angle="Three ideas all touch storytelling.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )


def test_generates_text(atom_source, mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Drafted post body. Word word word " * 30)]
    )
    loader = AtomLoader(atom_source)
    gen = TextGenerator(client=mock_client, loader=loader)
    brief = _brief()
    out = gen.generate(brief)
    assert "Drafted" in out.draft_text
    assert out.status.value == "text_ready"


def test_voice_rules_in_system_prompt(atom_source, mocker):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(
        content=[MagicMock(text="body " * 100)]
    )
    loader = AtomLoader(atom_source)
    gen = TextGenerator(client=mock_client, loader=loader)
    gen.generate(_brief())
    call_kwargs = mock_client.messages.create.call_args.kwargs
    system = call_kwargs.get("system", "")
    assert "em-dash" in system.lower() or "no em" in system.lower()
    assert "contrastive" in system.lower() or "not as x" in system.lower()
