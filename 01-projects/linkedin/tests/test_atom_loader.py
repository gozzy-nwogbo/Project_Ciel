from pathlib import Path

from atom_loader import Atom, AtomLoader


def test_loads_concept_atom(atom_source: Path):
    loader = AtomLoader(atom_source)
    atoms = loader.load_all()
    titles = [a.title for a in atoms]
    assert "Sample Concept" in titles


def test_filter_by_source(atom_source: Path):
    loader = AtomLoader(atom_source)
    atoms = loader.load_by_source("test-fixture")
    assert all(a.origin == "test-fixture" for a in atoms)


def test_atom_has_slug(atom_source: Path):
    loader = AtomLoader(atom_source)
    atoms = loader.load_all()
    concept = next(a for a in atoms if a.title == "Sample Concept")
    assert concept.slug == "sample-concept"
