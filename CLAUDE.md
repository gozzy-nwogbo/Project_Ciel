# CLAUDE.md — Second Brain Instruction Layer

> This file is the navigation and convention guide for this vault.
> Read this at the start of every session. Do not ingest full project
> codebases unless explicitly working on that project.

---

## 1. Vault Structure

```
second-brain/
├── CLAUDE.md                  ← you are here
├── 00-inbox/                  ← raw capture, unprocessed. Do not reference until processed.
├── 01-projects/               ← one folder per project: notes, decisions, docs only (not code)
├── 02-knowledge/              ← durable reference knowledge, indexed and wiki-linked
├── 03-skills/                 ← reusable Claude skills + registry.md (check here first)
├── 04-reflections/            ← retrospectives, voice profile, meeting debriefs
├── 05-resources/              ← templates, prompt frameworks, reusable assets
├── 06-daily/                  ← session logs and daily notes
└── 07-portfolio/              ← preserved finished work, promoted from active projects
```

**Navigation rules:**
- Always check `03-skills/registry.md` before building anything new — the skill may already exist.
- `00-inbox/` is a staging zone. Never treat it as a knowledge source.
- `02-knowledge/` is the authoritative layer. Cross-link from projects into here, not the reverse.
- If a file belongs to a running codebase, do not migrate it — create a reference note instead.

---

## 2. Code Locations (do not ingest unless explicitly working on that project)

| Project | Code Lives At |
|---------|--------------|
| n8n workflows (483 JSONs) | `~/ai_domain/n8n/workflows/` |
| open-brain MCP server | `~/second-brain/01-projects/open-brain/mcp-server/server.py` |

