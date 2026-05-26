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
