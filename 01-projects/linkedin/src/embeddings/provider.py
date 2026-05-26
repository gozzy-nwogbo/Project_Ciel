"""OpenAI embedding provider. Wraps text-embedding-3-small."""
from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI


MODEL = "text-embedding-3-small"


class OpenAIEmbedder:
    """Synchronous OpenAI embedder. One text in, one vector out."""

    def __init__(self, api_key: Optional[str] = None):
        resolved = api_key or os.environ.get("OPENAI_API_KEY")
        if not resolved:
            raise ValueError(
                "OpenAIEmbedder requires OPENAI_API_KEY in env or api_key kwarg."
            )
        self._client = OpenAI(api_key=resolved)

    def embed(self, text: str) -> list[float]:
        response = self._client.embeddings.create(model=MODEL, input=text)
        return list(response.data[0].embedding)
