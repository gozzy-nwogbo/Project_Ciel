# Open Brain — Product Requirements Document

**Status:** Phase 1 complete. Phase 2 complete. Phase 3 complete. Phase 4 complete.
**Last updated:** 2026-04-14
**Execution environment:** Claude Code, running inside `~/second-brain/`

---

## What We Are Building

A personal AI second brain: a single, owned, infrastructure-grade system that gives AI agents a clean memory layer to read from and write to, while giving the human a readable knowledge canvas to navigate. It synthesizes two architectures — Nate B Jones's database-backed Open Brain (Supabase + pgvector + MCP) and Cole Medin's file-based vault system (Obsidian + Claude Code + Skills) — into one coherent build.

This is not a SaaS product. It is personal infrastructure. It is built once, maintained incrementally, and compounds in value over time.

**Design philosophy:** agent surfaces, human decides, agent executes.

---

## Core Architecture

| Concern | Solution | Source |
|---|---|---|
| Agent-readable memory | Supabase + pgvector + MCP server | Nate |
| Human-readable knowledge canvas | Obsidian vault | Cole |
| Persistent context across sessions | Session hooks + memory.md + daily logs | Cole |
| Semantic retrieval | pgvector semantic search | Nate |
| Proactive intelligence | Heartbeat cron + Claude Agent SDK | Cole |
| Visual human interface | Vercel-hosted web UI over Supabase | Nate |
| Modular capabilities | Skills system in `.claude/skills/` | Cole |
| Context management | WHISK framework | Cole |
| Self-evolving knowledge base | Compiler-model LLM KB (Karpathy pattern) | Cole |
| Token efficiency | Token management principles + guardrails | Nate |

**Separation of concerns (non-negotiable):**
- Storage ≠ Intelligence ≠ Interface
- Session state ≠ Workflow state
- Conversation transcript ≠ System event log
- Raw input ≠ Compiled wiki

---

## Explicit Scope

**In scope for this build:**
- Memory foundation (soul.md, user.md, memory.md, session hooks)
- Self-evolving knowledge base (raw → compile → wiki pipeline)
- Supabase database with pgvector
- MCP server with semantic_search, list_recent, stats, write tools
- Core integrations: Gmail (read + draft), Google Calendar (read), Slack (notify), Asana (write to approved projects)
- Skills: content research, brand voice, meeting debrief, second brain PRD generator
- Heartbeat: morning digest, weekly review, relationship nudges
- Visual layer: daily digest view, job search pipeline, relationship health dashboard
- Claude Code slash commands: /context, /today, /close-day, /handoff

**Explicitly out of scope until Phase 8:**
- Neo4j graph storage
- Qdrant vector DB
- LangGraph / PydanticAI multi-agent framework
- Remotion video generation
- iMessage / SMS integration
- LinkedIn integration (use web search supplement only)
- Open Brain as public API / SDK

---

## Security Boundaries (Non-Negotiable)

These apply from Phase 1 forward. No integration may exceed these permissions without an explicit decision logged.

| Integration | Allowed | Not Allowed |
|---|---|---|
| Gmail | Read inbox, create drafts | Send emails |
| Google Calendar | Read events | Create or modify events |
| Telegram | Read Open Brain bot messages, reply in bot chat | Access other bots or groups |
| Slack | Read channels, send DMs/notifications (Phase 6) | Post publicly |
| Asana | Read/write to approved projects only | Access all workspaces |
| GitHub | Read PRs, review code | Merge, push, delete |
| Supabase | Read/write to defined tables | Schema changes, drop tables |
| File system | Read/write within vault only | Outside vault paths |

**Zero-trust defaults:**
- Every new integration starts read-only
- Write access is added deliberately after read-only is stable
- Every permission decision is logged with: action, tool, reason, timestamp
- Confidence bouncer: below 0.6 threshold → log as needs-review, never auto-file

---

## The 12 Primitives — Build Integration

