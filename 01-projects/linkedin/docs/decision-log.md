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

---

## 2026-05-26 — v1.2.1: friction + tldr hygiene + strategy-aware THESIS

Three-item follow-up landing the v1.2 cleanup items. Branch `feat/linkedin-engine-v1.2.1`, 4 commits, 110/110 tests pass.

### Item 1: friction kill

- `01-projects/linkedin/bin/draft-post` shell wrapper bundles `PYTHONPATH=src`, `LINKEDIN_ATOM_SOURCE`, `LINKEDIN_PROJECT_ROOT`, `LINKEDIN_BRAND_SPEC` and forwards args to `python3 -m cli.draft_post`. Usable from any working directory.
- `.gitignore` updated to whitelist `01-projects/linkedin/bin/` and `01-projects/linkedin/scripts/`.
- `01-projects/linkedin/CLAUDE.md` "How to run" section rewritten with three invocation tiers (slash command for Claude Code, `./bin/draft-post` for terminal, raw `python -m cli.draft_post` only when debugging the wrapper). Explicit note that pasting env-var prefixes means "you're doing it wrong."
- Verified by running all v1.2.1 smokes through `./bin/draft-post`. No multi-line env-var pasting at any point.

Commit `eeaaec5`.

### Item 2: tldr re-cap

Eleven atoms in `02-knowledge/` had pre-truncated tldrs ending in `…` (the v1.1.1 safety-net signature). Renderer reads what the atom file holds, so the truncation surfaced as incomplete sentences in convergence funnel cards.

- Tightened the `TldrFiller.SYSTEM_PROMPT` to target 60 chars with 80 as the hard cap, plus an explicit "draft, count, rewrite shorter, aim short" instruction.
- Added `01-projects/linkedin/scripts/recap_tldrs.py` maintenance script: scans the vault for `…`-ending tldrs and re-runs `TldrFiller`. Cost: ~$0.001 per atom on Haiku.

Findings:
- Even with the tightened prompt, Haiku consistently overshoots 80 chars and the safety net cuts with `…` again. 8 of 9 first-pass regenerations still came back truncated.
- Hand-fixed all 9 atoms from the first pass + 2 more discovered during the v1.2.1 verification smoke (filler-generated truncations from the v1.2 live smokes that the initial scan missed): 11 total. All complete sentences ≤80 chars now.
- Three additional atoms surfaced by a second convergence smoke had no `tldr` at all (the strategy picks based on cooldown rotation; fresh atoms = fresh fill calls). Pre-loaded clean tldrs by hand before render to dodge the Haiku-overshoot path entirely.

Commit `5195cb6`.

### Item 3: strategy-aware THESIS

Added `CONVERGENCE_THESIS_OVERRIDE` to `text_generator.py`. `_compose_system_prompt(strategy)` now appends both `CLAIM_TAG_RULE` and the THESIS override when the strategy is `convergence_finder`. The override explicitly tells the LLM "do not put the aphorism inside <THESIS>; do not put the framing inside <CLAIM>; the visual depends on the role split."

Two new tests in `test_text_generator.py`: one asserts the override fires only for convergence, the other asserts the override mentions framing routing.

Smoke result: CLAIM correctly held a synthesis takeaway ("Whenever a domain matures, it converges on the same answer..."). THESIS still tended toward aphorism rather than the explicit framing line. The LLM's bias toward "aphorism in THESIS" is strong enough that the override is competing rather than dominating.

User accepted this as the natural shape: "aphorism on top, synthesis below reads fine." The original v1.2 user complaint (CLAIM holding the framing observation, reading backwards) is fully resolved. Pushing further to force the framing line into THESIS is treated as v1.2.2 work if needed.

Commit `6814312`.

### Final state

- Branch: `feat/linkedin-engine-v1.2.1` with 4 commits.
- Tests: 110/110 pass (108 from v1.2 + 2 new for THESIS override).
- Vault: 11 truncated tldrs cleaned + 3 missing tldrs pre-loaded = 14 atoms touched, all complete-sentence tldrs.
- Engine: tighter TldrFiller prompt; CONVERGENCE_THESIS_OVERRIDE constant; new helper script `scripts/recap_tldrs.py`.
- Wrapper: `bin/draft-post` ships.

### v1.2.2 follow-ups (not blocking merge)

