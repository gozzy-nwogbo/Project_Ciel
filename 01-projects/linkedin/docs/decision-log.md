# Decision log

## 2026-05-25 — v1.0 execution complete (orchestrator)

All 26 plan tasks executed against the plan in `2026-05-24-v1-0-implementation-plan.md` (+part2):
- 25 tasks committed (A1 was already in place at session start).
- M2 (manual smoke test) handed back to the user — see Smoke Test section below.

Patches required during execution:
- **G3 fixtures**: added `sixth-concept.md` (storytelling tag). Plan's only-3 fixtures combined with `MIN_CLUSTER_SIZE=4` would have failed the test.
- **H1 linter regex**: rewrote the second alt of `contrastive_framing` from `\bnot [A-Za-z]+[+]\b` to `\b[A-Za-z]{3,}\+`. Original regex could not match the plan's own test fixture because trailing `\b` after `[+]` requires a word/non-word transition that never exists when `+` is followed by punctuation.
- **C3 test**: G1's added `sample-to-third` connection broke the original `len(edges) == 1` assertion. Loosened to `>= 1` and find the mechanism edge by type.
- **L3 PYTHONPATH**: the plan's slash command markdown omitted `PYTHONPATH=src`; without it `python -m cli.draft_post` cannot resolve sibling-module imports. Patched both wrappers.

Test status: 38/38 pass at branch tip.

---

## 2026-05-25 — v1.0 smoke test commands (prepared for user)

To run the manual smoke test the user executes these from any terminal in the vault:

```bash
# 1. Generate a draft against real atoms
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --strategy=source_spotlight --source='Richard Rumelt, 2011' --no-render

# 2. Read the bundle slug from the "Wrote bundle:" line, then advance Gate 1 (renders diagram)
# Replace <slug> below.
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --advance <slug>

# 3. View status
PYTHONPATH=src \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
python3 -m cli.linkedin_status --backlog

# 4. Open the rendered diagram (replace <slug>)
open /Users/gozzynwogbo/second-brain/01-projects/linkedin/backlog/<slug>/diagram.png
```

Pre-flight checks already verified by orchestrator: `ANTHROPIC_API_KEY` is set (109 chars), `dot` binary installed via brew, vault has atoms with `origin: "Richard Rumelt, 2011"` (8 found).

Smoke result to append after run: voice-linter hard fails, anything notable in the rendered diagram or generated text.

---

## 2026-05-25 — v1.0 smoke result (user-run)

Strategy used: source_spotlight on source="Richard Rumelt, 2011".
Atoms chosen: Chain-Link Systems, Four Hallmarks of Bad Strategy, Design-Type Strategy.

**Text:** Coherent and tight. Synthesized a shared pattern ("coherence beats effort, find the binding constraint"). Closing question landed. User feedback: "good start, missing polish" — specifically, the post assumes the reader knows who Rumelt is and what those three concepts are. Reads inside-baseball to a cold LinkedIn reader.

**Diagram:** 3 floating ovals, no edges. Broken-looking.

**Root cause of broken diagram (not brand-spec):** source_spotlight picked atoms that have no `type: connection` atoms tying them together in the vault. ConnectionGraph found 0 edges among the 3 atoms. Renderer dutifully drew 3 isolated nodes.

### v1.0.1 follow-ups

1. **Diagram-strategy pairing bug.** source_spotlight defaults to visual_tier="1_diagram" but Tier 1 only makes sense when ≥1 edge exists between the chosen atoms. Options:
   - (a) Synthesize an edge from the strategy's `secondary_domain` finder or the post's named pattern, and draw it.
   - (b) Have source_spotlight default to Tier 2 (carousel) or no visual when no edges exist.
   - (c) Add a pre-render validator: if Tier 1 + edge_count == 0, drop to "no visual" and surface a warning.

2. **System prompt: anchor unfamiliar concepts.** Add a rule to `VOICE_SYSTEM_PROMPT`: "When you name a concept from an atom, give a 5-to-8-word inline definition the first time it appears. Assume the reader has never heard of the source." This is the polish gap the smoke test surfaced.

3. **Slug filesystem-safety.** Source slug "richard-rumelt,-2011-spotlight" includes a comma. Works on macOS but brittle on other filesystems. Strip more punctuation in `_make_slug`.

None of these block merging v1.0 if the goal is "ship the engine, iterate on output quality." If the goal is "ship something I'd actually post," (1) and (2) need to land first.