The 12 primitives from the Claude Code architecture leak are distributed across phases. **Do not advance to the next phase until the current phase's primitives are stable.** The order is a dependency chain, not a suggestion.

| Primitive | Phase | What to build |
|---|---|---|
| 1. Tool registry | Phase 1 | `list_tools()` on MCP server; all capabilities as metadata before session |
| 2. Permission tiers | Phase 1 | Read-only / mutating / destructive classification per integration |
| 3. Session persistence | Phase 1 | Session JSON: messages + token usage + permission state + config; resumable |
| 4. Workflow state | Phase 2 | Explicit states for any multi-step task: planned → executing → awaiting_approval → done |
| 5. Token budget | Phase 2 | Hard per-session ceilings; pre-turn projection; structured stop before API call if exceeded |
| 6. Structured streaming | Phase 2 | Typed events for every agent action visible in Slack/UI; crash event type with reason |
| 7. System event log | Phase 3 | Separate from conversation: every context load, tool call, permission decision logged |
| — | — | **[Validate Tier 1 is stable before continuing]** |
| 8. Two-level verification | Phase 4 | Agent self-checks output; harness tests run after any change to CLAUDE.md or skill config |
| 9. Tool pool assembly | Phase 4 | Session-specific tool pool from MCP registry; not all tools always loaded |
| 10. Transcript compaction | Phase 6 | Auto-compact after N turns; preserve original goal instruction; daily log flush saves decisions |
| 11. Permission audit trail | Phase 6 | Permission state as queryable first-class object; all three handler types designed in |
| 12. Agent type system | Phase 7 | Named types with scoped tools: capture, reflect, research, execute, verify |

---

## Build Phases

### Phase 1 — Memory Foundation
**Goal:** Claude Code has persistent identity and memory that survives session resets.
**Primitives:** 1 (tool registry), 2 (permission tiers), 3 (session persistence)

**Deliverables:**
- `soul.md` — personality and behavioral principles for the agent
- `user.md` — persistent facts: name, timezone, preferences, role, goals
- `memory.md` — key decisions, lessons, facts (concise, always loaded at session start)
- Session start hook — loads soul.md + user.md + memory.md + index.md into context
- Pre-compact hook — triggers Claude Agent SDK to summarize transcript → daily log
- Session end hook — promotes key decisions from daily log → memory.md
- Supabase project initialized with pgvector enabled
- MCP server scaffolded with `list_tools()` registry (even if tools are stubs)
- Permission tier classification document for all planned integrations
- Session JSON persistence: messages + token usage + permission state

**Success criteria:**
- [x] ✅ Starting a new Claude Code session auto-loads memory files without manual instruction
- [x] ✅ Closing a session auto-writes a summary to `05-daily/`
- [ ] `list_tools()` returns capability metadata without executing anything (deferred to Phase 3)
- [x] ✅ Every planned integration is classified as read-only / mutating / destructive

---

### Phase 2 — Context Persistence
**Goal:** Sessions are resumable and the knowledge pipeline is live.
**Primitives:** 4 (workflow state), 5 (token budget), 6 (structured streaming)

**Deliverables:**
- Daily reflection cron job — processes raw daily log → extracts decisions/lessons/facts → promotes to memory.md
- Flush process — runs daily, extracts concepts + connections from daily logs → populates wiki
- `02-knowledge/index.md` — auto-maintained navigation file; updated by flush process
- Workflow state model for all multi-step tasks (heartbeat, email pipeline, review)
- Hard token ceiling per session; pre-turn projection before API call
- Structured event types for agent actions (defined schema, not ad hoc)
- Markdown auto-conversion pipeline for any document hitting the knowledge store

**Success criteria:**
- [x] ✅ `02-knowledge/index.md` updates automatically after every flush
- [ ] A session that crashes mid-task can be resumed without re-doing completed steps (deferred to Phase 3, depends on system event log)
- [x] ✅ Token budget enforcement: limits defined and visible at session start; hard enforcement in Phase 3
- [x] ✅ All document ingestion automatically converts to markdown before hitting any context window

