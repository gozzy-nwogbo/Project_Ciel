"""Text generator — Claude API call constrained by voice rules."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from atom_loader import AtomLoader
from models import PostBrief, Status, utc_now

if TYPE_CHECKING:
    from sources.registry import SourcesRegistry


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

COLD READER ANCHOR (source-type-aware):
- Assume the reader has never heard of the source author or the concepts you name.
- The first time you reference a concept from an atom, anchor it with a 5-to-8-word inline definition or context cue. Example: not "Chain-Link Systems are tricky" but "Chain-Link Systems, where the weakest link caps the whole, are tricky."
- For source authors, anchor depends on source type (provided in the user prompt under "Source anchors"):
  - type: book → On first reference, introduce the author using the full bio sentence provided. Example: "Reading three atoms from Richard Rumelt, a UCLA strategy professor and author of Good Strategy / Bad Strategy, a pattern surfaced."
  - type: video | podcast | post → On first reference, use a 3-5 word descriptor.
  - source type not provided → Use a 3-5 word descriptor as fallback.
- The post must stand alone for a cold LinkedIn reader who has not been following any prior posts.

THESIS LINE:
- The post must contain exactly one thesis sentence wrapped in <THESIS>...</THESIS> tags.
- Treat the tagged sentence as a standalone aphorism — it will be rendered as the visual's hero line.
- Place the tags where the sentence reads naturally in the body. It is part of the post, not a header.

OUTPUT:
- Plain text only. No headers, no markdown.
- Target word count provided in the user prompt — stay in range.
"""

CLAIM_TAG_RULE = """CLAIM TAG (strategy-scoped, two_atom_bridge and convergence_finder only):
- This post must contain exactly one synthesizing sentence wrapped in <CLAIM>...</CLAIM> tags.
- For two_atom_bridge: the shared-mechanism sentence. It renders as the italic line inside the mechanism band beneath the two atom pillars. The THESIS above is your headline aphorism; the CLAIM is the mechanism that supports it.
- For convergence_finder: the synthesis takeaway sentence. The funnel arrows visually point AT this sentence as the conclusion. The CLAIM is your payoff. For convergence posts only, the THESIS above should set up the observation or framing (e.g., "Three atoms from different domains surfaced this week, all pointing at the same thing"), not the takeaway itself. Put the headline aphorism inside <CLAIM>, not <THESIS>.
- Place the tags where each sentence reads naturally in the body. The engine strips both tag pairs so the saved post.md reads clean.
"""

_CLAIM_STRATEGIES = {"two_atom_bridge", "convergence_finder"}


def _compose_system_prompt(strategy: str) -> str:
    """Compose the per-call system prompt.

    Appends CLAIM_TAG_RULE for strategies that need a synthesizing sentence
    (bridge + convergence). The v1.2.1 CONVERGENCE_THESIS_OVERRIDE has been
    removed in v1.2.2: the LLM bias toward "aphorism in THESIS" is strong
    enough that the override competed without winning, and the resulting
    "aphorism on top, synthesis below" shape was accepted as the natural
    convergence layout. The CLAIM_TAG_RULE alone is sufficient to keep
    framing-lines out of the CLAIM slot, which was the original v1.2 fix.
    """
    if strategy in _CLAIM_STRATEGIES:
        return VOICE_SYSTEM_PROMPT + "\n" + CLAIM_TAG_RULE
    return VOICE_SYSTEM_PROMPT


class TextGenerator:
    def __init__(
        self,
        client: Any,
        loader: AtomLoader,
        model: str = "claude-opus-4-7",
        sources_registry: Optional["SourcesRegistry"] = None,
    ):
        self.client = client
        self.loader = loader
        self.model = model
        self.sources_registry = sources_registry

    def generate(self, brief: PostBrief, target_word_range: tuple[int, int] = (80, 200)) -> PostBrief:
        from linter.thesis import extract_thesis

        atom_summaries = []
        source_anchors: list[str] = []
        seen_sources: set[str] = set()
        for ref in brief.atoms_used:
            atom = self.loader.load_one(ref.slug)
            if not atom:
                continue
            snippet = (atom.body or "").strip().replace("\n", " ")[:240]
            atom_summaries.append(f"- [{atom.title}] ({atom.domain or 'no-domain'}): {snippet}")
            src = atom.source or atom.origin
            if src and src not in seen_sources and self.sources_registry is not None:
                seen_sources.add(src)
                entry = self.sources_registry.lookup(src)
                if entry is None:
                    source_anchors.append(f"- {src}: type=unknown (fall back to 3-5 word descriptor)")
                elif entry.type == "book" and entry.author_bio:
                    source_anchors.append(f"- {src}: type=book, bio=\"{entry.author_bio}\"")
                else:
                    source_anchors.append(f"- {src}: type={entry.type}")

        atoms_block = "\n".join(atom_summaries) or "(no atom summaries available)"
        sources_block = "\n".join(source_anchors) if source_anchors else "(no source entries available)"

        lo, hi = target_word_range
        user_prompt = (
            f"Write a LinkedIn post advancing this angle:\n\n"
            f"  {brief.angle}\n\n"
            f"Use these atoms as substance:\n\n"
            f"{atoms_block}\n\n"
            f"Source anchors:\n\n"
            f"{sources_block}\n\n"
            f"Target word count: {lo}-{hi}.\n"
            f"Name 'my second brain' or 'the atom graph' as the source of the observation.\n"
            f"Plain text only — no markdown, no headers. Remember the THESIS tag rule."
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_compose_system_prompt(brief.strategy),
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(block.text for block in response.content if hasattr(block, "text"))

        extraction = extract_thesis(text.strip())
        brief.thesis = extraction.thesis
        brief.draft_text = extraction.clean_body.strip()

        brief.updated_at = utc_now()
        brief.status = Status.TEXT_READY

        if brief.strategy in _CLAIM_STRATEGIES:
            from linter.tagged import extract_tagged
            claim_result = extract_tagged(extraction.clean_body, "CLAIM")
            brief.panel_claim = claim_result.extracted
            brief.draft_text = claim_result.clean_body.strip()
            if claim_result.warning:
                brief.status_history.append({
                    "status": Status.TEXT_READY.value,
                    "timestamp": brief.updated_at.isoformat(),
                    "actor": "engine",
                    "note": claim_result.warning,
                })

        brief.status_history.append({
            "status": Status.TEXT_READY.value,
            "timestamp": brief.updated_at.isoformat(),
            "actor": "engine",
            "note": extraction.warning or "",
        })
        return brief
