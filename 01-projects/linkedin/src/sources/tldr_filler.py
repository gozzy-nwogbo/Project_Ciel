"""LLM-based tldr fill for atoms missing the optional v2.2 tldr field.

Successful fills back-write the result to the atom file's front-matter
so the atom is "completed" for future uses — the graph compounds.
"""
from __future__ import annotations

from typing import Any, Optional

import frontmatter

from atom_loader import Atom


SYSTEM_PROMPT = """You distill a knowledge atom into one sentence.

The sentence:
- Stands alone for a cold reader who has never seen this atom.
- Is one declarative sentence, ideally under 80 characters.
- Captures the core mechanism or claim, not metadata about the atom.
- Plain text only. No quotes, no markdown, no preamble.
"""


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
            f"Produce one sentence."
        )
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=120,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = "".join(block.text for block in response.content if hasattr(block, "text"))
        except Exception:
            return None

        tldr = text.strip().strip('"').strip()
        if not tldr:
            return None

        if atom.path is not None and atom.path.exists():
            try:
                post = frontmatter.load(atom.path)
                post["tldr"] = tldr
                atom.path.write_text(frontmatter.dumps(post) + "\n")
            except Exception:
                # Back-write failed; still return the tldr so caller can use it for this render.
                pass

        return tldr
