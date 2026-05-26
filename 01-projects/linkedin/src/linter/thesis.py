"""Extract <THESIS>...</THESIS> sentences from generated body text.

Thin wrapper over the tag-agnostic linter.tagged.extract_tagged so v1.1 callers
that still use ExtractionResult keep working.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from linter.tagged import extract_tagged


@dataclass
class ExtractionResult:
    thesis: str
    clean_body: str
    warning: Optional[str]


def extract_thesis(body: str) -> ExtractionResult:
    r = extract_tagged(body, "THESIS")
    return ExtractionResult(thesis=r.extracted, clean_body=r.clean_body, warning=r.warning)
