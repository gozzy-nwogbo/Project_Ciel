"""Extract <TAG>...</TAG> sentences from generated body text. Tag-agnostic."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_SENTENCE_RE = re.compile(r"([^.!?]+[.!?])(?:\s|$)")


@dataclass
class TaggedExtractionResult:
    extracted: str
    clean_body: str
    warning: Optional[str]


def extract_tagged(body: str, tag: str) -> TaggedExtractionResult:
    """Extract content from <TAG>...</TAG>. Strip all such tags from the body.

    Returns the first non-empty match; warns if multiple were found, or falls
    back to the body's first sentence if no non-empty match exists.
    """
    pattern = re.compile(rf"<{tag}>(.*?)</{tag}>", re.DOTALL)
    matches = pattern.findall(body)
    non_empty = [m.strip() for m in matches if m.strip()]
    clean = pattern.sub(lambda m: m.group(1), body)

    if not non_empty:
        first = _first_sentence(clean)
        return TaggedExtractionResult(
            extracted=first,
            clean_body=clean,
            warning=f"no {tag} tag found, used first sentence fallback",
        )

    if len(non_empty) == 1 and len(matches) == 1:
        return TaggedExtractionResult(extracted=non_empty[0], clean_body=clean, warning=None)

    return TaggedExtractionResult(
        extracted=non_empty[0],
        clean_body=clean,
        warning=f"multiple {tag} tags found, used the first",
    )


def _first_sentence(body: str) -> str:
    stripped = body.strip()
    m = _SENTENCE_RE.search(stripped)
    if m:
        return m.group(1).strip()
    return stripped.split("\n")[0].strip()