---

### Phase 3 — Memory Search & RAG
**Goal:** Agent can retrieve relevant knowledge without full document ingestion.
**Primitives:** 7 (system event log)

**Deliverables:**
- [x] ✅ pgvector enabled in Supabase (2026-04-10)
- [x] ✅ Four tables created (captures, people, projects, ideas) with HNSW indexes (2026-04-10)
- [x] ✅ match_documents RPC function live (2026-04-10)
- [x] ✅ MCP server running with all four tools: `semantic_search`, `list_recent`, `stats`, `write` (2026-04-10)
- [x] ✅ MCP server connected to Claude Code via `.mcp.json` (2026-04-10)
- [x] ✅ Write/embed/store pipeline verified end-to-end (2026-04-10)
- [x] ✅ SQLite FTS5 index of daily logs with CLI search interface (2026-04-10)
- [x] ✅ System event log: JSONL-based, 5 categories, CLI query, integrated into summarize-session.py and flush.py (2026-04-10)
- [x] ✅ Health-check / lint process: gaps, stale data, broken links, raw-to-wiki discrepancies with weekly cron (2026-04-10)
- [x] ✅ Obsidian Web Clipper configured, flush.py extended to process raw inbox files into knowledge (2026-04-10)

**Success criteria:**
- [x] ✅ Semantic search returns relevant results by meaning, not keyword (2026-04-10)
- [x] ✅ System event log can reconstruct any agent run from audit trail alone (2026-04-10)
- [x] ✅ Health check identifies at least gaps and broken links on first run (2026-04-10)
- [x] ✅ **Tier 1 stability validated before Phase 4 begins** (2026-04-10)

---

### Phase 4 — Core Integrations
**Goal:** Agent reads from the real world. No writes until read-only is stable.
**Primitives:** 8 (two-level verification), 9 (tool pool assembly)

**Deliverables:**
- [x] ✅ Telegram capture pipeline: Open Brain bot receives messages, classifies via Claude Haiku, routes to Supabase, replies in chat (2026-04-13)
- [x] ✅ n8n workflow live: Telegram Trigger → Classify (Haiku) → Parse JSON → Route (IF) → Supabase write → Telegram reply (2026-04-13)
- [x] ✅ captures table receiving real data with auto-generated embeddings (2026-04-13)
- [x] ✅ Gmail integration: read inbox, surface relevant threads, create drafts with explicit approval, no send (2026-04-14)
  - Default filtering excludes newsletters/automated senders, `show:all` override available
  - Draft creation requires explicit user approval before firing tool
  - Job alert scoring: cross-references roles against user.md, scores high/medium/low, logs high fits to Supabase captures as job-lead
- [x] ✅ Google Calendar integration: read events, surface conflicts, check availability (2026-04-14)
  - 3 calendars discovered: primary, big back activities, Holidays in Canada
  - 4 read tools allowed (list_calendars, list_events, get_event, suggest_time)
  - 4 write tools blocked (create_event, update_event, delete_event, respond_to_event)
  - Conflict detection algorithm documented, availability checks working via suggest_time
- [x] ✅ Asana integration: read tasks, write to approved projects only (2026-04-14)
  - 1 workspace, 1 project (Open-Brain) discovered and set as approved write target
  - 18 read tools allowed, 4 write tools allowed (approved projects only), 4 tools blocked
  - Approval-first pattern: surface proposed writes, wait for user confirmation
  - Permission decisions logged to system-events.jsonl