- **TldrFiller retry-on-overshoot.** Haiku overshoots the 80-char cap on ~90% of generations even with the tightened prompt. Safety-net truncation produces `…` endings. Fix: detect overshoot (pre-cut response > 80 chars), call again with "rewrite in under 50 chars" follow-up, accept whichever shorter result lands. Or: switch to Sonnet for tldr fills (more reliable, ~3x the cost per atom but still trivial).
- **THESIS override needs more force.** Current override is the last block in the system prompt but loses to the universal "standalone aphorism" instruction earlier in `VOICE_SYSTEM_PROMPT`. Options: edit the THESIS rule itself to be strategy-aware via prompt assembly (replace the line for convergence rather than append an override); or accept that "aphorism on top, synthesis below" is the natural shape and remove the override.
- **Moving-target truncation.** As long as the filler is unreliable, every smoke with fresh atoms can introduce new truncated tldrs. The retry-on-overshoot fix above is the structural answer; until then, the recap script is the maintenance pass.
- Carryover from v1.2: `--reset-cooldowns` flag, slug-safety, `atom_card.html.j2` migration to shared CSS partial, renderer-side domain validation.

---

## 2026-05-26 — v1.2.2: TldrFiller upgrade + accept aphorism-on-top shape

Two-item follow-up resolving the v1.2.1 structural concerns. Branch `feat/linkedin-engine-v1.2.2`, 2 commits, 114/114 tests pass.

### Item 1: TldrFiller switches to Sonnet + retry-on-overshoot

The v1.2.1 finding was that Haiku consistently overshoots the 80-char cap even with the tightened prompt, producing `…` truncations on ~90% of generations. v1.2.2 fixes this two ways:

- **Default model upgraded** from `claude-haiku-4-5-20251001` to `claude-sonnet-4-6`. Sonnet follows length constraints more reliably; cost per atom rises from ~$0.001 to ~$0.003, still trivial for a vault-scale operation.
- **Retry-on-overshoot safety net.** If the first response would trigger the truncation safety net (length > 80 chars after cleaning), the filler issues a second call with `RETRY_PROMPT_SUFFIX` ("Rewrite in under 50 characters. Cut every word that is not load-bearing."). The `_pick_better` helper then chooses between the two responses, preferring complete sentences within the cap.
- New behavior is testable. Five new unit tests in `test_tldr_filler.py` cover: default model is Sonnet, retry fires only on overshoot, retry-call prompt includes the under-50-chars instruction, retry picks the shorter complete sentence, and the safety-net truncation still applies when both responses overshoot (rare).

Cost decision: belt + suspenders rather than either alone. Sonnet is the primary; retry catches the tail.

Commit `0c35004`.

### Item 2: Remove CONVERGENCE_THESIS_OVERRIDE

The v1.2.1 override was meant to push the THESIS into a framing-observation role for convergence posts. In practice the LLM's bias toward "aphorism in THESIS" was strong enough that the override competed without winning. User accepted "aphorism on top, synthesis below" as the natural convergence layout in the v1.2.1 close.

The override is deleted in v1.2.2. `CLAIM_TAG_RULE` alone is sufficient to keep framing-lines out of the CLAIM slot, which was the original v1.2 fix. The two v1.2.1 tests asserting the override exists are removed and replaced with one test that asserts the override has been removed and the convergence prompt is exactly `VOICE_SYSTEM_PROMPT + CLAIM_TAG_RULE`.

Commit `6415c14`.

### v1.2.2 smoke

Ran `convergence_finder --topic=feedback` via `./bin/draft-post`. The strategy picked three atoms with no existing tldrs (`shallowing-hypothesis`, `npd-for-ai`, `door-shut-door-open`), which exercised the Sonnet-driven filler end-to-end.

Sonnet results (all three first-try, no retries fired):
- `shallowing-hypothesis`: "Habitual scrolling trains shallow processing that undermines deep reading." (75 chars)
- `npd-for-ai`: "AI product development adapts classic NPD steps for ML data and modeling needs." (80 chars exact)
- `door-shut-door-open`: "Draft alone first, then revise with audience feedback in mind." (62 chars)

All complete sentences within cap. No `…`. Funnel cards rendered clean.

THESIS: "Every creative discipline eventually invents a protocol for when the door opens." (aphorism, at top)
CLAIM: "Feedback is a dosage problem, not a quality problem." (synthesis, in panel)

User feedback: "visually looks great. the text slumped me. it's not bad i just didnt get it."

### The text-coherence finding (NOT a v1.2.2 issue)

The user's "didn't get the message" feedback surfaced a real concern that is upstream of the engine: `convergence_finder` picks atoms by tag overlap, not by semantic coherence. The three `feedback`-tagged atoms came from substantially different domains (attention/scrolling, AI product methodology, creative drafting workflow) and represented different *kinds* of feedback. The LLM strained to find a meta-synthesis ("feedback is a dosage problem") that fit all three, producing text that reads strained because the underlying convergence is strained.