**MCP server:** Configured in `.mcp.json`. Starts automatically when Claude Code connects. Requires `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, and `OPENAI_API_KEY` in `.env`.

**Granola:** AI training opt-out must be enabled in Granola Settings before MCP is connected. Meeting notes are sensitive, do not pass full transcripts into context. Extract and discard pattern only.

**Rule:** If you need context from a codebase, read only the specific file needed. Do not ingest the full project tree.

---

## 3. Writing Conventions

These apply to all written output produced in this vault — cover letters, docs, notes, communications.

- **No em-dashes** in any output. Use a comma, period, or restructure the sentence.
- **No AI watermarks.** Contrastive framing ("Not as X, but as Y") is a flagged AI tell — avoid it.
- **Active voice** is the default. Passive voice only when the subject is genuinely unknown.
- **Max 1 exclamation point per 150 words.**
- **Never restate resume content in cover letters.** Default to personal projects and portfolio narrative.
- **Always say "2 years" of AI experience**, not "1.5 years."
- **Markdown format default.** Never deliver raw PDFs or binary formats as knowledge inputs — convert to markdown first.

---

## 4. Recruiting System

When working in `01-projects/recruiting/`, always reference the master guides before touching any company folder:

- `recruiting/application_guide.md` — the system for generating applications
- `recruiting/cover_letter_style_guide.md` — voice, tone, and structural rules
- `recruiting/recruitmentprojects.md` — the 13 canonical projects for adaptation

**Resume selection:** Tech Resume vs. Consulting Resume based on >50% role alignment.

**JD frames (pick one per application):**
- Builder / Enterprise / Agentic / Sales-GTM / Product-Design / Regulated

**Voice options (pick one per application):**
- Voice A: Humbled Builder
- Voice B: Pattern Seeker
- Voice C: Infrastructure Student

**Session tracking:** Maintain `.continue-here.md` at the root of any multi-session recruiting work. Check it first on every new session before doing any work.

---

## 5. Architecture Preferences

**Preferred stack pattern (3 layers):**
1. Directives — SOPs, behavioral rules, decision criteria
2. Orchestration — agent coordination, routing, decision making
3. Execution — deterministic scripts, API calls, output formatting

**Agent design principles:**
- Single-agent design by default. Only move to multi-agent when the task genuinely requires parallel execution or role separation.
- Define agent types sharply: explore, plan, verify, execute. An explore agent does not edit files. A plan agent does not run code.
- Scope every agent's context to the minimum it needs. A planning agent does not need the full codebase.
- Scope authority deliberately — always define what an agent can and cannot do before it runs.
- Build observability first. Log input tokens, output tokens, and task outcome per agent call.

**Terminal-first preference:** Terminal-based AI workflows are preferred over browser-based. Fewer dependencies, faster iteration, better auditability.

**Open Brain agent types (scoped capabilities):**
- capture — write to inbox only, no reads, no processing
- reflect — read daily logs, write to wiki, no external calls
- research — read + web search, write to raw inbox, no mutations
- execute — run approved actions, structured output only
- verify — read-only across all surfaces, no writes

---

## 5b. Coding Discipline

Four principles from Karpathy's LLM coding pitfalls observations. Apply when writing or editing code — inside this vault or outside.

**1. Think before coding.** State assumptions explicitly. If multiple interpretations exist, surface them — don't pick silently. If a simpler approach exists, say so. If something is unclear, stop and name the confusion. Ask.

**2. Simplicity first.** Minimum code that solves the problem. No features beyond what was asked. No abstractions for single-use code. No flexibility, configurability, or error handling for scenarios that weren't requested. If 200 lines could be 50, rewrite it. Test: would a senior engineer call this overcomplicated? If yes, simplify.

**3. Surgical changes.** Every changed line traces directly to the request. Don't improve adjacent code, comments, or formatting. Don't refactor what isn't broken. Match existing style even if I'd do it differently. If I notice unrelated dead code, mention it — don't delete it. Clean up only orphans my own changes created.

**4. Goal-driven execution.** Convert imperative tasks into verifiable goals. "Fix the bug" → "write a test that reproduces it, then make it pass." "Refactor X" → "ensure tests pass before and after." For multi-step tasks, state a plan with per-step verification checks. Strong success criteria let me loop independently; weak criteria ("make it work") force constant clarification.

Tradeoff note: these principles bias toward caution over speed. For trivial edits (typos, one-liners), use judgment. Not every change needs the full rigor.

---

## 6. Session Types (P9 — Tool Scope Enforcement)

Every session begins by declaring a session type. The session type determines which MCP tools are in scope. Tools outside the declared scope are not called unless the session type is explicitly upgraded to `execute` by the user.

| Session Type | Purpose | Tools In Scope | Tools Out of Scope |
|---|---|---|---|
| `capture` | Telegram bot, inbox processing, classification | Telegram (via n8n), Supabase write, n8n workflow tools | Gmail, Calendar, Asana, file system writes |
| `reflect` | Daily log review, memory promotion, handoff writing | File system (read/write within vault), Supabase read | Gmail, Calendar, Asana, n8n, Supabase write |
| `research` | Knowledge retrieval, semantic search, external lookup | Supabase read, semantic_search, web search, Gmail read, Calendar read | Gmail draft/write, Asana write, n8n workflow mutation, Supabase write |
| `execute` | Building, coding, full integration work | All tools available | None — full access |

**Hard rules:**
- At session start, read the session goal and declare: `SESSION TYPE: [type]`.
- If the task requires tools outside the declared scope, state the conflict and ask the user to upgrade to `execute` before calling the out-of-scope tool.
- Do not silently upgrade. The upgrade must be explicit in the conversation.
- If no session goal is stated, default to `research`.

**Gmail self-send exception (Phase 6.4):** `gmail_send` is permitted ONLY when `to:` address is `nwogbo.gozzy@gmail.com`. Used by the weekly review workflow. Any send to an external address remains blocked. Every send logged to `system-events.jsonl`.

**Upgrade path:** Docker proxy is the Phase 7 upgrade path for true P9 enforcement. Session-type flag is the interim behavioral constraint until VPS is live.

---

## 7. n8n Patterns

**Standard agent workflow (6 nodes):**
```
Trigger → Prepare Input → AI Agent → Chat Model → Output Parser → Format Output
```

**Standard automation workflow (6 nodes):**
```
Webhook → Validate → Execute Agent → Error Handle → Format → Respond
```

**Always use templates first** when building new workflows. Reference `01-projects/n8n/` for patterns before creating from scratch.

**Workflow catalog:** 483 workflows organized across 8 phases (foundation, business, legal, finance, insurance, real estate, logistics, tax). Native-refactored versions are canonical — original phase folders are historical.

---

## 8. Design System (Locked)

These decisions are final. Do not propose alternatives unless explicitly asked.

- **Accent color:** Teal
- **Font:** Geist
- **Secondary:** 5% amber
- **Token approach:** Semantic tokens only — no hardcoded hex values in components
- **Design pipeline:** Forensic audit → Brand interview → Synthesis → Quality check → 5-pass refinement

Design methodology atoms in `02-knowledge/concepts/`: `physical-metaphor-anchoring.md`, `lock-tokens-against-reference-drift.md`. Design book corpus in `personalplayground/notebooklm/` (8 topic domains).

---

## 9. Skill Invocation

**Before building anything:** Check `03-skills/registry.md` for an existing skill.

**If a skill exists:** Invoke it. Do not recreate.

**If no skill exists:** Build it to the standard format and register it in `registry.md` before use.

**Skill architecture (two layers):** Skills live at `.claude/skills/[category]/[skill-name]/SKILL.md` for runtime auto-discovery by Claude Code. The skill registry index lives at `03-skills/registry.md` for human-facing lookup, audit tracking, and metadata. Both are authoritative for their respective purposes. The two should not drift — every skill in `.claude/skills/` must have a corresponding row in `03-skills/registry.md`. Drift detection between filesystem and registry runs via the `registry-audit` skill (.claude/skills/meta/registry-audit/). Audit status: PASS.

**Skill categories in `03-skills/`:**
- `design/` — brand audit, website cloner, design system
- `development/` — TDD, debugging, code review, git worktrees, planning, refactoring
- `writing/` — voice matching, cover letter, content
- `productivity/` — session management, context scoping
- `n8n/` — workflow builder, expression syntax, MCP tools, node config
- `meta/` — skill creator, registry management

**Spec contracts (Phase 5+):** All deliverables from Phase 5 onward require a spec contract before execution begins. Template at `.claude/templates/spec-contract.md`. No build starts without an approved spec.

---

## 10. Token Efficiency Rules

These apply to every session:

- **Never ingest raw PDFs.** Convert to markdown before any agent touches them.
- **Never sprawl a conversation.** If a task requires more than ~15 turns, summarize and start a new session with the summary as context.
- **Cache stable context.** System prompts, skill definitions, and persona instructions do not need to be re-explained each session — reference this file.
- **Minimum viable context per task.** Only load what the current task needs. Do not preload full project trees.
- **Index before dump.** If searching a knowledge folder, check if an index or summary file exists before reading individual files.

---

## 11. Session Protocol

At the start of every Claude Code session in this vault:

1. Read this file (`CLAUDE.md`)
2. Check `06-daily/` for the most recent session log
3. If working on a project, check `01-projects/[project]/.continue-here.md`
4. Check `03-skills/registry.md` if a skill-dependent task is planned
5. Declare session type per Section 6: `SESSION TYPE: [capture | reflect | research | execute]`
6. Begin work with minimum viable context loaded

At the end of every session:

1. Run ACT NOW capture protocol (see `.claude/hooks/session-end.md`): scan for commitments, open questions, unresolved blockers. Surface candidates for approval. Never write to `act_now` without explicit approval.
2. Write or update `06-daily/[date].md` with: what was done, decisions made, open questions
3. Update `.continue-here.md` in the active project folder
4. If new durable knowledge was produced, file it in `02-knowledge/` with wiki-links

---

## 12. Memory Layer (.claude/)

On session start, load in this order:
1. `.claude/soul.md` — behavioral identity
2. `.claude/user.md` — persistent user facts  
3. `.claude/memory.md` — promoted memories from previous sessions
4. `.claude/hooks/` — session hook instructions

Skills live in `.claude/skills/` as invocable files.
`03-skills/` contains documentation and the registry — not the invocable files.

---

## 13. Output Routing

| Output type | Goes in |
|-------------|---------|
| Writing drafts | `01-projects/[project]/output/writing/` |
| Research notes | `02-knowledge/[topic]/` |
| New skills | `03-skills/[category]/` + update `registry.md` |
| Templates | `05-resources/templates/` |
| Session logs | `06-daily/[YYYY-MM-DD].md` |
| Unprocessed captures | `00-inbox/` |

---

## 14. Knowledge Pipeline

**External sources:**
Drop raw content (articles, transcripts, papers) into `00-inbox/raw/`
Run compile script → processed output lands in `02-knowledge/`

**Internal sources (session memory):**
Session-end and pre-compact hooks auto-summarize → write to `06-daily/`
Flush script runs daily → extracts concepts/connections → promotes to `02-knowledge/`

**Agent querying:**
Always start from `02-knowledge/index.md` — this is the map of the entire wiki.
Never query `00-inbox/raw/` directly — content there is uncompiled.

**Health checks:**
Run lint script periodically to surface: gaps in coverage, stale articles,
broken wiki-links, raw items not yet compiled.

---

## 15. Permission Logging (Universal)

Every MCP tool call must produce: (1) a `.claude/logs/system-events.jsonl` entry (existing behavior, unchanged) AND (2) a Supabase `permission_log` entry. Both are required. Neither replaces the other. The `reason` field is mandatory in both. An entry without a `reason` field is incomplete and must be flagged.

**system-events.jsonl format (unchanged):**

```json
{
  "timestamp": "[ISO-8601]",
  "session_id": "[current session ID]",
  "action": "[exact tool name called]",
  "integration": "[gmail / calendar / asana / telegram / supabase / n8n]",
  "permission_tier": "[read-only / mutating / destructive]",
  "inputs_summary": "[one line — what was passed]",
  "result": "[success / blocked / error]",
  "reason": "[why this call was made]"
}
```

**Supabase permission_log fields:** session_id, integration, tool, tier, action, inputs, result, reason, violation, violation_detail. Written via `log_permission.py` CLI helper at `01-projects/open-brain/scripts/log_permission.py`.

**Hard rules:**
- A log entry without a `reason` field is incomplete. Every call must state why it was made.
- `permission_tier` / `tier` must match the tool's classification in `02-knowledge/mcp-tool-audit.md`.
- Blocked tool attempts are logged with `result: blocked`.
- After any session that uses MCP tools, run `tail -5 .claude/logs/system-events.jsonl` to verify entries exist.
- Run the `permission-log-coverage` harness test (`.claude/tests/harness/permission-log-coverage.md`) after any integration change.
- Weekly: run `flag_incomplete_logs.py` to catch entries missing the `reason` field in `permission_log`.
- Permission boundaries enforced by `check_violations.py` reading from `01-projects/open-brain/config/permission-boundaries.json`.
- Session start and close hooks automatically write to permission_log. This provides bookend coverage for every session without manual logging.

---

---

## 16. Slash Commands

Commands live in `.claude/commands/` as markdown files. Type `/command-name` in Claude Code to invoke.

| Command | When to use | Writes? |
|---|---|---|
| `/close-session` | End of every session. Summary, decisions, ACT NOW, handoff doc. | `06-daily/`, Supabase `act_now` (with approval) |
| `/orient` | Start of complex sessions. Full orientation across all active tracks. | No (read-only) |
| `/today` | Morning desk review. Prioritized plan from calendar, tasks, act_now. | No (read-only) |
| `/draft-email` | Draft Gmail replies on-demand. One thread at a time, approval required. | Gmail drafts, Supabase `draft_log` |

**Rules:**
- `/close-session` never overwrites existing daily logs. Always appends.
- `/context` and `/today` are strictly read-only. They surface information, they do not act on it.
- ACT NOW writes require explicit user approval. No exceptions.

---

*Last updated: 2026-04-30*
*This is a living document. Update it when conventions change -- do not let it drift from actual practice.*
