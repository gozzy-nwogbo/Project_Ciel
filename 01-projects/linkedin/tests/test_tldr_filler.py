from pathlib import Path
from unittest.mock import MagicMock

from atom_loader import Atom
from sources.tldr_filler import TldrFiller


def _atom_file(tmp_path: Path) -> Path:
    """Write a real atom file we can read back to check the back-write."""
    p = tmp_path / "filler-fixture.md"
    p.write_text(
        "---\n"
        "title: Filler Fixture\n"
        "type: concept\n"
        "source: Test Source, 2026\n"
        "domain: test\n"
        "tags: [fixture]\n"
        "---\n\n"
        "Some body text describing the concept.\n"
    )
    return p


def _make_atom(path: Path) -> Atom:
    return Atom(
        slug="filler-fixture",
        title="Filler Fixture",
        type="concept",
        source_date="",
        body="Some body text describing the concept.",
        tags=["fixture"],
        domain="test",
        source="Test Source, 2026",
        tldr=None,
        path=path,
    )


def test_fill_calls_llm_and_returns_single_sentence(tmp_path):
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="A single sentence distillation of the concept.")]
    fake_client.messages.create.return_value = fake_response

    filler = TldrFiller(client=fake_client, model="claude-haiku-4-5-20251001")
    result = filler.fill(atom)

    assert result == "A single sentence distillation of the concept."
    fake_client.messages.create.assert_called_once()


def test_fill_back_writes_tldr_to_atom_file(tmp_path):
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text="Back-written distillation.")]
    fake_client.messages.create.return_value = fake_response

    TldrFiller(client=fake_client).fill(atom)

    content = path.read_text()
    assert "tldr: Back-written distillation." in content
    # Body still present
    assert "Some body text describing the concept." in content


def test_fill_returns_none_when_client_raises(tmp_path):
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = RuntimeError("API down")

    result = TldrFiller(client=fake_client).fill(atom)
    assert result is None


def test_fill_truncates_over_long_response_at_word_boundary(tmp_path):
    """LLM responses that exceed 80 chars are truncated with ellipsis at a word boundary."""
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    long_text = (
        "A four-quadrant grid that forces simultaneous examination of what to "
        "eliminate, reduce, raise, and create in your value proposition."
    )
    assert len(long_text) > 80

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text=long_text)]
    fake_client.messages.create.return_value = fake_response

    result = TldrFiller(client=fake_client).fill(atom)

    assert result is not None
    assert len(result) <= 80
    assert result.endswith("…")
    # Ends at a word boundary — no partial word right before the ellipsis
    assert " " not in result[-2:-1]  # char before ellipsis is not a space


def test_fill_under_cap_passes_through_unchanged(tmp_path):
    """Responses already under 80 chars are returned as-is, no ellipsis."""
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    short = "Diagnosis first. Then policy. Then coherent action."
    assert len(short) <= 80

    fake_client = MagicMock()
    fake_response = MagicMock()
    fake_response.content = [MagicMock(text=short)]
    fake_client.messages.create.return_value = fake_response

    result = TldrFiller(client=fake_client).fill(atom)
    assert result == short
    assert "…" not in result


# ---------- v1.2.2 additions ----------


def test_default_model_is_sonnet():
    """v1.2.2: default model upgraded from Haiku to Sonnet for length reliability."""
    from unittest.mock import MagicMock

    filler = TldrFiller(client=MagicMock())
    assert filler.model == "claude-sonnet-4-6"


def test_fill_retries_on_overshoot_and_returns_shorter_response(tmp_path):
    """v1.2.2: if first response > 80 chars, retry with a tighter prompt and take the shorter complete sentence."""
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    over_long = (
        "An exhaustive four-quadrant grid that forces simultaneous examination "
        "of what to eliminate, reduce, raise, and create in your value proposition."
    )
    assert len(over_long) > 80

    retry_response = "Eliminate, reduce, raise, create across your value proposition."
    assert len(retry_response) <= 80
    assert retry_response.endswith(".")

    fake_client = MagicMock()
    fake_responses = [
        _wrap_response(over_long),
        _wrap_response(retry_response),
    ]
    fake_client.messages.create.side_effect = fake_responses

    result = TldrFiller(client=fake_client).fill(atom)

    assert result == retry_response
    assert fake_client.messages.create.call_count == 2
    # The retry call must include the retry suffix in its user prompt
    second_call_kwargs = fake_client.messages.create.call_args_list[1].kwargs
    user_prompt = second_call_kwargs["messages"][0]["content"]
    assert "under 50 characters" in user_prompt


def test_fill_does_not_retry_when_first_response_fits(tmp_path):
    """v1.2.2: if first response is already <=80 chars, no second call."""
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    fits = "Self-directed quality output, measured through feedback loops."
    assert len(fits) <= 80

    fake_client = MagicMock()
    fake_client.messages.create.return_value = _wrap_response(fits)

    result = TldrFiller(client=fake_client).fill(atom)

    assert result == fits
    fake_client.messages.create.assert_called_once()


def test_fill_picks_shorter_when_both_responses_within_cap(tmp_path):
    """v1.2.2: if retry happens and both responses fit, prefer the shorter complete sentence."""
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    # First exceeds cap, retry returns a SHORTER response than would be needed.
    over_long = "x" * 100 + "."  # 101 chars, complete sentence
    short_retry = "Loops measure the gap."  # 22 chars

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = [
        _wrap_response(over_long),
        _wrap_response(short_retry),
    ]

    result = TldrFiller(client=fake_client).fill(atom)
    assert result == short_retry


def test_fill_falls_back_to_truncation_when_both_overshoot(tmp_path):
    """v1.2.2: if Sonnet AND retry both overshoot (rare), safety-net truncation still applies."""
    path = _atom_file(tmp_path)
    atom = _make_atom(path)

    over_long_1 = "A super long sentence about the concept that runs well past the eighty character limit because the model overshot."
    over_long_2 = "A different but still too long sentence about the same concept that also exceeds the cap considerably."
    assert len(over_long_1) > 80
    assert len(over_long_2) > 80

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = [
        _wrap_response(over_long_1),
        _wrap_response(over_long_2),
    ]

    result = TldrFiller(client=fake_client).fill(atom)
    assert result is not None
    assert len(result) <= 80
    # Safety net signature
    assert result.endswith("…")


def _wrap_response(text: str):
    """Helper: produce a MagicMock that mimics the Anthropic response shape."""
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    return response