- Slack deferred to Phase 6 (notifications only, not capture)
- Tool pool assembly: session-specific tool subset from MCP registry
- Two-level verification: agent self-check + harness test suite after config changes
- Zapier MCP bridge as fallback for any integration without direct API setup
- Two-door audit: add `retrieval_log` table to Supabase (fields: query, results_returned, useful: bool, timestamp). Tracks whether captures are actually coming back out through retrieval.
- `/review-change` slash command: reads diff of any changed file, scores against 7 dimensions (mission alignment, token hygiene, permission boundary compliance, vault path consistency, skill trigger clarity, test coverage, scope fit), returns go/no-go verdict. Concrete implementation of two-level verification (P8).

**Success criteria:**
- [x] ✅ Telegram capture pipeline classifies and routes messages to correct Supabase tables (2026-04-13)
- [x] ✅ Gmail reads work without triggering any send behavior (2026-04-14)
- [x] ✅ Tool pool assembled per session — session-type flag in CLAUDE.md Section 6 constrains tool scope per session type (capture/reflect/research/execute). Docker proxy is Phase 7 upgrade for true enforcement. (2026-04-14)
- [x] ✅ Harness test suite exists and runs after any change to CLAUDE.md or skill config — 3 tests in `.claude/tests/harness/`: destructive-approval-gate (PASSED), token-budget-stop, permission-log-coverage (PASSED). (2026-04-14)
- [x] ✅ Every integration logs permission decisions with action + reason + timestamp — universal 8-field logging standard in CLAUDE.md Section 15, verified via permission-log-coverage harness test. (2026-04-14)

---

### Phase 5 — Skills & Capabilities
**Goal:** Modular capabilities invocable on demand without bloating context.
**Primitives:** 9 (tool pool assembly, continued)

**Deliverables:**
- Migrate all 35 existing skills to `.claude/skills/` with progressive disclosure format
- New skills to build:
  - ~~Brand Voice Generator (interview workflow → tone profile)~~ **COMPLETE (2026-04-14)** — approach revised: voice profile v1.0 installed directly at `03-reflections/voice-profile.md` (built from interview + writing samples, March 2026) + writing-gateway skill built as the application layer at `.claude/skills/writing/writing-gateway/SKILL.md`. Platform rules installed at `02-knowledge/platform-rules.md`. Voice evolution log at `03-reflections/voice-evolution-log.md` with session-start hook for review scheduling.
  - Meeting Debrief (transcript → structured debrief + action items)
  - Content Research Writer (YouTube pipeline: search → NotebookLM → deliverable)
  - Second Brain PRD Generator (meta skill — generate a PRD for any new project)
  - RAG / Semantic Search skill
  - MCP2Skill bridge (Claude Code ↔ any MCP server via Python)
- Skill architecture: description loaded first (few tokens), full SKILL.md on demand
- Skills point to vault paths for reference material — not embedded inline
- Eval / test suite run on every new skill before registering in registry.md
- Add `metadata.json` alongside every SKILL.md during restructure. Minimum fields: name, category, trigger_phrases, vault_paths, primitives_required, last_eval_date. Required for tool pool assembly (P9).
- Add heavy-file-ingestion skill to registry. Converts PDFs, spreadsheets, and other binary formats into working artifacts before passing to model. Standard preprocessing step for inbox pipeline.
- Use spec contract template (`.claude/templates/spec-contract.md`) for every Phase 5 deliverable before execution. No build starts without an approved spec.

**Success criteria:**
- [ ] All 35 existing skills work from `.claude/skills/` with progressive disclosure
- [ ] New skills pass eval before registration
- [ ] No skill embeds reference material inline — all reference material lives in vault paths

---

### Phase 6 — Heartbeat & Proactive Layer
**Goal:** System acts on your behalf without prompting.
**Primitives:** 10 (transcript compaction), 11 (permission audit trail)

