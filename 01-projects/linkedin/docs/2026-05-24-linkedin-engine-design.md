# LinkedIn Content Engine — Design Spec

**Date:** 2026-05-24
**Version:** v1 (design)
**Status:** Approved (brainstorm), pending planning
**Owner:** nwogbo_gozzy
**Companion docs:**
- Command reference: `01-projects/linkedin/docs/command-reference.md`
- Library of Alexandria v2 prompt: `05-resources/prompts/library-of-alexandria-v2.md`
- Source feasibility report: `~/Downloads/LinkedIn-Safe Content Automation and High-Leverage Visual Formats.md`

---

## Executive summary

An on-demand LinkedIn content engine that draws from the second-brain atom graph and produces post-ready bundles (text + visual) in one of four post patterns. Each post reads as "insight + visible system" — the atom graph is the differentiator, not hidden infrastructure. The engine ships in versioned phases: v1.0 produces text + atom-graph diagrams (workhorse), v1.1 adds carousels, v1.2 adds Higgsfield-generated branded video. v2 swaps filesystem backlog for Supabase storage and adds a Buffer/Metricool scheduler. Compliance boundary per LinkedIn ToS: no direct API automation — last-mile posting via native scheduler (v1) or authorized third-party scheduler (v2). Job-search visibility play in the short term, durable content infrastructure in the long term.

---

## 1. Goal & strategic framing

### 1.1 What we're building

An engine that:
1. Reads atoms (concepts, frameworks, principles, connections) from `02-knowledge/`.
2. Runs one of four post-generation strategies to produce a candidate post.
3. Drafts body text obeying CLAUDE.md voice rules.
4. Renders a visual asset in one of three tiers (diagram, carousel, branded video).
5. Writes a post-ready bundle to the local backlog for human review and posting.

### 1.2 Strategic positioning

Each post reads as **"insight + visible system."** The atom graph is the differentiator — posts name the source ("my second brain surfaced an unexpected tie between X and Y") and the diagram visualizes the actual atoms. Two payloads per post: the idea itself, and the implicit "I built the system that found this."

### 1.3 Why this differentiates

Most LinkedIn posts are *takes*. This engine produces *pattern discovery* — two or more ideas that shouldn't touch but do, rendered visually, signed by the system that spotted them. Hard to copy without the underlying atom graph. As atoms grow, the engine produces richer connections; readers can suggest atoms or connections in comments, feeding the graph back.

### 1.4 Success criteria

1. **Inbound network signal** — recruiters / connections messaging in response to posts.
2. **Engagement quality** — saves and substantive comments over likes.
3. **Reader-contributed connections** — at least one outside-contributed connection or source per month after launch.
4. **Internal craft** — a 10+ post backlog of work the author would publish unedited.

### 1.5 Non-goals

- Multi-platform syndication (Twitter/X, Threads) — possible later, optimized for LinkedIn first.
- Direct LinkedIn API integration — banned per ToS, never in scope.
- Engagement automation (auto-comment, auto-DM) — banned per LinkedIn ToS, never in scope.
- Cross-posting the atom graph publicly as a browsable web product — interesting separate project, not this one.

---

## 2. Architecture

### 2.1 Component inventory

| # | Component | Status | Notes |
|---|---|---|---|
| 1 | **Atom store** | Existing | `02-knowledge/` + Open Brain Supabase. Read-only for this engine. |
| 2 | **Strategy modules** | New (v1.0) | Four modules sharing one interface. See §4. |
| 3 | **PostBrief object** | New (v1.0) | Internal contract carrying atoms, angle, visual tier, brief, state. See §3. |
| 4 | **Text generator + voice linter** | New (v1.0) | Claude API call constrained by CLAUDE.md §3 voice rules. |
| 5 | **Visual renderer (3 tiers)** | New, phased | Tier 1 (v1.0), Tier 2 (v1.1), Tier 3 (v1.2). See §5. |
| 6 | **Bundle writer / storage adapter** | New (v1.0) | Filesystem in v1; same schema, Supabase in v2. |
| 7 | **State store** | New (v1.0) | Atom usage, connection usage, strategy history, angle embeddings, rejections, approvals. |
| 8 | **Approval gate + scheduler service** | v2.0 | Telegram approval surface + Buffer/Metricool API. |
| 9 | **Analytics loop** | v2.5 | Per-post performance pulled from scheduler/LinkedIn analytics. |

### 2.2 Data flow (one post, v1.0)

```
slash command (/draft-post)
  → strategy module reads atoms + connections
  → emits PostBrief (atoms + angle + provisional visual tier + visual brief)
  → text generator drafts body text
  → voice linter runs; warnings annotated, hard fails block
  → ★ GATE 1 (review): user approves/edits text, locks visual tier
  → renderer (selected tier) produces asset
  → bundle writer creates folder with text.md + asset + meta.json
  → ★ GATE 2 (final): user reviews full bundle
  → status: ready_to_post
  → user posts manually via LinkedIn native scheduler
  → status: posted (with permalink stored)
```

