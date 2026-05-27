"""Pure-function tests for the coherence module."""
import pytest


def test_cosine_similarity_identical_vectors():
    from embeddings.coherence import cosine_similarity
    v = [0.6, 0.8]  # unit vector
    assert cosine_similarity(v, v) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal():
    from embeddings.coherence import cosine_similarity
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_opposite():
    from embeddings.coherence import cosine_similarity
    assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)


def test_cosine_similarity_zero_vector_returns_zero():
    from embeddings.coherence import cosine_similarity
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0


def test_min_pairwise_similarity_three_vectors():
    from embeddings.coherence import min_pairwise_similarity
    # Two close vectors and one orthogonal: min pairwise is the orthogonal pair (0.0)
    vecs = [[1.0, 0.0], [0.99, 0.14], [0.0, 1.0]]
    assert min_pairwise_similarity(vecs) == pytest.approx(0.0, abs=0.01)


def test_min_pairwise_similarity_all_identical():
    from embeddings.coherence import min_pairwise_similarity
    v = [0.6, 0.8]
    assert min_pairwise_similarity([v, v, v]) == pytest.approx(1.0)


def test_rank_triples_picks_highest_min():
    """Given two candidate triples, the higher-min triple ranks first."""
    from atom_loader import Atom
    from embeddings.coherence import rank_triples

    a = Atom(slug="a", title="A", type="concept", source_date="", body="", domain="x")
    b = Atom(slug="b", title="B", type="concept", source_date="", body="", domain="y")
    c = Atom(slug="c", title="C", type="concept", source_date="", body="", domain="z")
    d = Atom(slug="d", title="D", type="concept", source_date="", body="", domain="z")

    # a, b, c tightly aligned. d orthogonal to a (and to b, c).
    embeddings = {
        "a": [1.0, 0.0],
        "b": [0.99, 0.14],
        "c": [0.98, 0.20],
        "d": [0.0, 1.0],
    }
    domain_to_atoms = {"x": [a], "y": [b], "z": [c, d]}

    ranked = rank_triples(domain_to_atoms, embeddings)
    top_score, top_triple = ranked[0]
    top_slugs = sorted([atom.slug for atom in top_triple])
    assert top_slugs == ["a", "b", "c"], f"expected (a,b,c) triple to win, got {top_slugs}"
    assert top_score > 0.9


def test_rank_triples_deterministic_tiebreak():
    """When triples tie, sort key is the slug tuple ascending."""
    from atom_loader import Atom
    from embeddings.coherence import rank_triples

    a1 = Atom(slug="a1", title="", type="concept", source_date="", body="", domain="x")
    a2 = Atom(slug="a2", title="", type="concept", source_date="", body="", domain="x")
    b = Atom(slug="b", title="", type="concept", source_date="", body="", domain="y")
    c = Atom(slug="c", title="", type="concept", source_date="", body="", domain="z")

    v = [1.0, 0.0]
    embeddings = {"a1": v, "a2": v, "b": v, "c": v}
    domain_to_atoms = {"x": [a1, a2], "y": [b], "z": [c]}

    ranked = rank_triples(domain_to_atoms, embeddings)
    first_slugs = sorted([atom.slug for atom in ranked[0][1]])
    second_slugs = sorted([atom.slug for atom in ranked[1][1]])
    assert first_slugs == ["a1", "b", "c"]
    assert second_slugs == ["a2", "b", "c"]