**Deliverables:**
- Daily heartbeat via Claude Agent SDK cron — gathers context from all APIs, reasons about priorities, sends Slack DM
- Morning digest (scheduled): top 3 actions + 1 stuck item + 1 win, under 150 words
- Weekly review (Sunday): open loops + 3 next-week actions + 1 recurring theme, under 250 words
- Relationship nudges: flag neglected contacts, suggest outreach
- Email draft automation: auto-draft replies for approval
- Transcript compaction with configurable threshold; original session goal always preserved
- Permission audit trail: permission state as queryable object, not boolean flags
- Auto-Capture ACT NOW: extend session end hook to surface ACT NOW items before closing. Write to `act_now` Supabase table (fields: item, source_session, created_at, status, due_date). Surface in morning digest.
- Self-Skill-Creator: post-session hook that identifies novel reusable patterns, drafts SKILL.md candidate, queues for human review. Does not auto-register, human approves before skill enters registry.
- Self-Improving Assistant: extend heartbeat layer with calendar patterns, habit tracking, and recurring behavior detection. Surfaces patterns without being asked.
- Composition Workflow Recipes: pre-built multi-step workflows in `04-resources/workflow-recipes/`. Start with: research + memo, daily digest, weekly review.

**Success criteria:**
- [ ] Morning digest arrives at chosen time without any manual trigger
- [ ] Compaction preserves original session goal across 100% of test runs
- [ ] Permission state can be queried and replayed for any agent run
- [ ] All proactive actions are presented for approval before execution (no autonomous sends)

---

### Phase 7 — Visual Layer
**Goal:** Human door to the same tables the agent writes to.
**Primitives:** 12 (agent type system)

**Deliverables:**
- Lightweight web app over Supabase (no sync layer — direct table reads/writes)
- Views to build (in order):
  1. Daily Digest View — top 3 actions + stuck item + win, fits phone screen
  2. Job Search Pipeline — companies, roles, contacts, status, resume versions
  3. Relationship Health Dashboard — health scores, neglected contact alerts
  4. Idea Browser
  5. Home Maintenance Tracker
- Deployed to Vercel (free tier), bookmarkable on phone
- Agent type system: capture, reflect, research, execute, verify — each with scoped tool access
- Row Level Security: PostgreSQL RLS policies on all Supabase tables before any public-facing surface goes live. Reference OB1 primitives/rls SQL patterns. Non-negotiable prerequisite for Vercel layer.

**Success criteria:**
- [ ] Daily digest view renders correctly on mobile
- [ ] Web app reads from same Supabase tables as MCP server (no sync layer)
- [ ] Agent type system: each type has explicit capability boundary, invocable by name
- [ ] Vercel deployment live at stable URL

---

### Phase 8 — Advanced Extensions
**Goal:** Cross-table reasoning, time bridging, and the compounding moat.

**Deliverables (sequenced by value):**
- Warm Introduction Engine: job posting input → scan contacts + conference notes → surface warm paths
- Interview Pattern Analysis Dashboard: patterns across interviews, resume version performance
- Cross-table reasoning workflows: connections the human would never make manually
- Time bridging automations: maintenance tracking, annual reminders, recurring pattern detection
- Open Brain as API endpoint: external applications can query the second brain
- Advanced agent frameworks if scaling: Pydantic AI, LangGraph (only if single-agent is hitting real limits)

**Success criteria:**
- [ ] At least one cross-table reasoning workflow that surfaces an insight unprompted
- [ ] Time bridging catches at least one missed recurring task in first 30 days
- [ ] API endpoint is queryable from at least one external tool

---

## Slash Commands to Build

| Command | What it does |
|---|---|
| `/context` | Load full context about current life/work state, follow backlinks |
| `/today` | Morning review: calendar + tasks + past week of daily notes → prioritized plan |
| `/close-day` | Extract action items, surface vault connections, check confidence markers |
| `/handoff` | Summarize session for continuity in next session |
| `/ghost` | Write in your voice from vault history |
| `/emerge` | Surface ideas the vault implies but never states explicitly |
| `/drift` | Compare stated intentions vs actual behavior over 30–60 days |
| `/deep` | 30-day vault scan with cross-domain pattern detection |

Build /context, /today, /close-day, and /handoff in Phase 2. The rest in Phase 5+.