Gate 1 is the expensive gate — it sits *before* the renderer fires, so Higgsfield credits never burn on text the user would have rejected. Gate 2 is the cheap "final look at the whole package" pass.

### 2.3 Pluggable seams

Designed so v1.x → v2 transitions are plug-in, not rewrite:

- **Strategy modules** behind `generate_brief(filter_params) → PostBrief`.
- **Visual renderers** behind `render(brief) → RenderResult`.
- **Storage adapter** behind `write(brief, assets)` and `read(slug)` — filesystem in v1.0, Supabase in v2.0, same calls.
- **Posting backend** — manual in v1.x, scheduler API in v2.0.
- **Brand spec** — external file consulted by all renderers; not owned by this engine.

### 2.4 File layout

```
01-projects/linkedin/
├── CLAUDE.md                # project-specific instructions; portable for extraction
├── brand-spec.md            # placeholder in v1; symlinked or pointed to brand revamp output
├── src/                     # code lives here (Python + Node where needed)
│   ├── strategies/
│   ├── renderers/
│   ├── storage/
│   ├── linter/
│   └── cli/                 # slash command implementations
├── docs/
│   ├── 2026-05-24-linkedin-engine-design.md   # this file
│   ├── command-reference.md
│   ├── schema.md
│   └── decision-log.md
├── backlog/                 # v1.0 storage; one folder per post
│   └── [YYYY-MM-DD]-[slug]/
│       ├── meta.json
│       ├── text.md
│       └── <asset files>
├── state/
│   ├── atom-usage.json
│   ├── connection-usage.json
│   ├── strategy-history.jsonl
│   ├── angle-embeddings.jsonl
│   ├── approvals.jsonl
│   └── rejections.jsonl
├── logs/
│   ├── state.jsonl
│   ├── cost.jsonl
│   └── errors.jsonl
└── tests/

.claude/skills/video/        # vault-level harvested skills
├── higgsfield-prompt/
├── higgsfield-cli/
└── remotion/

.claude/skills/linkedin/     # project-scoped skill
└── visual-discipline/

.claude/commands/
├── draft-post.md            # slash command definition
└── linkedin-status.md
```

### 2.5 Portability

The engine is designed to function standalone when promoted to portfolio or extracted to its own repo:

- **Project-level `CLAUDE.md`** documents conventions without depending on second-brain context.
- **Internal logging** in `01-projects/linkedin/logs/` rather than only `system-events.jsonl`.
- **Configurable atom source path** — engine accepts a config value, defaults to `02-knowledge/`.
- **Brand-spec as external dependency** — pointer, not embedded.

---

## 3. Data model

### 3.1 PostBrief — central object

`PostBrief` is the internal contract carrying one post through the pipeline. Serialized as `meta.json` in v1 filesystem; same shape as a `linkedin_drafts` row in v2 Supabase.

```yaml
PostBrief:
  # Identity
  id: uuid
  slug: kebab-case-string
  created_at, updated_at: iso8601

  # Strategy + atoms
  strategy: source_spotlight | two_atom_bridge | cluster_reveal | convergence_finder
  strategy_params:
    # strategy-specific subobject; see §4 per-strategy detail
  atoms_used:
    - {slug: string, role: primary | auxiliary, source: string}

  # Content
  angle: string                  # the thesis the post advances
  text_constraints:
    voice_rules: [from CLAUDE.md §3]
    word_range: [min, max]
  draft_text: string             # populated by text generator
  approved_text: string          # populated at Gate 1
  edit_delta:                    # diff between draft and approved
    diff: string                 # unified diff
    magnitude: minor | moderate | major
    types: [voice_correction, factual_edit, restructure, ...]

  # Visual
  visual_tier: 1_diagram | 2_carousel | 3_video
  visual_brief:
    # tier 1
    diagram_layout: bridge | constellation | cluster
    diagram_emphasis: string
    # tier 2
    slide_count: int             # 6-8 enforced
    slide_outlines: [string]
    image_augmentation: bool     # whether to call Higgsfield for slide imagery
    # tier 3
    style_variant: string        # which Higgsfield prompt skill variant
    seedance_brief:              # 8-block canonical Seedance structure
      hook: string
      beat_timeline: [{second: int, action: string}]
      camera: string
      lighting: string
      sound: string
      asset_refs: [string]       # ≤12 total (9 image, 3 video, 3 audio)
      platform: linkedin_feed | linkedin_reel
      target_lines: int          # 15-25
    remotion_brief:
      composition_id: string
      duration_seconds: int      # ≤15 enforced
      brand_frames: [...]
      captions: [{start: float, end: float, text: string}]
    text_video_relationship: two_registers | complementary | video_carries
  visual_asset_paths: [string]   # populated after rendering

  # State machine
  status: drafting → text_ready → gate1_approved
        → rendering → gate2_pending → ready_to_post
        → posted → archived
  status_history: [{status, timestamp, actor}]

  # Series + metadata
  series: string?                # nullable; for recurring themes
  topic_tags: [string]
  target_platforms: [linkedin_profile]

  # v2 fields (nullable in v1)
  scheduled_time: iso8601?
  scheduler_platform: buffer | metricool | null
  scheduler_post_id: string?
  published_url: string?

  # v2.5 fields (nullable until analytics lands)
  metrics:
    impressions: int
    reactions: int
    comments: int
    saves: int
    recruiter_inbound: bool      # manually flagged or NLP-detected
    fetched_at: iso8601
```

