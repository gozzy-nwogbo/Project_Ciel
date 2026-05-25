"""Text generator — Claude API call constrained by voice rules."""
from __future__ import annotations

from typing import Any

from atom_loader import AtomLoader
from models import PostBrief, Status, utc_now


VOICE_SYSTEM_PROMPT = """You write LinkedIn posts in the author's voice.

HARD RULES (these are never broken):
- No em-dashes or en-dashes. Use commas, periods, or restructure.
- No contrastive framing patterns ("Not as X, but as Y", "Not just X, X+"). This is an AI watermark.
- No AI watermark vocabulary: "delve", "tapestry", "navigate the complex", "in conclusion", "moreover", "furthermore", "in essence".
- Active voice as default. Passive only when the subject is genuinely unknown.
- Maximum 1 exclamation point per 150 words.

POSITIONING:
- Framing is "insight + visible system". Posts can name "my second brain" or "the atom graph"
  as the source of the observation. The system is the differentiator.

VOICE:
- Observational, sharp, willing to be specific. Not promotional.
- Tight openings. No throat-clearing. No "In today's world..." or "Have you ever noticed...".
- One observation, evidence from the atoms, named takeaway.
- End with a question or an invitation when natural. No forced CTAs.

OUTPUT:
- Plain text only. No headers, no markdown.
- Target word count provided in the user prompt — stay in range.
"""


class TextGenerator:
    def __init__(self, client: Any, loader: AtomLoader, model: str = "claude-opus-4-7"):
        self.client = client
        self.loader = loader
        self.model = model

    def generate(self, brief: PostBrief, target_word_range: tuple[int, int] = (80, 200)) -> PostBrief:
        atom_summaries = []
        for ref in brief.atoms_used:
            atom = self.loader.load_one(ref.slug)
            if atom:
                snippet = (atom.body or "").strip().replace("\n", " ")[:240]
                atom_summaries.append(f"- [{atom.title}] ({atom.domain or 'no-domain'}): {snippet}")
        atoms_block = "\n".join(atom_summaries) or "(no atom summaries available)"

        lo, hi = target_word_range
        user_prompt = (
            f"Write a LinkedIn post advancing this angle:\n\n"
            f"  {brief.angle}\n\n"
            f"Use these atoms as substance:\n\n"
            f"{atoms_block}\n\n"
            f"Target word count: {lo}-{hi}.\n"
            f"Name 'my second brain' or 'the atom graph' as the source of the observation.\n"
            f"Plain text only — no markdown, no headers."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=VOICE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))

        brief.draft_text = text.strip()
        brief.status = Status.TEXT_READY
        brief.updated_at = utc_now()
        brief.status_history.append({
            "status": Status.TEXT_READY.value,
            "timestamp": brief.updated_at.isoformat(),
            "actor": "engine",
        })
        return brief