---

## Token Hygiene — Built Into Every Phase

These are not optional. They apply from Phase 1 forward.

- All documents converted to markdown before entering any context window
- Index-first retrieval: agent always starts at `02-knowledge/index.md`, not raw files
- Context scoped to minimum needed per task
- Stable context cached (system prompts, tool definitions, skill descriptions)
- Model selection: Opus for complex reasoning only; Sonnet for execution; Haiku for formatting
- Fresh conversation every 10–15 turns — never mix gather-information mode with get-work-done mode
- Measure what you burn: per-call token tracking from Phase 2 onward

---

## WHISK Context Management (Operational for Every Session)

- **W (Write):** Write handoff doc at session end. Create plan before implementation.
- **I (Isolate):** Sub-agents handle research. Scout agents explore before loading into main context. Sub-agent outputs → 500-token summary into main context only.
- **S (Select):** Layer 1 = global rules (CLAUDE.md). Layer 2 = on-demand context. Layer 3 = skills (progressive). Layer 4 = live vault exploration via /prime at session start.
- **C (Compress):** /compact with custom instructions. If compaction needed twice in one session → start fresh with handoff doc. After compact: ask agent to summarize what it remembers.

---

## Open Questions (Decide Before Phase 4)

1. ~~**Always-on vs session-based:**~~ **RESOLVED.** Always-on using cloud n8n for Phase 4. Self-hosted n8n migration deferred to Phase 7 when VPS is set up for the heartbeat system. Cloud n8n accepted for now, non-sensitive captures only until self-hosted.
2. ~~**Capture channel:**~~ **RESOLVED.** Capture channel changed from Slack to Telegram. Reason: Slack n8n integration lacks test/production parity, making workflow development unworkable. Telegram bot provides identical capture UX with full n8n test mode support.
3. ~~**Notion vs Supabase for structured data:**~~ **RESOLVED.** Supabase is the only canonical store. Notion is not used in this architecture. Obsidian inbox is the mobile capture surface via iCloud sync.
4. **Heartbeat VPS:** Digital Ocean / Hostinger for 24/7 agent hosting, or rely on Zapier/cron? Affects Phase 6 infrastructure.

---

## Build Principles (Encoded Here, Not Rediscovered Later)

1. Architecture is portable, tools are not — build to principles, swap tools freely
2. If the agent builds it, the agent can maintain it — involve AI in construction, keep conversation history
3. Reduce the human's job to ONE reliable behavior: throw a thought into the capture channel
4. Treat prompts as APIs — fixed input schema, fixed output schema, JSON only, no surprises
5. Build trust mechanisms first — inbox log, confidence scores, fix button, receipts
6. Default to safe behavior when uncertain — fail gracefully, log and ask, never guess-and-pollute
7. Output should be small, frequent, and actionable — no 2,000-word reports
8. Build one core loop, attach modules later — resist agentifying everything
9. Optimize for maintainability over cleverness — the most common failure is premature complexity
10. The compounding moat is context — start logging from day one, never from day 30

---

## Extension Design Principles

Before any new skill, integration, or extension is added to the PRD, evaluate it against these four principles. A proposed capability should satisfy at least two to be worth building.

1. **Time-bridging** — Does it connect past and future, not just manage the present? Example: a recurring behavior detector that surfaces patterns from 30 days ago to inform tomorrow's priorities.

2. **Cross-category reasoning** — Does it make connections across domains the human wouldn't make manually? Example: linking a neglected contact to an open job posting at their company.

3. **Proactive surfacing** — Does it surface relevant context without being asked? Example: morning digest that pulls calendar + tasks + stale captures without a prompt.

4. **Judgment line** — Is it clear what the agent decides vs. what the human decides? Example: agent scores job fit, human decides whether to apply.

---

*This PRD is the planning artifact. No implementation begins without reference to this document.
When a phase is complete, mark its success criteria and update this file before starting the next.*
