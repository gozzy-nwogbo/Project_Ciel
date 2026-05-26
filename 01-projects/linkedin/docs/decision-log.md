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

---

## 2026-05-25 — v1.0.1 patches landed (in-branch)

User chose Option 1 (patch then ship). Two surgical fixes committed on `feat/linkedin-engine-v1.0`:

**Patch A — cold-reader anchor (commit 9823c39):**
Added a `COLD READER ANCHOR` section to `VOICE_SYSTEM_PROMPT` in `src/text_generator.py`. Requires the model to (a) place source authors in 3-5 words on first reference, (b) anchor named concepts with a 5-to-8-word inline definition the first time they appear, (c) assume the reader has not been following prior posts.

**Patch B — edgeless Tier 1 guard (commit e38e6ff):**
`DiagramRenderer.validate` now flags bundles where no `type: connection` atom exists among `atoms_used` as "edgeless diagram." CLI `_advance` catches the flag and advances the bundle to gate2_pending with `visual_asset_paths=[]` and a stderr warning. `--force` overrides if user wants the floating-nodes render anyway.

**Tests:** 39/39 pass. New tests: `test_validate_rejects_edgeless_tier1`, added "anchor" assertion to `test_voice_rules_in_system_prompt`.

**Re-smoke needed (user-run, hits Anthropic API):**

```bash
# 1. Generate (will use atoms not in cooldown from first smoke run)
cd /Users/gozzynwogbo/second-brain/01-projects/linkedin && \
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --strategy=source_spotlight --source='Richard Rumelt, 2011' --no-render

# 2. Advance — should now warn "edgeless" and skip the diagram if no connections exist
PYTHONPATH=src \
LINKEDIN_ATOM_SOURCE=/Users/gozzynwogbo/second-brain/02-knowledge \
LINKEDIN_PROJECT_ROOT=/Users/gozzynwogbo/second-brain/01-projects/linkedin \
LINKEDIN_BRAND_SPEC=/Users/gozzynwogbo/second-brain/01-projects/linkedin/brand-spec.md \
python3 -m cli.draft_post --advance <new-slug>
```

Expected: post text now includes inline anchors for Rumelt and the concept names; advance prints "WARNING: Tier 1 diagram skipped" because the new Rumelt atoms also have no connection atoms among them. Result: a shippable text post, no broken diagram.

---

## 2026-05-26 — v1.1 implementation complete + smoke result

v1.1 shipped per `2026-05-25-tier1-redesign-design.md`. Replaces graphviz network-diagram Tier 1 renderer with a Playwright-driven HTML/CSS atom-card renderer; bundles source-type-aware cold-reader anchoring. 14-task plan executed inline (after the first Haiku subagent thrashed on autocompact in the same failure mode as the v1.0 session — confirms the "mechanical tasks shouldn't be subagent-delegated in this environment" learning).

### v1.1.0 (initial implementation)

13 commits on `feat/linkedin-engine-v1.1`: dependency swap (Playwright + Jinja2 replace graphviz), atom v2.2 `tldr` field, sources.yml registry, TldrFiller, THESIS extraction, voice prompt v2, atom-card template, AtomCardRenderer (Playwright headless Chromium → 1080×1080 PNG), CLI integration, strategy default flips (two_atom_bridge + convergence_finder back to Tier 1), visual-discipline skill update, graphviz deletion. 64/64 tests pass.

### v1.1 smoke (W. Chan Kim & Renee Mauborgne, 2014)

First Rumelt smoke failed at strategy stage — 6 of 8 Rumelt atoms in primary cooldown from the v1.0 / v1.0.1 smokes. Switched to W. Chan Kim & Renee Mauborgne after adding them to `sources.yml`.

**Text:** Voice prompt v2 worked. Body opened "Three atoms from W. Chan Kim and Renée Mauborgne, INSEAD strategy professors and co-authors of Blue Ocean Strategy, sat next to each other in my second brain this morning." — full book-bio anchor fired as designed. Thesis line ("A good strategy tool isn't a prompt, it's a place you can't hide.") extracted from `<THESIS>` tags cleanly, tags stripped from saved post.md.

**Diagram:** Layout correct, brand tokens right (terracotta + cream + Geist), atom blocks rendered properly. But third atom block (Four Actions Framework) cut off bottom of canvas because TldrFiller produced ~200-char distillations despite the "ideally under 80" prompt — and those got back-written to atom files.

### v1.1.1 patches (in-branch)

