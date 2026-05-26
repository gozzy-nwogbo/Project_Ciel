"""Tests for the embedding cache layer."""
import json
from pathlib import Path


class FakeEmbedder:
    """Returns a stable vector based on the text; counts calls."""
    def __init__(self):
        self.calls = 0

    def embed(self, text: str) -> list[float]:
        self.calls += 1
        return [float(len(text)), 0.0, 1.0]


def test_cache_miss_calls_embedder_and_persists(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()

    vec = cache.get_or_embed("slug1", "hello world", embedder)

    assert vec == [11.0, 0.0, 1.0]
    assert embedder.calls == 1
    saved = json.loads(cache_path.read_text())
    assert "slug1" in saved
    assert "body_hash" in saved["slug1"]
    assert saved["slug1"]["embedding"] == [11.0, 0.0, 1.0]


def test_cache_hit_does_not_call_embedder(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()

    _ = cache.get_or_embed("slug1", "hello world", embedder)
    _ = cache.get_or_embed("slug1", "hello world", embedder)

    assert embedder.calls == 1, "second call should hit cache"


def test_cache_hash_mismatch_re_embeds(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()

    _ = cache.get_or_embed("slug1", "hello", embedder)
    vec2 = cache.get_or_embed("slug1", "hello world", embedder)

    assert embedder.calls == 2
    assert vec2 == [11.0, 0.0, 1.0]


def test_cache_survives_round_trip(tmp_path: Path):
    """A new cache instance reads the persisted JSON on init."""
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache = EmbeddingCache(cache_path)
    embedder = FakeEmbedder()
    _ = cache.get_or_embed("slug1", "hello", embedder)

    cache2 = EmbeddingCache(cache_path)
    vec = cache2.get_or_embed("slug1", "hello", FakeEmbedder())  # fresh embedder

    assert vec == [5.0, 0.0, 1.0]


def test_cache_creates_parent_directory(tmp_path: Path):
    from embeddings.cache import EmbeddingCache
    nested = tmp_path / "deep" / "nested" / "embeddings.json"
    cache = EmbeddingCache(nested)
    _ = cache.get_or_embed("slug1", "x", FakeEmbedder())
    assert nested.exists()


def test_cache_handles_corrupt_json(tmp_path: Path):
    """If existing JSON is malformed, init resets to empty (no exception)."""
    from embeddings.cache import EmbeddingCache
    cache_path = tmp_path / "embeddings.json"
    cache_path.write_text("not valid json {{{")
    cache = EmbeddingCache(cache_path)
    vec = cache.get_or_embed("slug1", "hello", FakeEmbedder())
    assert vec == [5.0, 0.0, 1.0]
