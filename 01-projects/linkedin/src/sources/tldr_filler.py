"""LLM-based tldr fill for atoms missing the optional v2.2 tldr field.

Successful fills back-write the result to the atom file's front-matter
so the atom is "completed" for future uses — the graph compounds.
"""
from __future__ import annotations

from typing import Any, Optional

import frontmatter

from atom_loader import Atom


TLDR_MAX_CHARS = 80


SYSTEM_PROMPT = """You distill a knowledge atom into one short sentence.

Hard requirements (these are not aspirational, they are limits):
- ONE sentence.
- Under 80 characters total, including the period.
- Stands alone for a cold reader who has never seen this atom.
- Captures the core mechanism or claim, not metadata about the atom.
- Plain text only. No quotes, no markdown, no preamble.

If your first draft exceeds 80 characters, rewrite it shorter before responding.
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


class TldrFiller:
    def __init__(self, client: Any, model: str = "claude-haiku-4-5-20251001"):
        self.client = client
        self.model = model

    def fill(self, atom: Atom) -> Optional[str]:
        """Generate a tldr for the atom. Back-write on success. Return text or None on failure."""
        body_snippet = (atom.body or "").strip().replace("\n", " ")[:600]
        user_prompt = (
            f"Atom title: {atom.title}\n"
            f"Domain: {atom.domain or 'unspecified'}\n"
            f"Source: {atom.source or 'unspecified'}\n"
            f"Body:\n{body_snippet}\n\n"
            f"Produce one sentence under 80 characters."
        )
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=40,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(block.text for block in response.content if hasattr(block, "text"))
        except Exception:
            return None

        tldr = text.strip().strip('"').strip()
        if not tldr:
            return None
        # Safety net — even with a stricter prompt, the LLM may overshoot.
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
