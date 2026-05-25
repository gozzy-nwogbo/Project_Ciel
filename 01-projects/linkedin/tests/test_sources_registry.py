from pathlib import Path

from sources.registry import SourceEntry, SourcesRegistry


def _registry_path(tmp_path: Path) -> Path:
    p = tmp_path / "sources.yml"
    p.write_text(
        'Richard Rumelt, 2011:\n'
        '  type: book\n'
        '  author_bio: "UCLA strategy professor and author of Good Strategy / Bad Strategy"\n'
        '  work: "Good Strategy / Bad Strategy"\n'
        '\n'
        '"Nate B. Jones, AI Daily Update":\n'
        '  type: video\n'
        '\n'
        'Anonymous:\n'
        '  type: post\n'
    )
    return p


def test_registry_loads_book_entry(tmp_path):
    reg = SourcesRegistry(_registry_path(tmp_path))
    entry = reg.lookup("Richard Rumelt, 2011")
    assert entry is not None
    assert entry.type == "book"
    assert "UCLA" in entry.author_bio
    assert entry.work == "Good Strategy / Bad Strategy"


def test_registry_loads_video_entry_without_bio(tmp_path):
    reg = SourcesRegistry(_registry_path(tmp_path))
    entry = reg.lookup("Nate B. Jones, AI Daily Update")
    assert entry is not None
    assert entry.type == "video"
    assert entry.author_bio is None


def test_registry_missing_entry_returns_none(tmp_path):
    reg = SourcesRegistry(_registry_path(tmp_path))
    assert reg.lookup("Unknown Person, 9999") is None


def test_registry_handles_missing_file(tmp_path):
    """Registry loads cleanly even if the file does not exist."""
    reg = SourcesRegistry(tmp_path / "does-not-exist.yml")
    assert reg.lookup("anyone") is None