- **TldrFiller hard 80-char cap.** Dropped "ideally" wording, reduced max_tokens from 120 to 40, added post-process truncation at word boundary with ellipsis. Two new tests.
- **Renderer safety net.** atom.tldr truncated at 80 chars in `_build_template_context` so stale or hand-authored over-long tldrs can't overflow. Tested.
- **Thesis auto-shrink.** Thesis font drops from 78px to 60px when sentence exceeds 60 chars, keeping it to 2 lines instead of 3. Tested.
- **Atom file cleanup.** Trimmed the 3 K&M atoms' bloated tldrs in-place (errc-grid, strategy-canvas, four-actions-framework) to under 80 chars each.

### v1.1.1 smoke

Six K&M atoms now cooled down from cumulative smokes; engine picked Six Paths Framework, Price Corridor of the Target Mass, Pioneer-Migrator-Settler Map. Diagram fit cleanly. Text was solid. User feedback: "Both are much better. We're getting closer to what I consider good. The visuals are solid."

Two minor footer issues surfaced:
1. Footer left wrapped onto 2 lines because source slug "W. Chan Kim & Renee Mauborgne, 2014" included the citation year.
2. Footer right "3 atoms · source-spotlight" also wrapped, looking cramped.

### v1.1.2 patches (in-branch)

- **Strip citation year from footer.** `_strip_citation_year()` drops trailing `, YYYY` from the displayed source slug. sources.yml lookup still uses the full citation key — only the visual is cleaned. Tested.
- **Footer nowrap defense.** Added `white-space: nowrap` + gap to footer flex items so future borderline-long content can't wrap into multiple lines.

### v1.1.2 smoke (Hamilton Helmer, 2017)

Added Hamilton Helmer to sources.yml (Strategy Capital founder, author of 7 Powers). Smoke run produced a clean post and diagram. User feedback: "both look great."

### Final state

- Branch: `feat/linkedin-engine-v1.1` with 16 commits (13 v1.1.0 + 2 v1.1.1 + 1 v1.1.2; plus 2 content commits adding K&M and Helmer to sources.yml)
- Tests: 68/68 pass including live Playwright render smoke
- Three book sources seeded in sources.yml (Rumelt, Kahneman, Munger, K&M, Helmer); seven atoms now have clean tldrs in 02-knowledge

### v1.1.x follow-ups (not blocking merge)

