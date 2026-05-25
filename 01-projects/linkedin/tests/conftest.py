"""Shared pytest fixtures for linkedin engine tests."""
import shutil
from pathlib import Path

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def atom_source(tmp_path: Path) -> Path:
    """Copy fixture atoms to a tmp dir; return the dir path."""
    dest = tmp_path / "atoms"
    shutil.copytree(FIXTURES_DIR / "atoms", dest)
    return dest


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    """Bare project root with state/, backlog/, logs/ subfolders."""
    for sub in ("state", "backlog", "logs"):
        (tmp_path / sub).mkdir()
    return tmp_path


@pytest.fixture
def brand_spec(tmp_path: Path) -> Path:
    """Minimal brand-spec for renderer tests."""
    path = tmp_path / "brand-spec.md"
    path.write_text(
        '```yaml\n'
        'colors:\n'
        '  accent_primary: "#1F1F1F"\n'
        '  background: "#FFFFFF"\n'
        '  edge_default: "#737373"\n'
        'typography:\n'
        '  body: "sans-serif"\n'
        '  size_label: "11px"\n'
        'layout:\n'
        '  padding: 32\n'
        '  node_padding: 12\n'
        '```\n'
    )
    return path
