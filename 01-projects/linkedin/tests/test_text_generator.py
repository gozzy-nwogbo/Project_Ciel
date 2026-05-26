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
    # Cold-reader anchor rule: the prompt must require inline definitions
    # for unfamiliar concepts. Surfaced in the v1.0 smoke (2026-05-25).
    assert "anchor" in system.lower() or "first time" in system.lower() or "cold reader" in system.lower()


def test_voice_prompt_v2_thesis_requirement():
    """System prompt requires exactly one <THESIS>...</THESIS> block."""
    from text_generator import VOICE_SYSTEM_PROMPT
    assert "<THESIS>" in VOICE_SYSTEM_PROMPT
    assert "</THESIS>" in VOICE_SYSTEM_PROMPT
    assert "exactly one" in VOICE_SYSTEM_PROMPT.lower()


def test_voice_prompt_v2_source_type_aware_anchor():
    """COLD READER ANCHOR rule mentions source type differentiation."""
    from text_generator import VOICE_SYSTEM_PROMPT
    assert "book" in VOICE_SYSTEM_PROMPT.lower()
    assert "video" in VOICE_SYSTEM_PROMPT.lower() or "podcast" in VOICE_SYSTEM_PROMPT.lower()
    assert "author_bio" in VOICE_SYSTEM_PROMPT or "bio" in VOICE_SYSTEM_PROMPT.lower()


def test_generate_extracts_thesis_and_strips_tags(tmp_path):
    """generate() populates brief.thesis and strips tags from draft_text."""
    from datetime import datetime, timezone
    from unittest.mock import MagicMock

    from atom_loader import AtomLoader
    from models import AtomRef, PostBrief, Status
    from text_generator import TextGenerator

    atom_file = tmp_path / "atom-a.md"
    atom_file.write_text(
        "---\ntitle: Atom A\ntype: concept\nsource: Test, 2026\ndomain: test\ntags: []\n---\n\nBody.\n"
    )

    loader = AtomLoader(tmp_path)

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text=(
        "Opening line.\n\n"
        "<THESIS>The locked thesis sentence.</THESIS>\n\n"
        "Closing line."
    ))]
    fake_client.messages.create.return_value = fake_response

    now = datetime.now(timezone.utc)
    brief = PostBrief(
        id="b1",
        slug="thesis-extract-test",
        created_at=now,
        updated_at=now,
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug="atom-a", role="primary")],
        angle="An angle.",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )

    gen = TextGenerator(client=fake_client, loader=loader)
    result = gen.generate(brief)

    assert result.thesis == "The locked thesis sentence."
    assert "<THESIS>" not in result.draft_text
    assert "</THESIS>" not in result.draft_text
    assert "The locked thesis sentence." in result.draft_text


def test_voice_prompt_does_not_include_claim_rule_for_source_spotlight():
    """source_spotlight posts should not see the CLAIM rule."""
    from text_generator import CLAIM_TAG_RULE, _compose_system_prompt

    prompt = _compose_system_prompt(strategy="source_spotlight")
    assert CLAIM_TAG_RULE not in prompt


def test_voice_prompt_includes_claim_rule_for_two_atom_bridge():
    from text_generator import CLAIM_TAG_RULE, _compose_system_prompt

    prompt = _compose_system_prompt(strategy="two_atom_bridge")
    assert CLAIM_TAG_RULE in prompt


def test_voice_prompt_includes_claim_rule_for_convergence_finder():
    from text_generator import CLAIM_TAG_RULE, _compose_system_prompt

    prompt = _compose_system_prompt(strategy="convergence_finder")
    assert CLAIM_TAG_RULE in prompt


def test_claim_tag_rule_mentions_band_and_panel():
    """The rule must explain where the claim renders so the model gets the right tone."""
    from text_generator import CLAIM_TAG_RULE

    assert "<CLAIM>" in CLAIM_TAG_RULE
    assert "</CLAIM>" in CLAIM_TAG_RULE
    assert "two_atom_bridge" in CLAIM_TAG_RULE
    assert "convergence_finder" in CLAIM_TAG_RULE
    assert "mechanism" in CLAIM_TAG_RULE.lower()
    assert "exactly one" in CLAIM_TAG_RULE.lower()


def test_generate_extracts_claim_for_bridge(tmp_path):
    """generate() must populate brief.panel_claim from <CLAIM> for bridge posts."""
    from atom_loader import AtomLoader
    from models import AtomRef, PostBrief, Status, utc_now
    from text_generator import TextGenerator

    class StubBlock:
        def __init__(self, text):
            self.text = text

    class StubMessage:
        def __init__(self, text):
            self.content = [StubBlock(text)]

    class StubMessages:
        def create(self, **kwargs):
            return StubMessage(
                "Stress is the dose. <THESIS>Stress is not the enemy.</THESIS> "
                "<CLAIM>Both systems get stronger from controlled stress they can recover from.</CLAIM> "
                "Find your dose."
            )

    class StubClient:
        def __init__(self):
            self.messages = StubMessages()

    loader = AtomLoader(tmp_path)
    gen = TextGenerator(client=StubClient(), loader=loader)

    brief = PostBrief(
        id="t", slug="t",
        created_at=utc_now(), updated_at=utc_now(),
        strategy="two_atom_bridge",
        strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary"), AtomRef(slug="b", role="primary")],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    result = gen.generate(brief)
    assert result.thesis == "Stress is not the enemy."
    assert result.panel_claim == "Both systems get stronger from controlled stress they can recover from."
    assert "<THESIS>" not in result.draft_text
    assert "<CLAIM>" not in result.draft_text


def test_generate_skips_claim_extraction_for_source_spotlight(tmp_path):
    """source_spotlight briefs leave panel_claim empty even if model emits a CLAIM tag."""
    from atom_loader import AtomLoader
    from models import AtomRef, PostBrief, Status, utc_now
    from text_generator import TextGenerator

    class StubBlock:
        def __init__(self, text):
            self.text = text

    class StubMessage:
        def __init__(self, text):
            self.content = [StubBlock(text)]

    class StubMessages:
        def create(self, **kwargs):
            return StubMessage(
                "<THESIS>Source spotlight thesis.</THESIS> "
                "<CLAIM>Stray claim tag the model emitted.</CLAIM>"
            )

    class StubClient:
        def __init__(self):
            self.messages = StubMessages()

    loader = AtomLoader(tmp_path)
    gen = TextGenerator(client=StubClient(), loader=loader)

    brief = PostBrief(
        id="t", slug="t",
        created_at=utc_now(), updated_at=utc_now(),
        strategy="source_spotlight",
        strategy_params={},
        atoms_used=[AtomRef(slug="a", role="primary")],
        angle="x",
        visual_tier="1_diagram",
        status=Status.DRAFTING,
    )
    result = gen.generate(brief)
    assert result.thesis == "Source spotlight thesis."
    assert result.panel_claim == ""
    # source_spotlight does not extract or strip CLAIM tags. A stray <CLAIM>
    # from the model would survive in draft_text. This is intentional;
    # the prompt doesn't include the CLAIM rule for source_spotlight.
    assert "<CLAIM>" in result.draft_text