Side observation: the CLAIM used contrastive framing ("dosage problem, *not* a quality problem"), which is exactly what the v1.0.1 voice linter rule catches. We force-bypassed during smoke; an actual post would require editing.

These are strategy-design concerns, not engine bugs. v1.2.2 ships with the engine improvements intact.

### Final state

- Branch: `feat/linkedin-engine-v1.2.2` with 2 commits.
- Tests: 114/114 pass (110 from v1.2.1 + 5 new TldrFiller + 1 new THESIS-override-removed minus 2 v1.2.1 override tests).
- Engine: TldrFiller default is Sonnet with retry; CONVERGENCE_THESIS_OVERRIDE removed.
- Vault: 3 newly-touched atoms (`shallowing-hypothesis`, `npd-for-ai`, `door-shut-door-open`) gained clean Sonnet-generated tldrs during smoke.

### v1.2.3+ follow-ups (not blocking)

- **Convergence atom-coherence scoring.** Tag overlap is necessary but not sufficient. Options: embed atoms and require minimum cosine similarity across the chosen trio; or require LLM-judged coherence after candidate selection; or curate topic-to-atom-set mappings for the topics worth posting about. v1.3 territory.
- **Voice linter prompt-time reinforcement.** Contrastive framing rule is in the prompt and the linter catches violations post-hoc, but the model still produces them ~10% of the time. Consider a CLAIM-specific reinforcement that re-states the prohibition right where the synthesis sentence lands.
- Carryover from v1.2.1: `--reset-cooldowns` flag, slug-safety, `atom_card.html.j2` migration to shared CSS partial, renderer-side domain validation.

---

## 2026-05-26 — v1.3 design: atom-coherence scoring for convergence_finder

Resolves the v1.2.2 finding ("convergence picks atoms by tag overlap, not semantic coherence"). Approach picked: embedding cosine similarity, score candidate triples by minimum pairwise similarity. Brainstorm closed on six decisions. Full implementation plan in `2026-05-26-v1-3-implementation-plan.md`.

### Decisions

| Question | Choice | Rationale |
|---|---|---|
| Embedding provider | OpenAI `text-embedding-3-small` (1536 dims) | Reuses the `OPENAI_API_KEY` already in `.env` for open-brain MCP. ~$0.02 one-time vault embed, near-zero per-finder cost. Quality is sufficient for triple ranking. Only new dep is the `openai` Python package. |
| Embed scope | `title + body` per atom | Title anchors the semantic gist (e.g., "Child Development Trust"); body adds context. Robust against body-language drift toward domain-specific framing. |
| Cache + lifecycle | Lazy, single JSON file at `01-projects/linkedin/.cache/atom-embeddings.json`, gitignored. Schema: `{slug: {body_hash, embedding}}`. Hash mismatch re-embeds. | Matches the engine's on-demand pattern (everything is lazy/per-invocation). Easy to inspect, easy to nuke. Hash-keyed invalidation handles atom edits cleanly. |
| Threshold | `0.35` default, configurable via env var `LINKEDIN_CONVERGENCE_MIN_SIM` or per-call param. Log min-sim to `logs/state.jsonl` each run. | Liberal start that still rejects the v1.2.2 'feedback' failure case (estimated min-sim 0.2–0.3). Tunable for empirical calibration over the first 5–10 smoke runs. |
| Failure mode | Hard `ValueError` with diagnostic payload: best min-sim found, threshold used, slugs of top 3 candidate triples ranked by min-sim. | Surfaces enough info to debug or recalibrate without re-running. No automatic fallback. Engine stays deterministic. |
| Integration | Replace per-domain selection entirely. Enumerate every `(domain-triple × atom-per-domain)` combination, score each by min pairwise cosine, pick highest. Drop graph-connectivity heuristic. | Fixes both "first 3 domains is arbitrary" and "per-domain pick uses the wrong signal" in one move. ~500 candidate triples per topic (cheap math on cached vectors). |

### Combinatorics check

For a topic like 'feedback' (~5 domains, ~3–5 atoms per domain):

- Domain triples: `C(5, 3) = 10`
- Atom triples per domain-triple: 3³ to 5³ = 27 to 125
- Total candidates: ~500
- Per candidate: 3 cosine sims on cached 1536-dim vectors

In-memory, well under 100ms total.

### Architectural impact

New module `src/embeddings/` with three files:

- `provider.py`: `OpenAIEmbedder` wrapping `text-embedding-3-small`.
- `cache.py`: `EmbeddingCache` with hash-based invalidation, JSON persistence.
- `coherence.py`: pure functions for cosine similarity, min-pairwise, triple ranking.

