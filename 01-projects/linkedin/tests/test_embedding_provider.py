"""Tests for the OpenAI embedder. Mocks the openai client to avoid API hits."""
from unittest.mock import MagicMock, patch

import pytest


def test_openai_embedder_calls_text_embedding_3_small():
    from embeddings.provider import OpenAIEmbedder

    fake_response = MagicMock()
    fake_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    fake_client = MagicMock()
    fake_client.embeddings.create.return_value = fake_response

    with patch("embeddings.provider.OpenAI", return_value=fake_client):
        embedder = OpenAIEmbedder(api_key="sk-test")
        vec = embedder.embed("hello world")

    assert vec == [0.1, 0.2, 0.3]
    fake_client.embeddings.create.assert_called_once()
    call_kwargs = fake_client.embeddings.create.call_args.kwargs
    assert call_kwargs["model"] == "text-embedding-3-small"
    assert call_kwargs["input"] == "hello world"


def test_openai_embedder_reads_env_var_when_no_key_passed(monkeypatch):
    from embeddings.provider import OpenAIEmbedder

    monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
    with patch("embeddings.provider.OpenAI") as MockClient:
        _ = OpenAIEmbedder()
    init_kwargs = MockClient.call_args.kwargs
    assert init_kwargs.get("api_key") == "sk-from-env"


def test_openai_embedder_raises_when_no_key_anywhere(monkeypatch):
    from embeddings.provider import OpenAIEmbedder
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        _ = OpenAIEmbedder()
