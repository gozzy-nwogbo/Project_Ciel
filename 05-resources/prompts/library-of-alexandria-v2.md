# Library of Alexandria v2 — Munger Lattice Reading List

**Purpose:** Generate a tiered, cross-domain reading list designed to function as a "Munger lattice" of high-transfer mental models. Paste into Perplexity deep research (or equivalent).

**When to use:** When expanding the NotebookLM corpus across disciplines that compound. Pairs with the second-brain atom system — books from this list become atomized into `02-knowledge/`.

**Context:** Existing canon already covers writing and design. This prompt fills the gaps in disciplines whose ideas transfer across domains.

---

## Prompt (paste-ready)

```
You are building a curated reading list across 8 disciplines designed to function
as a "Munger lattice" — a corpus where ideas from one domain compound
when combined with ideas from another. The goal is not breadth for its own sake
but high-transfer mental models: books whose frames carry into other domains.

For each of the following 8 domains, produce a tiered reading list:

DOMAINS:
1. Cognitive science & behavioral economics
2. Engineering & systems thinking
3. Game theory & strategy
4. Biology & complex adaptive systems
5. Probability & statistics (decision under uncertainty)
6. Economics & markets (incentives, emergent order)
7. Philosophy of knowledge (epistemology, philosophy of science)
8. Intellectual history (history of ideas + history of technology)

For each domain, return THREE tiers:

- TIER A (Foundational, 3-7 books): The books that define the domain.
  A serious reader cannot skip these. Include canonical authors and the
  specific titles. Note which book to read first.

- TIER B (Consolidating, 5-15 books): Books that extend, refine, or
  apply the foundations. Includes both classical and contemporary works.
  Prioritize books with high cross-domain transfer — ones whose frames
  show up in other disciplines.

- TIER C (Advanced / specialized, 5-20 books): Deep cuts, specialized
  works, or contested texts that reward serious engagement. Optional
  but high-value for someone going deep.

CRITERIA FOR INCLUSION:
- Prefer books over articles unless an article is canonical (e.g.,
  Conway's "How Do Committees Invent?")
- Prefer authors who reason well over authors who are merely popular.
- Prioritize books that pattern-match across disciplines (e.g.,
  Donella Meadows' Thinking in Systems shows up usefully in biology,
  engineering, economics, and policy).
- Flag any books that appear in multiple domains' lists — these are
  the high-transfer titles.

OUTPUT FORMAT:
For each domain, structure as:
  ## [Domain name]
  ### Tier A — Foundational
  1. [Author, Title] — [1-sentence reason]
  ### Tier B — Consolidating
  ...
  ### Tier C — Advanced/specialized
  ...

End with a "CROSS-DOMAIN INDEX" section listing books that appeared
in multiple domains, with notes on why they transfer.

The reader's context: they are building AI agent systems, doing
consulting, and creating content. They already have strong canons in
writing and design — do not duplicate those domains.
```

---

## Why these 8 domains

Triangulated against trajectory (AI builder + consulting + content + video):

| Domain | What it powers |
|---|---|
| Cognitive science / behavioral econ | UX, content hooks, persuasion, persona-driven video |
| Engineering / systems thinking | Agent architecture, second brain, infra design |
| Game theory / strategy | Consulting framing, B2B GTM, deal design |
| Biology / complex adaptive systems | Multi-agent design, emergent behavior, niches |
| Probability / statistics | AI reasoning, decision quality, risk framing |
| Economics / markets | Incentive design, pricing, emergent order |
| Philosophy of knowledge | Epistemic connection type (atom graph), AI reasoning grounding |
| Intellectual history | Genealogical connection type, "why ideas win" pattern recognition |

## What was cut

Linguistics, anthropology, architecture/pattern languages, military doctrine, law, theology, art history, music theory. Either narrow-transfer or covered by adjacent picks. See the brainstorm transcript for the trade-off reasoning.

## After running the prompt

1. Save Perplexity output to `personalplayground/notebooklm/munger-lattice-canon.md`.
2. Prioritize **Tier A across all 8 domains first** (~40 books) before going deep on any one.
3. Download → upload to NotebookLM → atomize via existing pipeline.
4. Books that appear in the cross-domain index get priority — they're the connectors.

## Operational principle

Build the corpus for **thinking quality**, not for content output. The LinkedIn engine extracts value from a well-built corpus; the corpus must never be shaped to feed the engine. The day you pick a book because "it'll make great atoms for a post" is the day the lattice starts decaying.

---

*Drafted 2026-05-24 during LinkedIn engine brainstorm. Companion to `01-projects/linkedin/` spec.*
