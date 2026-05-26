"""Extract <THESIS>...</THESIS> sentences from generated body text."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


_THESIS_RE = re.compile(r"<THESIS>(.*?)</THESIS>", re.DOTALL)
# Naive sentence split — splits on . ! ? followed by whitespace/EOL. Good enough
# for fallback; voice rules already cap exclamation points.
_SENTENCE_RE = re.compile(r"([^.!?]+[.!?])(?:\s|$)")


@dataclass
class ExtractionResult:
    thesis: str
    clean_body: str
    warning: Optional[str]


def extract_thesis(body: str) -> ExtractionResult:
    matches = _THESIS_RE.findall(body)
    non_empty = [m.strip() for m in matches if m.strip()]

    if not non_empty:
        first = _first_sentence(body)
        clean = _strip_tags(body)
        warning = "no THESIS tag found, used first sentence fallback"
        return ExtractionResult(thesis=first, clean_body=clean, warning=warning)

    clean = _strip_tags(body)

    if len(non_empty) == 1 and len(matches) == 1:
        return ExtractionResult(thesis=non_empty[0], clean_body=clean, warning=None)

    warning = "multiple THESIS tags found, used the first"
    return ExtractionResult(thesis=non_empty[0], clean_body=clean, warning=warning)


def _strip_tags(body: str) -> str:
    return _THESIS_RE.sub(lambda m: m.group(1), body)


def _first_sentence(body: str) -> str:
    stripped = _strip_tags(body).strip()
    m = _SENTENCE_RE.search(stripped)
    if m:
        return m.group(1).strip()
    return stripped.split("\n")[0].strip()