### 3.2 State machine

Status transitions are the audit log. Every transition writes to `logs/state.jsonl` with timestamp and actor (user, engine, scheduler).

```
drafting → text_ready          (text generator completes)
text_ready → gate1_approved    (Gate 1 — user approves text + tier)
text_ready → rejected           (Gate 1 — user kills)
gate1_approved → rendering      (renderer starts)
rendering → gate2_pending       (renderer succeeds)
rendering → gate1_approved      (renderer fails; user can edit brief and retry)
gate2_pending → ready_to_post   (Gate 2 — user approves bundle)
gate2_pending → rejected        (Gate 2 — user kills)
ready_to_post → posted          (user marks posted; permalink stored)
ready_to_post → scheduled       (v2.0+ — pushed to scheduler)
scheduled → published           (v2.0+ — scheduler confirms)
posted | published → archived   (after analytics retention window)
```

### 3.3 Hard guardrails (schema validator)

Two categories: **technical caps** (hard-fail, the tool literally cannot do otherwise) and **creative defaults** (soft-warn, user decides).

**Technical hard caps:**
- **Tier 1:** no more than 6 nodes in diagram, every node has ≥1 edge.
- **Tier 2:** ≤8 slides, ≤50 words per slide, ≤9 Higgsfield-augmented images if applicable.
- **Tier 3:** ≤12 total asset refs (Higgsfield cap), ≤15s duration, 720p, body text always present (never video-only).
- **All tiers:** voice linter style rules pass on `approved_text` before status can advance past Gate 1 (em-dash, contrastive framing, exclamation count — these are style hard-fails; see §4.3).

**Creative defaults (soft warn outside range):**

| Tier | Target word range | Rationale |
|---|---|---|
| Tier 1 (diagram) | 80–200 | Diagram carries the visual; text frames it |
| Tier 2 (carousel) | 60–150 | Body is the in-feed hook; substance lives on slides |
| Tier 3 (video) | 80–200 | Text frames the video; LinkedIn UX shows ~3 lines before cutoff |
| Convergence-finder posts | 150–350 | Walking through 3+ domains needs more room |

**Extreme outliers (still hard-fail):** < 30 words or > 600 words — almost certainly a broken generation, not a creative choice.

The linter surfaces word count as: *"word count: 215. Target 80–200 for Tier 1. Soft warn — review before advancing."* User decides whether to advance, edit, or regenerate. Length is creative judgment; voice is not.

### 3.4 v2 Supabase tables

When v2 lands, same shape lifted to Supabase:

- `linkedin_drafts` — PostBrief rows
- `linkedin_schedule` — scheduler-specific state
- `linkedin_analytics` — time-series metrics
- `linkedin_series` — recurring themes (Systems Sketches, Funnel Autopsies, etc.)
- `linkedin_atom_usage` — atom cooldown tracking
- `linkedin_connection_usage` — connection cooldown tracking
- `linkedin_rejections` — rejection log
- `linkedin_approvals` — approval log with edit_delta and post performance

---

## 4. Post-generation pipeline

### 4.1 Strategy modules

Four modules behind one interface: `generate_brief(filter_params) → PostBrief`. Each reads atoms and connections, populates `strategy`, `atoms_used`, and `angle`, and returns a brief in `status: drafting`.

#### 4.1.1 `source_spotlight`

