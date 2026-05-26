"""LLM-based tldr fill for atoms missing the optional v2.2 tldr field.

Successful fills back-write the result to the atom file's front-matter
so the atom is "completed" for future uses; the graph compounds.

v1.2.2: default model upgraded to Sonnet (Haiku consistently overshoots
the 80-char cap). Retry-on-overshoot adds a safety net for the rare cases
Sonnet still misses: if the first response would trigger the truncation
safety net, ask for a fresh sentence under 50 chars and keep that one
instead. Returns the shortest complete sentence available.
"""
from __future__ import annotations

from typing import Any, Optional

import frontmatter

from atom_loader import Atom


TLDR_MAX_CHARS = 80
TLDR_RETRY_TARGET_CHARS = 50


SYSTEM_PROMPT = """You distill a knowledge atom into one short sentence.

Hard requirements (these are not aspirational, they are limits):
- ONE complete sentence ending in a period.
- Target 60 characters. Hard cap 80 characters total, including the period.
- Stands alone for a cold reader who has never seen this atom.
- Captures the core mechanism or claim, not metadata about the atom.
- Plain text only. No quotes, no markdown, no preamble.

Process: draft the sentence. Count characters. If over 60, rewrite shorter.
If over 80, rewrite again. Aim for the shortest complete sentence that still
conveys the mechanism. Better to land at 50 characters than 79.
"""


RETRY_PROMPT_SUFFIX = """
Your previous attempt exceeded the 80-character cap and would have been
truncated mid-sentence. Rewrite in under 50 characters. Keep the mechanism
intact but cut every word that is not load-bearing. One complete sentence,
period at the end.
"""


def _truncate_at_word_boundary(text: str, max_chars: int) -> str:
    """Truncate to max_chars at the last whitespace boundary, append ellipsis."""
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - 1].rstrip()
    space = cut.rfind(" ")
    if space > 0:
        cut = cut[:space]
    return cut.rstrip(",;:.") + "…"


def _clean_response(text: str) -> str:
    """Strip quotes, whitespace, common LLM ornaments. Returns cleaned text."""
    return text.strip().strip('"').strip()


class TldrFiller:
    def __init__(self, client: Any, model: str = "claude-sonnet-4-6"):
        self.client = client
        self.model = model

    def fill(self, atom: Atom) -> Optional[str]:
        """Generate a tldr for the atom. Back-write on success. Return text or None on failure."""
        body_snippet = (atom.body or "").strip().replace("\n", " ")[:600]
        base_user_prompt = (
            f"Atom title: {atom.title}\n"
            f"Domain: {atom.domain or 'unspecified'}\n"
            f"Source: {atom.source or 'unspecified'}\n"
            f"Body:\n{body_snippet}\n\n"
            f"Produce one sentence under 80 characters."
        )

        # First attempt
        first = self._call(base_user_prompt)
        if first is None:
            return None
        first_clean = _clean_response(first)
        if not first_clean:
            return None

        # If the first response fits, accept it.
        if len(first_clean) <= TLDR_MAX_CHARS:
            tldr = first_clean
        else:
            # Overshoot. Retry once with a tighter constraint. Take whichever
            # response is shorter while still being a complete sentence (ends in
            # period/!/?). If the retry also overshoots, fall back to the
            # truncate-at-word-boundary safety net on whichever is shorter.
            retry_prompt = base_user_prompt + RETRY_PROMPT_SUFFIX
            second = self._call(retry_prompt)
            second_clean = _clean_response(second or "")
            tldr = _pick_better(first_clean, second_clean)
            if len(tldr) > TLDR_MAX_CHARS:
                tldr = _truncate_at_word_boundary(tldr, TLDR_MAX_CHARS)

        if atom.path is not None and atom.path.exists():
            try:
                post = frontmatter.load(atom.path)
                post["tldr"] = tldr
                atom.path.write_text(frontmatter.dumps(post) + "\n")
            except Exception:
                # Back-write failed; still return the tldr so caller can use it for this render.
                pass

        return tldr

    def _call(self, user_prompt: str) -> Optional[str]:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=80,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return "".join(block.text for block in response.content if hasattr(block, "text"))
        except Exception:
            return None


def _is_complete_sentence(text: str) -> bool:
    """Heuristic: ends in . ! or ? and has no trailing ellipsis from a safety-net cut."""
    if not text:
        return False
    last = text[-1]
    if last not in ".!?":
        return False
    # The truncate-at-word-boundary helper appends '…'; reject those.
    return not text.endswith("…")


def _pick_better(first: str, second: str) -> str:
    """Return the better candidate when retry happened.

    Preference order:
    1. Both complete sentences and both <= cap: shorter wins.
    2. One complete sentence within cap, other not: complete-within-cap wins.
    3. Neither within cap but both complete: shorter wins (safety net will truncate).
    4. Otherwise: longer/non-empty wins as best-effort fallback.
    """
    first_ok = _is_complete_sentence(first) and len(first) <= TLDR_MAX_CHARS
    second_ok = _is_complete_sentence(second) and len(second) <= TLDR_MAX_CHARS

    if first_ok and second_ok:
        return second if len(second) < len(first) else first
    if first_ok:
        return first
    if second_ok:
        return second

    # Neither within cap. Prefer complete sentences over fragments.
    if _is_complete_sentence(first) and _is_complete_sentence(second):
        return second if len(second) < len(first) else first
    if _is_complete_sentence(first):
        return first
    if _is_complete_sentence(second):
        return second

    # Neither is a complete sentence; fall back to whichever has content.
    return first if first else second