`StrategyContext` gains an optional `embedder: Embedder | None` field. `convergence_finder.generate_brief` is rewritten end-to-end (graph-connectivity ranking removed; coherence ranking added). No changes to other strategies, renderers, voice linter, or text generator.

### What v1.3 explicitly does NOT include

- Coherence scoring for `bridge_finder`. The v1.2.2 failure was convergence-specific; bridges already have a tighter mechanism-edge constraint.
- Topic auto-discovery via clustering.
- Migration to a vector DB or Supabase. Premature at this scale.
- Re-introducing connectivity as a soft tiebreaker or weighted signal. Revisit only if pure coherence ranking surfaces fringe atoms in practice.

---

## 2026-05-27 — v1.3 smoke result

Re-ran the v1.2.2 failure case (`convergence_finder --topic=feedback`) against the new coherence-ranking strategy. Branch tip: `a8aac7b` (5 implementation commits + wrapper dotenv fix).

### Atoms picked

| Slug | Domain | Source/Author |
|---|---|---|
| `transformational-coping` | mental-models | Csikszentmihalyi (flow research) |
| `expectancy-postponement` | philosophy-resilience | Seneca (Stoic letters) |
| `territorial-orientation` | style-voice-craft | Pressfield (creative-war essays) |

### Coherence score

`min_sim = 0.4327` against a threshold of `0.35`. About 24% headroom. The cache populated all candidate atoms on first run; subsequent runs would hit cache for any atom whose body/title hash is unchanged.

### Differs from v1.2.2 pick entirely

v1.2.2 picked `shallowing-hypothesis + npd-for-ai + door-shut-door-open` (attention/scrolling, AI product methodology, creative drafting workflow). All three shared the `feedback` tag but addressed different *kinds* of feedback. v1.3 picks an entirely different trio because the v1.2.2 atoms scored a low min_sim and coherence-ranking surfaced a better candidate.

The new triple all address the same underlying mechanism: **what to do when external feedback is missing or hostile**. Three different traditions (psychology, Stoic philosophy, creative-process literature) converging on the same problem from different angles. Convergence is now semantic not just tag-shared.

### Generated post

Mocked Anthropic in tests; this smoke uses real Anthropic with the live VOICE_SYSTEM_PROMPT. Sonnet returned (verbatim):

> Three atoms collided in my second brain this week, each from a different shelf, each answering the same question: what do you do when external feedback goes silent or sour?
>
> Csikszentmihalyi, the flow researcher, calls it Transformational Coping. A "dissipative structure of the mind" that takes a brutal event and metabolizes it into a challenge that strengthens the self.
>
> Seneca, the Stoic letter-writer, attacks the opposite failure mode: Expectancy, the habit of postponing life by hanging it on tomorrow. The feedback you're waiting for is the trap.
>
> Pressfield, who writes on the creative war, names the cure Territorial Orientation. You define yourself by the turf you work, a gym, a piano, a page, and sustenance comes from effort, not applause.
>
> When the world stops clapping, you either transform the input, refuse to wait on it, or stop needing it.
>
> Three centuries apart. One muscle.
>
> Which of the three is your default move?

### User feedback

"i like this text a lot more"

The v1.2.2 smoke pulled "the text slumped me. it's not bad i just didnt get it." The v1.3 pick is digestible because the three atoms genuinely converge on one mechanism, not three different things sharing a label.

### Calibration note

Threshold 0.35 worked first try. The winning triple landed at 0.4327, comfortably above. No env-var override needed. Recommend keeping the default for the next 5–10 runs; if multiple legitimate convergence topics start producing threshold errors, lower to 0.30. If multiple ship-worthy posts come from triples in the 0.35–0.45 band (as this one did), the threshold is correctly calibrated.

### Wrapper follow-up landed in the same branch

The smoke surfaced a missing piece: `bin/draft-post` did not source the vault dotenv, so `OPENAI_API_KEY` could not reach the Python process. Fixed in commit `a8aac7b`. The slash command at `.claude/commands/draft-post.md` duplicates the env wiring and has the same gap. Not blocking; logged as a v1.3.1+ follow-up.

### v1.3+ follow-ups (not blocking)

- `.claude/commands/draft-post.md` should delegate to `./bin/draft-post` instead of duplicating env wiring.
- Carryover from v1.2.x: `--reset-cooldowns` flag, slug-safety on source slug, `atom_card.html.j2` migration to shared CSS partial, renderer-side domain validation, voice-linter contrastive-framing reinforcement at CLAIM-time.
- After 5–10 more convergence smokes, audit `logs/state.jsonl` (via `brief.strategy_params.min_sim`) and decide whether threshold needs adjustment.