- **Input:** source name (e.g., "Nate B. Jones"), atom_count (default 3).
- **Logic:** Filter atoms where `origin` / `source` field matches → sample N (recency-weighted) → fetch outgoing connections for each → find a secondary domain that touches ≥2 of the N atoms.
- **Angle template:** *"Three ideas from [source] all touch [Y]. Here's why that matters."*
- **Default visual tier:** Tier 1 (diagram shows source's atom subgraph).

#### 4.1.2 `two_atom_bridge`

- **Input:** `atom_a` and `atom_b` slugs (or `--auto` = pick two far-apart by domain tag with non-empty tag overlap).
- **Logic:** Load both atoms → check for existing typed connection atom; if present, use its claim → if absent, surface shared-concept candidates by tag overlap → user picks one.
- **Angle template:** *"[Domain A] and [Domain B] are doing the same job. The shared mechanism is [X]."*
- **Default visual tier:** Tier 1 (diagram shows the bridge edge with its type).
- **Guardrail:** requires atoms from different domain tags — no same-domain bridges.

#### 4.1.3 `cluster_reveal`

- **Input:** timeframe (default last 30 days) or `cluster_anchor` tag.
- **Logic:** Query atoms added/updated in window → cluster by wiki-link density + tag overlap → if a cluster of ≥4 atoms exists without an explicit naming atom, name the theme.
- **Angle template:** *"I keep capturing notes about [X] without realizing. Here's the pattern."*
- **Default visual tier:** Tier 2 (carousel walks through the cluster).
- **Guardrail:** requires ≥4 atoms — smaller clusters don't reveal a pattern.

#### 4.1.4 `convergence_finder` (new strategy)

- **Input:** topic (e.g., "trust", "feedback", "naming things").
- **Logic:** Find atoms across N distinct domain tags that all touch the topic, prioritizing atoms connected via `mechanism` or `analogical` connection types.
- **Angle template:** *"[Topic] shows up in [domain A], [domain B], and [domain C]. Three solutions to the same problem."*
- **Default visual tier:** Tier 2 (convergence posts work better as carousels — they walk through 3+ atoms).
- **Guardrail:** requires ≥3 distinct domain tags represented; fewer = strategy fails with gap signal.

### 4.2 Text generator

- **Input:** `PostBrief` with `angle` + `atoms_used` + `text_constraints` filled.
- **Implementation:** Claude API call (or in-conversation if running inside the slash command).
- **System prompt:** loads CLAUDE.md §3 voice rules verbatim — no em-dashes, no AI watermarks, no contrastive framing ("not as X, but as Y"), active voice default, max 1 exclamation per 150 words.
- **User prompt:** constructed from the brief — angle, atoms (with summaries), word range, framing instruction ("visible-system: name 'my second brain' or atom-graph as the source").
- **Output:** `draft_text`, written into the brief. Status → `text_ready`.

### 4.3 Voice linter

Runs immediately on `draft_text`. Annotations attach to the brief; hard failures block Gate 1 advance unless overridden with `--force`.

| Check | Behavior |
|---|---|
| Em-dash detected | Hard fail (objective AI tell) |
| Contrastive framing pattern ("Not X, but Y", "Not just X, X+") | Hard fail (objective AI tell) |
| Exclamation count > 1 per 150 words | Hard fail (objective style violation) |
| Word count < 30 or > 600 | Hard fail (almost certainly broken output) |
| AI watermark words ("delve", "tapestry", "navigate the complex", etc.) | Soft warn |
| Word count outside tier target range (§3.3) | Soft warn |
| Active-voice ratio < 80% | Soft warn |
| Triple-em sentence parallelism (three-clause balance) | Soft warn |
| Mirroring phrases from CLAUDE.md user.md flagged patterns | Soft warn |

**Principle:** the linter is strict on *objective AI tells* (these are wrong by rule, no judgment needed) and advisory on *creative judgment* (length, rhythm, register — user decides). Soft warns annotate the brief without blocking; hard fails block Gate 1 advance unless `--force` overrides.

The linter is a Python module reading rules from `01-projects/linkedin/src/linter/rules.yml` so rules are tunable without code changes.

### 4.4 Gate 1 — text + tier review

- User opens the bundle folder. Reads `text.md`. Edits in place if needed.
- Confirms or changes `visual_tier`. Default tier from strategy is a suggestion only.
- Advances via slash command OR conversational instruction. Engine writes `approved_text`, computes `edit_delta`, advances status, atoms enter persistent cooldown.

### 4.5 Atom selection guardrails

- `source_spotlight` excludes atoms used as `primary` in last 30 days.
- `two_atom_bridge` requires atoms from different domain tags.
- `cluster_reveal` requires ≥4 atoms.
- `convergence_finder` requires ≥3 distinct domain tags.

---

## 5. Visual rendering layer

The visual layer is where the "wait, how did they make that" hook lives. Three pluggable renderers behind `render(brief) → RenderResult`. Each tier maps to a different infrastructure and a different post archetype.

### 5.1 Tier 1 — Atom-graph diagram (workhorse, ~80% of posts)

- **Stack:** Python + `graphviz` or `d3-node` (Node headless) for SVG output. Deterministic. No external API calls.
- **Inputs:** atoms (2–6) + connection edges + `connection_type` per edge (drives edge styling) + `diagram_layout` (`bridge` / `constellation` / `cluster`).
- **Output:** PNG (LinkedIn-feed) + SVG (vector source). Both written to bundle folder.
- **Why workhorse:** cheap, deterministic, visualizes the actual atoms (visible-system positioning), scales infinitely as graph grows.

**Anti-pattern checks (deterministic, impeccable-style):**
- No center-gradient backgrounds.
- No more than 6 nodes (cognitive load).
- Edge labels mandatory when `connection_type` ≠ `general`.
- No floating nodes (every node has ≥1 edge).
- Aspect ratio locked to 1:1 or 4:5.

### 5.2 Tier 2 — Carousel PDF (deep-dive, ~15% of posts)

- **Stack:** Satori (Vercel — JSX → SVG → PDF) or React-PDF. Decision deferred to v1.1 planning based on layout complexity. *Not Remotion* — wrong tool for static multi-page PDFs.
- **Slide structure:**
  - Slide 1: hook + atom names
  - Slides 2 to N-1: one connection per slide
  - Final slide: synthesis + comment-prompt CTA
- **Optional Higgsfield image augmentation:** off by default; when on, prompts from `higgsfield-prompt-construction` skill (image mode).
- **Hard caps:** 6–8 slides, ≤50 words/slide, ≤9 generated images if augmented.

### 5.3 Tier 3 — Branded video (rare, ~5% of posts, ≤2-3/month)

The critical split: **Higgsfield generates pixels, Remotion composites brand.** Together: Higgsfield handles *what's on screen*; Remotion handles *how it's framed and branded*. That's how the output stops looking like generic AI video and starts looking like the author's.

**Two formats:**

1. **Problem-persona ad-style.** AI-rendered person embodying the pain point the post discusses. Higgsfield CLI invoked via `higgsfield-prompt-construction` skill (style variant `problem-persona-ad`, forked from `AKCodez/higgsfield-claude-skills/01-cinematic`). 8-block canonical Seedance prompt: 2-sec hook → beat timeline → camera → lighting (with Kelvin) → sound → asset refs → platform → ~20 lines total. Quantify everything.

2. **Atom-graph reveal animation.** The Tier 1 diagram animated into existence as a short reel. Pure Remotion, no Higgsfield. Used for "big reveal" posts. Deterministic, cheap.

**Remotion composition layer (on top of Higgsfield output):**
- Title card (atom names + handle, 1.5s)
- Subtitle captions throughout (from `approved_text` key claim)
- End card (atom-graph thumbnail + comment CTA)
- Brand frame edges (consulted from brand-spec)

**Text-video relationship:** always paired with body text (LinkedIn's UX hard-favors text+media over pure video). Relationship parameter per post — defaults to `complementary`, overridable to `two_registers` or `video_carries`. Marked as experimental, iterate on what lands in production.

**Cost gating:** Tier 3 cannot fire without Gate 1 approval. Pre-flight prompt shows estimated credit cost before CLI invocation. Failed renders logged to `01-projects/linkedin/logs/cost.jsonl` for monthly burn visibility.

### 5.4 Skill harvest (vault-level deliverable, v0)

Four skills harvested and polished to 2025-26 standard. First three live in `.claude/skills/video/` — vault-level assets, reusable across projects. Fourth is project-scoped.

| Skill | Lives in | Source repos | Purpose |
|---|---|---|---|
| `higgsfield-prompt-construction` | `.claude/skills/video/higgsfield-prompt/` | `AKCodez/higgsfield-claude-skills/01-cinematic`, `beshuaxian/higgsfield-seedance2-jineng`, `dexhunter/seedance2-skill` | Build 8-block Seedance prompts from a brief |
| `higgsfield-cli-execution` | `.claude/skills/video/higgsfield-cli/` | `AKCodez/higgsfield-claude-skills` Playwright skills (adapted to local CLI) | Invoke CLI, handle outputs, retry, manage asset cache |
| `remotion-composition` | `.claude/skills/video/remotion/` | `remotion-dev/skills` (drop-in, light frontmatter polish) | Author Remotion compositions from a brief |
| `linkedin-visual-discipline` | `.claude/skills/linkedin/visual-discipline/` | Inspired by `pbakaus/impeccable` + `Leonxlnx/taste-skill` + `alchaincyf/huashu-design` | Anti-pattern rules + brand-spec consultation for all three tiers |

Style variants (e.g., `problem-persona-ad`, `documentary-explainer`, `cinematic-product`) live as forks of the prompt skill, per `beshuaxian`'s 15-style-variant pattern.

Skill standard (2025-26):
- **Frontmatter:** `name`, `description` (trigger-keyword-dense for auto-invocation), `when_to_use`, `allowed-tools`, `version`.
- **Body:** purpose → trigger conditions → required inputs → numbered step protocol → anti-patterns/rules → 3+ worked examples → output contract.

### 5.5 Brand spec — external dependency

Brand spec is **not owned by this engine**. Renderers consult `brand-spec.md` at a configurable path (default `01-projects/linkedin/brand-spec.md`).

- v1.0 ships with a placeholder brand-spec (deliberately neutral) so the engine builds without blocking on brand work.
- Real brand spec is generated by a separate brand revamp workstream; LinkedIn engine points at the output when ready.
- Once defined, the brand-spec follows the *freeze* pattern (huashu-design): drift requires explicit unlock with logged rationale.

### 5.6 Renderer interface

```python
class Renderer(Protocol):
    tier: int
    def validate(brief: PostBrief) -> list[ValidationError]: ...
    def render(brief: PostBrief) -> RenderResult: ...

@dataclass
class RenderResult:
    asset_paths: list[Path]
    cost: float           # USD spent (Higgsfield)
    duration_s: float
    logs: list[str]
```

Concrete implementations: `DiagramRenderer`, `CarouselRenderer`, `VideoRenderer`. Adding a fourth tier means adding one class, not rewiring the pipeline.

---

## 6. Operations & posting flow

### 6.1 v1.0–v1.2 (manual last-mile)

- `/draft-post` invoked. Bundle written to `01-projects/linkedin/backlog/[YYYY-MM-DD]-[slug]/`.
- Status flows through state machine per §3.2.
- Gate 1 = edit text + confirm tier. Gate 2 = final bundle look. Both via slash command OR conversational instruction.
- When `ready_to_post`: user opens folder, uploads assets + pastes text into LinkedIn's native scheduler in browser. Marks `posted` with `--mark-posted <slug> --url=...`.

**Compliance boundary** (per Perplexity report §1): no automated interaction with `linkedin.com`. v1 manual posting is fully compliant by construction.

### 6.2 v2.0 (approval gate + scheduler API)

- Storage migrates from filesystem → Supabase `linkedin_drafts` table. Same schema, different adapter. One-time migration script lifts existing backlog.
- **Approval surface:** Telegram bot (reuses capture-channel infra). On `text_ready` or `gate2_pending`, bot pings with preview + inline buttons (approve / revise / kill).
- **Scheduler service:** polls `ready_to_post` rows, pushes to Buffer or Metricool via REST API. Compliance: scheduler holds the LinkedIn OAuth; engine never touches `linkedin.com`.
- Status flows extend: `ready_to_post → scheduled → published`.

### 6.3 v2.5 (analytics loop)

- Periodic job pulls per-post metrics (impressions, reactions, comments, saves) from LinkedIn analytics via scheduler API.
- Metrics write to `linkedin_analytics` table as time series.
- `/linkedin-status --stats` surfaces performance breakdowns by strategy, tier, and the four-quadrant approval-vs-performance matrix (see §9.4).

### 6.4 Conversational interface

Slash commands are *triggers and surfaces*. The daily interface is natural language inside Claude Code. Examples:

| Spoken | Engine action |
|---|---|
| *"Kill the third one, angle was too abstract."* | Parse target slug, write rejection with reason, release ephemeral atom locks |
| *"Advance the feedback-loops draft but rewrite paragraph 2 to lead with auth."* | Edit `approved_text`, log edit_delta, flip status, trigger renderer |
| *"What's in the backlog?"* | Same output as `/linkedin-status --backlog` |
| *"Why did you pick those atoms?"* | Return the score breakdown from the last selection run |

Both interfaces write to the same state files. The slash CLI exists for scripting, cron, and explicit/reproducible operations; the conversation is the daily flow.

### 6.5 Logging discipline (all versions)

| Log | Contents |
|---|---|
| `01-projects/linkedin/logs/state.jsonl` | Every state transition with timestamp + actor |
| `01-projects/linkedin/logs/cost.jsonl` | Every Higgsfield call (cost, duration, success) + LLM API spend |
| `01-projects/linkedin/logs/errors.jsonl` | Every render or lint error |

Project-internal logs, not just `system-events.jsonl`. Portable when extracted. Per CLAUDE.md §15, also writes vault-level `system-events.jsonl` + Supabase `permission_log` with `reason` field, for vault-wide audit.

### 6.6 Failure handling

- **Higgsfield CLI fails:** status reverts to `gate1_approved`, error logged, user notified. No silent retries (would burn credits).
- **Voice linter hard fail:** status stays at `text_ready`, blocked from Gate 1 advance unless `--force` override.
- **Scheduler API fails (v2+):** status reverts to `ready_to_post`, error logged, next poll retries with exponential backoff (3 attempts, then halt + ping).
- **Pool exhausted (no eligible atoms):** engine returns suggestion to override cooldown or wait; never silently picks a stale atom.

---

## 7. Build sequencing

Eight phases. v0 is a vault-level prerequisite that benefits other projects too.

| Phase | What ships | Est. effort |
|---|---|---|
| **v0** — Skill harvest + schema update | 4 polished skills in `.claude/skills/`. Updated `03-skills/registry.md`. Atom-front-matter v2.1 with `connection_type` field (8 typed values + `general` fallback). | 3–5 days |
| **v1.0** — Engine core + Tier 1 | `/draft-post` + `/linkedin-status` slash commands. 4 strategy modules. Text generator + voice linter. Diagram renderer. Filesystem backlog. PostBrief schema. State machine. Project-internal logging. `01-projects/linkedin/CLAUDE.md`. Placeholder brand-spec. State files (atom usage, connection usage, rejections, approvals). | 4–6 days |
| **v1.1** — Tier 2 carousels | Carousel renderer (Satori or React-PDF). Slide template (brand-spec-driven). Optional Higgsfield image augmentation (off by default). | 3–4 days |
| **v1.2** — Tier 3 video | Higgsfield CLI invocation. Remotion composition. Two video formats (problem-persona ad, atom-graph reveal animation). Cost gating + pre-flight cost preview. | 5–7 days |
| **v2.0** — Storage + scheduler | Supabase migration. Telegram approval gate. Scheduler service (Buffer or Metricool). Compliance audit checklist. | 4–6 days |
| **v2.5** — Analytics loop | Per-post metrics pull. `linkedin_analytics` table. `/linkedin-status --stats`. Strategy weighting from analytics. | 3 days |
| **v3.0** — Self-learning Hermes skill | Whatever the Hermes self-learning skill turns out to be once user provides the repo. Likely: engine learns from edit_delta and rejection reasons; updates prompt templates. Requires own ideation cycle. | TBD |
| **v∞ — Parallel** | Library of Alexandria v2 corpus ingest. Brand spec revamp. Connection-type backfill. Ongoing, not gating. | Ongoing |

**Time-to-first-post:** v0 + v1.0 = ~7–11 days. After that, posts ship while v1.1+ build in parallel.

---

## 8. Open questions, dependencies, parallel workstreams

### 8.1 Open questions to resolve during planning

1. **Higgsfield CLI versioning + auth model.** Confirm: does the local CLI require API keys per call? Persistent session? Credit cost per video? Affects cost gating logic. Resolve during v1.2 planning.
2. **Satori vs. React-PDF for Tier 2.** Both work. Decide during v1.1 planning based on slide layout complexity needs.
3. **Connection-type retro-tagging.** Existing connection atoms are untyped. Options: (a) leave untyped (default `general`), type new ones going forward, OR (b) run a one-shot Claude-assisted backfill that proposes types. Cost/value tradeoff — defer to v0 planning.
4. **Voice training data persistence.** First 10 posts effectively *are* the voice calibration set. `edit_delta` already captures this. Decision: also persist raw transcripts of Gate 1 conversations? Lean yes — cheap, useful for Hermes later.
5. **Series strategy.** Perplexity report suggested four recurring series (Systems Sketches, Funnel Autopsies, Agent Architecture Whiteboards, Field Notes). Adopt at launch or let series emerge organically and tag retroactively? Lean emergent — decide before first 10 posts ship.

### 8.2 Dependencies (external; affect quality not capability)

- **Brand spec revamp.** Renderer placeholder works for v1.0, but Tier 1 diagrams won't look like *the author's* diagrams until real brand-spec lands. Brand revamp is an upstream blocker for *visual brand recognition*, not functional output.
- **NotebookLM corpus expansion (Library of Alexandria v2).** Engine works on existing writing+design atoms. Cross-domain `convergence_finder` posts get dramatically richer once 3+ new domains are atomized.
- **Higgsfield account + credit budget.** Tier 3 requires both. Decision needed pre-v1.2: monthly burn cap? Hard or soft?

### 8.3 Parallel workstreams (can start today, not gating)

1. **Library of Alexandria v2 ingest.** Run prompt at `05-resources/prompts/library-of-alexandria-v2.md`. Download Tier A canon (~40 books), upload to NotebookLM, atomize via existing pipeline. 4–6 week cycle.
2. **Brand spec revamp.** Separate brainstorm + spec, owned by user. LinkedIn engine consumes output; doesn't define scope.
3. **Connection-type tagging.** As new connection atoms are written, type them (one of 8 types: `mechanism`, `analogical`, `causal`, `inverse`, `compositional`, `genealogical`, `critique`, `epistemic`, or `general`). Backfill decision deferred (see open question 3).
4. **Hermes self-learning skill ideation.** Separate brainstorm cycle when user is ready. Out of scope for this spec.

### 8.4 Out of scope (named so they don't sneak in)

- Direct LinkedIn API integration (banned per ToS).
- Multi-platform syndication (Twitter/X, Threads).
- Engagement automation (auto-comment, auto-DM) — banned per ToS.
- Cross-posting the atom graph as a public web product.
- Audience analytics beyond per-post metrics (follower growth, demographic breakdowns).

---

## 9. Generation workflow + repetition control

### 9.1 Three generation modes

| Mode | Invocation | Behavior |
|---|---|---|
| **Single (default)** | `/draft-post` | One draft, auto-picks strategy + atoms |
| **Batch** | `/draft-post --batch=N` | N drafts in one run; anti-repeat respected within batch |
| **Scan (rare)** | `/draft-post --scan` | Enumerates eligible candidates, scores them, writes top-10 |

Daily usage: single + occasional `--batch=3` to build backlog. Scan is for launch day or exploring options.

### 9.2 Anti-repeat (four layers)

1. **Atom usage cooldown.** Each atom tracks `last_used_at` + role. Can't be `primary` in two posts within 30 days. `auxiliary` role allowed sooner.
2. **Connection usage cooldown.** Each connection edge tracks `last_used_at`. Can't be spotlighted twice within 60 days. (Longer because spotlighting a connection IS the post.)
3. **Strategy diversity bias.** If last 3 posts used the same strategy, auto-picker biases away. Soft, overridable.
4. **Angle similarity check.** Embed new `angle`, compare semantic similarity to last 30 days. If > 0.85, regenerate or warn. Catches "different atoms, same idea."

### 9.3 Cooldown lifecycle (two tiers)

- **Ephemeral lock (per batch run):** atom used in draft 1 is locked through rest of batch. Released when batch finishes.
- **Persistent cooldown (across batches):** atom enters real cooldown only when draft passes Gate 1. Rejected drafts don't burn the atom — user can try again with same atom and different angle.

### 9.4 Scoring (for batch + scan modes)

```
score = +w1 * (atoms from less-used sources)
      +w2 * (typed connections > general; mechanism/analogical weighted highest)
      +w3 * (cross-domain spread by tag count)
      +w4 * (atom centrality — high connection count)
      -w5 * (atoms recently used)
      -w6 * (strategy recently used)
      -w7 * (angle similar to recent angles)
```

Weights flat in v1.0. v2.5 analytics tunes them based on what actually performs.

### 9.5 Rejection + approval logging (the Hermes training corpus)

Both files exist as JSONL:

**`01-projects/linkedin/state/rejections.jsonl`:**
```json
{
  "post_id": "...",
  "rejected_at": "...",
  "atoms_used": [...],
  "strategy": "...",
  "angle": "...",
  "draft_text": "...",
  "rejection_reason": "<free text from user, optional>",
  "rejection_signal": "killed_by_user" | "stale_7d" | "voice_lint_failed"
}
```

**`01-projects/linkedin/state/approvals.jsonl`:**
```json
{
  "post_id": "...",
  "approved_at": "...",
  "atoms_used": [...],
  "strategy": "...",
  "angle": "...",
  "draft_text": "<original>",
  "approved_text": "<after edits>",
  "edit_delta": {
    "diff": "<unified diff>",
    "magnitude": "minor | moderate | major",
    "types": [...]
  },
  "approved_visual_tier": 1 | 2 | 3,
  "tier_changed_at_gate1": bool,
  "posted_at": "...",
  "performance": {              // populated post-v2.5
    "impressions": int,
    "saves": int,
    "comments_quality": "high|mid|low",
    "recruiter_inbound": bool,
    "fetched_at": "..."
  }
}
```

### 9.6 Four-quadrant Hermes training matrix (v2.5+)

|  | Approved | Rejected |
|---|---|---|
| **Performed well** | Strong positive — replicate everything | Mixed — user's taste was wrong, audience would have liked it |
| **Performed poorly** | Weak — user liked it, audience didn't | Strong negative — both agreed |

Tracking both dimensions separately lets the engine learn *user taste* and *audience response* as distinct signals. Pre-v2.5 the performance column is empty and training relies on approval/rejection only.

### 9.7 Failure modes the user will hit

- **Pool exhausted.** All eligible atoms in cooldown. Engine surfaces: *"Closest eligible candidate reuses atom X (last used 12 days ago, cooldown is 30). Override or wait?"*
- **No typed connections.** Strategy wants `mechanism` but none exist. Falls back to `general`. Warns.
- **Convergence not found.** `convergence_finder` can't find 3 distinct domains. Returns: *"Atom corpus may be too narrow for [topic]. Widen, wait, or try different strategy."* This is also a gap signal for NotebookLM ingest prioritization.

---

## 10. Interface (slash commands + conversation)

Two slash commands total. Everything else is conversational inside Claude Code.

- **`/draft-post`** — generation entry point + state transitions (with flags)
- **`/linkedin-status`** — read-only state surface

Full flag and option reference: `01-projects/linkedin/docs/command-reference.md`.

The conversation interface handles daily flow. Slash commands exist for scripting, cron, and explicit/reproducible operations. Both interfaces write to the same state files.

---

## 11. Appendix — atom-front-matter v2.1 connection-type taxonomy

Backwards-compatible addition to `02-knowledge/`. Existing connections default to `connection_type: general`. New connections pick one of:

| Type | Meaning | Use in strategies |
|---|---|---|
| `mechanism` | Both implement the same underlying mechanism | Highest-value bridge type |
| `analogical` | Different domains, structurally similar | Cross-domain post gold |
| `causal` | One sets up or produces the other | Chain-style posts |
| `inverse` | Opposites in a meaningful way | Sharp contrast posts |
| `compositional` | One is a part of the other / they compose | Useful for cluster reveal |
| `genealogical` | One historically came from the other | Intellectual history posts |
| `critique` | One refines or pushes against the other | Idea-evolution posts |
| `epistemic` | Same thing seen from different ways of knowing | Rare, most philosophical |
| `general` | Untyped (default for legacy / unclassified) | Falls back; engine warns |

Migration: no breaking change. Atoms with no `connection_type` field are treated as `general`. Renderer edge-styling defaults to neutral for `general`.

---

*End of design spec.*