- `--reset-cooldowns` CLI flag for smoke-testing iteration (cooldowns exhausted Rumelt then K&M within 2-3 smokes; iteration loop is hostile without manual JSON editing)
- Slug-safety on source slug for filesystem (carryover from v1.0.1 follow-up #3 — still has comma in bundle paths)

---

## 2026-05-26 — v1.1.3: cross-domain strategy smokes + visual revert

### Cross-domain smokes (after v1.1 merged to main)

Ran the other two Tier 1 strategies end-to-end against real atoms:

- **two_atom_bridge:** `antifragile-triad` (mental-models) + `autoregulated-active-recovery` (health-performance). Cross-domain "respond to stress" pair.
- **convergence_finder:** `--topic=feedback`, which touches 11 different domains in the vault.

Texts on both: strong. Voice prompt v2's source-anchor rule fired correctly when atoms had book-source registry entries; fell back to 3-5 word descriptors otherwise. The engine is producing publish-quality body text across all three Tier 1 strategies.

### The visual mismatch

Visuals on both: **the wrong conceptual shape.** User feedback: "the visuals are really good for the single source or source_spotlight, but they're not as good for the convergence_finder and the two_atom_bridge."

Root cause: the Variant B atom-card template was designed in the brainstorm against the source_spotlight shape — "N atoms from one catalog page." That literally IS a list, so a list visual works. The other two strategies are different conceptual shapes:

- `two_atom_bridge` is about *a connection between two things*. The card flattens that into a bullet list of two items; the bridge structure (relationship, mechanism, analogy) is invisible.
- `convergence_finder` is about *multiple distant atoms pointing at a shared center*. The card flattens that hub-and-spokes shape into a bullet list; the convergence point itself is invisible.

We chose one visual template for all strategies and only mocked it against the one strategy it matches. Real design hole.

### v1.1.3 patch — text-only defaults for bridge + convergence

Defer the visual fix to a dedicated design cycle (proper strategy-specific visual treatments, separate brainstorm). For now:

- `two_atom_bridge` default `visual_tier` flips back to `0_text`.
- `convergence_finder` default `visual_tier` flips back to `0_text`.
- `source_spotlight` unchanged — it still defaults to Tier 1 atom-card.
- `--tier=1` still opts into the atom-card if the user wants it.

Texts ship as the workhorse for these strategies until v1.x adds proper visuals.

Test impact: positive assertions in `test_two_atom_bridge.py` and `test_convergence_finder.py` updated to assert `"0_text"`. `test_end_to_end.py` reverted to expect empty `visual_asset_paths` for the bridge pipeline (the v1.1 update of that assertion is itself rolled back).

### v1.1.3 follow-up (queued for a later cycle)

- **Strategy-specific visual treatments.** A separate brainstorming session for v1.2 or v1.3. Bridge wants something like side-by-side cards with a connector / shared-mechanism band; convergence wants a hub-and-spokes layout. Different conceptual shape per strategy means different visual primitive.

---

## 2026-05-26 — v1.2: strategy-specific visuals + smoke

### What shipped

v1.2 absorbed the v1.1.3 follow-up: strategy-specific Tier 1 visuals for `two_atom_bridge` and `convergence_finder`, both at 4:5 (1080x1350). `source_spotlight` is unchanged. The visual family stays coherent (terracotta accent, Geist font, shared meta-row + footer) but each strategy now gets a template that matches its conceptual shape.

- **Bridge A:** two atom pillars side-by-side, dashed-border mechanism band beneath carrying the `panel_label` (derived from connection type) and `panel_claim` (italic synthesis sentence from `<CLAIM>` tag).
- **Convergence C:** three funnel atom cards across the top, three downward arrows, solid-border convergence panel at the bottom carrying `CONVERGES ON · {TOPIC}` label and `panel_claim` synthesis.

Architecturally, the renderer codebase split from one class into three sibling renderers behind a small Tier 1 registry. PostBrief gained three additive fields (`aspect_ratio`, `panel_label`, `panel_claim`). Voice prompt v3 adds a strategy-scoped `<CLAIM>...</CLAIM>` tag for the two new strategies; THESIS rule still applies universally.

### Plan execution

Brainstorm produced `2026-05-26-strategy-visuals-design.md`; plan in `2026-05-26-v1-2-implementation-plan.md`. Executed via subagent-driven development: 14 tasks plus 4 follow-up fix commits from quality reviews and smoke iteration. Test count grew from 69 baseline to 108 passing at branch tip.

Selected commits worth flagging:
- `4c1c636` PostBrief schema deltas.
- `25138d7` Generalized `extract_thesis` into tag-agnostic `linter.tagged.extract_tagged`.
- `e27ec75` + `d440944` + `3c10987` Voice prompt v3 with strategy-scoped CLAIM rule; tightened CLAIM prompt boundary, timestamp consistency, and em-dash scrub during quality-review fix loop.
- `5055311` + `8139f24` Bridge strategy update with quality-review fixes (real-fallback test instead of dict.get truism; Playwright importorskip on e2e).
- `de90981` Convergence strategy update.
- `4a5a16c` + `9a15fd3` BridgeCardRenderer and ConvergenceCardRenderer with live Playwright smoke tests.
- `8936b5e` Convergence CLAIM rule tightening (post-first-smoke iteration; see "Smoke" below).
- `3f1a909` Convergence funnel-atom char cap raised 60 to 80 (post-second-smoke iteration).

### Bridge smoke (user-run)

Strategy: `two_atom_bridge` on `antifragile-triad` (mental-models) + `autoregulated-active-recovery` (health-performance). Same pair as v1.1.3 cross-domain smoke; connection cooldown was clear because v1.1.3 only generated text-only briefs against this pair.

Text: clean. Voice prompt v3's CLAIM rule produced a coherent shared-mechanism sentence wrapped in `<CLAIM>` tags. THESIS sat at the top of the card as an aphorism. Body stripped both tag pairs cleanly.

Visual: ships well. Two pillars rendered at proper proportion, mechanism band sits cleanly beneath, footer reads `2 atoms · cross-domain` + `two-atom-bridge`. User feedback: "shipped a clean visual." Minor visual note from user: the meta-row text `bridge // mental-models × health-performance` sits less neatly than convergence's shorter equivalent, but acceptable.

### Convergence smoke iteration

**First convergence smoke:** layout was right but the text role split was inverted. The LLM put the synthesis takeaway in THESIS (top of card, aphorism slot) and the framing observation in CLAIM (bottom convergence panel). The funnel arrows visually point AT the bottom panel, implying that's the conclusion, so a framing sentence there reads backwards. User feedback called this out: the three-atoms-surfaced framing belongs at the top; the synthesis takeaway belongs in the panel.

Root cause: the v1.2 CLAIM rule said "unified-mechanism sentence" which the LLM interpreted as the takeaway, and the universal THESIS rule "Treat the tagged sentence as a standalone aphorism" pulled the aphorism into the top slot. Two rules both pointed the aphorism upward.

**Patch (commit `8936b5e`):** tightened the convergence-specific CLAIM rule to make the role split explicit. For convergence posts, THESIS = framing/observation; CLAIM = synthesis takeaway; "Put the headline aphorism inside <CLAIM>, not <THESIS>." Added `test_claim_tag_rule_specifies_convergence_role_split` to lock the new prompt language.

**Second convergence smoke:** improvement. The CLAIM slot now correctly holds a synthesis sentence ("A demo, a label, and a stated task are the same tool..."). The THESIS slot still pulled an aphorism rather than the explicit framing line, but at a different abstraction level (general aphorism on top, atom-specific synthesis in panel). User feedback: "the thesis/claim pairing works."

Funnel atom cards: two of three rendered complete sentences. The third (Drucker "Knowledge Worker Productivity") was truncated mid-sentence. Investigation: the atom's `tldr` field in the vault is itself pre-truncated (`tldr: Knowledge work productivity measures quality output from self-directed…`). The 80-char cap can't recover what's already baked into the source file. Data hygiene, not engine bug. Two of three atoms shipped clean.

**Patch (commit `3f1a909`):** funnel-atom char cap raised from 60 to 80 to match the v1.1.1 filler hard-cap. Two of three atoms now render full sentences end-to-end.

Final user feedback: "all in all, this is a much better run than the last one... good job."

### Final state

- Branch: `feat/linkedin-engine-v1.2` with 18 commits (14 plan tasks + 4 fix commits from reviews and smoke).
- Tests: 108/108 pass, including live Playwright render smokes for bridge and convergence.
- All three Tier 1 renderers active behind `tier1_registry.for_strategy(...)`; `source_spotlight` unchanged.
- visual-discipline skill updated with per-strategy rule blocks; stale SVG-output line removed.
- PostBrief schema additive (aspect_ratio, panel_label, panel_claim); old briefs on disk deserialize with safe defaults.

### v1.2 follow-ups (queued, not blocking merge)

- **Truncated tldrs in vault atoms.** Pre-v1.1.1 atoms have tldrs already saved with trailing ellipsis (the renderer cap can't recover them). Either run the tldr-filler over the corpus with a tighter complete-sentence prompt and back-write the fixes, or add funnel-atom auto-shrink so longer text fits without truncation. Prefer the former since it benefits all renderers, not just convergence.
- **Convergence THESIS still pulls aphorism.** The strategy-scoped CLAIM rule moved the synthesis into the panel correctly, but the universal THESIS rule "Treat the tagged sentence as a standalone aphorism" still anchors the top slot. To get the explicit framing line at the top, the THESIS rule itself needs to become strategy-aware (a `_compose_system_prompt` extension or a per-strategy prompt assembly). One more iteration would lock it.
- **`atom_card.html.j2` still inlines its CSS** rather than including `_card_frame.css.j2`. Deferred from the spec to avoid source_spotlight regression risk during v1.2. Migrate after smoke confirms parity.
- **CLI friction.** Manual env-var prefixes (`PYTHONPATH=src`, `LINKEDIN_ATOM_SOURCE=...`, etc.) make every CLI invocation a five-line paste. The existing `/draft-post` slash command wrapper should be the daily driver; smoke runs in this cycle should have used it from the start. Document and adopt.
- **`--reset-cooldowns` CLI flag** carryover from v1.1.x. Still hostile to iterate smokes without manual JSON editing of `state/atom-usage.json` and `state/connection-usage.json`.
- **Slug-safety on source slug** carryover from v1.0.1 + v1.1.x. Commas in bundle paths still present.
- **Atom domain validation in renderer.** Spec §6.4 called for `BridgeCardRenderer.validate()` to check "atoms in different domains" and `ConvergenceCardRenderer.validate()` to check "≥3 distinct domains." Both checks live upstream in the strategy code instead. Renderer is not self-protecting against hand-crafted same-domain briefs.

